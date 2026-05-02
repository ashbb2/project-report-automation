import hashlib
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.config import Config
from app.db import (
    get_submission_execution_mode,
    set_submission_execution_mode,
    get_submission_baseline_lock,
    save_submission_baseline_lock,
    upsert_stage_checkpoint,
    add_validation_event,
    set_submission_last_failed_stage,
    get_assumptions_review,
)
from app.report_builder import build_doc, get_or_generate_section


class StageError(RuntimeError):
    pass


def _canonical_baseline(submission: Dict[str, Any]) -> Dict[str, Any]:
    """Build a stable baseline payload for lock hashing and stage consistency."""
    baseline_fields = [
        "business_idea",
        "product_service",
        "target_capacity",
        "total_investment",
        "budget",
        "debt_percentage",
        "equity_percentage",
        "loan_tenor",
        "interest_rate",
        "moratorium_period",
        "operating_days",
        "shifts_per_day",
        "hours_per_shift",
        "project_state",
        "project_country",
        "target_market",
        "target_customer",
    ]
    return {key: submission.get(key) for key in baseline_fields}


def _hash_payload(payload: Dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _question_for_missing_field(field_name: str) -> str:
    question_map = {
        "debt_percentage": "Please confirm debt percentage as a number between 0 and 100.",
        "equity_percentage": "Please confirm equity percentage as a number between 0 and 100.",
        "loan_tenor": "Please share loan tenor in years.",
        "interest_rate": "Please confirm annual interest rate percentage.",
        "selling_price": "Please confirm selling price per unit (or approve AI default explicitly).",
        "repayment_frequency": "Please select repayment frequency (monthly or quarterly).",
        "operating_days": "Please share operating days per year.",
        "production_rampup": "Please provide production ramp-up plan by year.",
        "currency": "Please confirm reporting currency code (for example INR).",
        "target_capacity": "Please provide target capacity for capacity-driven mode.",
        "total_investment": "Please provide total investment for budget-driven mode.",
    }
    return question_map.get(field_name, f"Please provide value for {field_name}.")


def _basis_and_source_for_assumption(
    field_name: str,
    value: Any,
    review_sources: Dict[str, Any],
) -> Tuple[str, List[str]]:
    source_meta = review_sources.get(field_name) if isinstance(review_sources, dict) else None
    if source_meta:
        provenance = source_meta.get("provenance") or "model_default"
        basis = {
            "client_provided": "Client Provided",
            "reliable_url": "Public Source",
            "model_default": "AI Default",
            "unable_to_source": "AI Default",
        }.get(provenance, "AI Default")
        links = [source_meta.get("source_url")] if source_meta.get("source_url") else []
        return basis, links

    if value is None or (isinstance(value, str) and not value.strip()):
        return "AI Default", []
    return "Client Provided", []


def _build_stage1_baseline_artifact(
    submission_data: Dict[str, Any],
    baseline_payload: Dict[str, Any],
    review: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    review_sources = (review or {}).get("sources", {})
    sizing_mode = submission_data.get("sizing_mode") or "not_provided"

    missing_fields = _financial_required_missing(submission_data)
    missing_questions = [
        {"field": field, "question": _question_for_missing_field(field)}
        for field in missing_fields
    ]

    tracked_assumptions = [
        ("selling_price", "currency"),
        ("interest_rate", "% p.a."),
        ("moratorium_period", "months"),
        ("operating_days", "days/year"),
        ("shifts_per_day", "shifts/day"),
        ("hours_per_shift", "hours/shift"),
        ("debt_percentage", "%"),
        ("equity_percentage", "%"),
        ("loan_tenor", "years"),
        ("total_investment", "currency"),
        ("target_capacity", "units"),
    ]

    assumptions_table = []
    for field_name, unit in tracked_assumptions:
        value = submission_data.get(field_name)
        basis, source_links = _basis_and_source_for_assumption(field_name, value, review_sources)
        assumptions_table.append(
            {
                "assumption": field_name,
                "value": value,
                "unit": unit,
                "basis": basis,
                "source_links": source_links,
            }
        )

    if sizing_mode == "capacity_driven":
        sizing_basis_statement = "Sizing is capacity-driven and depends primarily on declared target capacity."
        key_implications = [
            "Revenue build-up must reconcile with target capacity and ramp-up plan.",
            "Working-capital assumptions must match capacity-led volume assumptions.",
        ]
    elif sizing_mode == "budget_driven":
        sizing_basis_statement = "Sizing is budget-driven and depends primarily on available investment envelope."
        key_implications = [
            "Equipment and capacity assumptions must remain within budget cap.",
            "Financing schedule and debt service must reconcile with cap-based phasing.",
        ]
    else:
        sizing_basis_statement = "Sizing basis is not clearly set."
        key_implications = ["Report generation quality may degrade until sizing mode is confirmed."]

    return {
        "project_definition_summary": {
            "business_idea": baseline_payload.get("business_idea"),
            "product_service": baseline_payload.get("product_service"),
            "target_market": baseline_payload.get("target_market"),
            "target_customer": baseline_payload.get("target_customer"),
            "project_state": baseline_payload.get("project_state"),
            "project_country": baseline_payload.get("project_country"),
        },
        "mode_selection_logic": {
            "sizing_mode": sizing_mode,
            "selected_basis_field": "target_capacity" if sizing_mode == "capacity_driven" else "total_investment",
        },
        "sizing_basis_statement": sizing_basis_statement,
        "key_implications": key_implications,
        "assumptions_table": assumptions_table,
        "missing_inputs": missing_fields,
        "missing_input_questions": missing_questions,
    }


def _financial_required_missing(submission: Dict[str, Any]) -> List[str]:
    """Hard-stop list for financial computation prerequisites only."""
    required = [
        "debt_percentage",
        "equity_percentage",
        "loan_tenor",
        "interest_rate",
        "selling_price",
        "repayment_frequency",
        "operating_days",
        "production_rampup",
        "currency",
    ]

    missing: List[str] = []
    for field in required:
        value = submission.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)

    sizing_mode = submission.get("sizing_mode")
    if sizing_mode == "capacity_driven":
        if not submission.get("target_capacity"):
            missing.append("target_capacity")
    elif sizing_mode == "budget_driven":
        if not submission.get("total_investment"):
            missing.append("total_investment")

    return sorted(set(missing))


def _contains_quantitative_claims(text: str) -> bool:
    return bool(re.search(r"\b\d+(?:\.\d+)?%?\b", text or ""))


def _passes_sourcing_rule(text: str) -> Tuple[bool, str]:
    if not text:
        return False, "empty_text"

    has_link = bool(re.search(r"https?://\S+", text))
    has_fallback = Config.SOURCING_FALLBACK_PHRASE in text.lower()

    if has_link or has_fallback:
        return True, "ok"
    return False, "missing_link_or_fallback"


def _validate_financial_sourcing(submission_id: int, submission_data: Dict[str, Any], force: bool) -> str:
    """Generate financial section with bounded retries for sourcing discipline."""
    attempts = 0
    last_content = ""
    max_attempts = max(1, Config.MAX_SOURCING_RETRIES + 1)

    while attempts < max_attempts:
        attempts += 1
        content = get_or_generate_section(
            submission_id=submission_id,
            section_name="financial_feasibility",
            submission_data=submission_data,
            force=force or attempts > 1,
        )
        last_content = content

        if not _contains_quantitative_claims(content):
            return content

        passed, reason = _passes_sourcing_rule(content)
        add_validation_event(
            submission_id=submission_id,
            stage_name="financial",
            event_type="sourcing_validation",
            passed=passed,
            details={"attempt": attempts, "reason": reason},
        )
        if passed:
            return content

    # Soft-fail after bounded retries: append fallback and continue.
    suffix = (
        "\n\nSource note: Reliable public data not available for one or more quantitative "
        "claims in this section; conservative assumptions were retained."
    )
    content_with_fallback = (last_content or "") + suffix
    get_or_generate_section(
        submission_id=submission_id,
        section_name="financial_feasibility",
        submission_data=submission_data,
        force=True,
    )
    return content_with_fallback


def _build_material_number_provenance(submission_data: Dict[str, Any], review: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build provenance records for core material numbers used in financial and operating logic.
    """
    review_sources = (review or {}).get("sources", {})

    tracked_fields = [
        "selling_price",
        "interest_rate",
        "moratorium_period",
        "operating_days",
        "shifts_per_day",
        "hours_per_shift",
        "debt_percentage",
        "equity_percentage",
        "loan_tenor",
        "total_investment",
    ]

    records: List[Dict[str, Any]] = []
    for field in tracked_fields:
        value = submission_data.get(field)
        source_meta = review_sources.get(field) if isinstance(review_sources, dict) else None

        if source_meta:
            provenance = source_meta.get("provenance") or "unknown"
            source = source_meta.get("source")
            source_url = source_meta.get("source_url")
            note = source_meta.get("note")
        else:
            if value is None or (isinstance(value, str) and not value.strip()):
                provenance = "unable_to_source"
                source = "No confirmed source"
                source_url = None
                note = "No client value or review-source metadata available"
            else:
                provenance = "client_provided"
                source = "Submission payload"
                source_url = None
                note = "Derived from submission payload"

        records.append(
            {
                "field": field,
                "value": value,
                "provenance": provenance,
                "source": source,
                "source_url": source_url,
                "note": note,
            }
        )

    return records


def _build_stage2_financial_snapshot(submission_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a lightweight canonical object used for Chapter 6 consistency checks."""
    snapshot_fields = [
        "selling_price",
        "interest_rate",
        "moratorium_period",
        "debt_percentage",
        "equity_percentage",
        "loan_tenor",
        "repayment_frequency",
        "operating_days",
        "production_rampup",
        "total_investment",
        "target_capacity",
    ]
    return {field: submission_data.get(field) for field in snapshot_fields}


def _token_present(text: str, value: Any) -> bool:
    if value is None:
        return True
    token = str(value).strip()
    if not token:
        return True
    return token.lower() in (text or "").lower()


def _validate_chapter6_mapping(financial_text: str, model_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    missing_in_chapter = []
    for field_name, value in model_snapshot.items():
        if not _token_present(financial_text, value):
            missing_in_chapter.append(field_name)

    return {
        "mapped_fields": sorted(model_snapshot.keys()),
        "missing_in_chapter": sorted(missing_in_chapter),
        "match": len(missing_in_chapter) == 0,
    }


def _validate_equipment_profile_content(equipment_text: str) -> Dict[str, Any]:
    text = equipment_text or ""
    has_url = bool(re.search(r"https?://\S+", text))
    has_image_link = bool(re.search(r"https?://\S+\.(?:png|jpg|jpeg|webp|svg)", text, re.IGNORECASE))
    has_brand_hint = "brand" in text.lower() or "manufacturer" in text.lower() or "oem" in text.lower()
    has_tech_spec = "spec" in text.lower()
    has_performance = "performance" in text.lower() or "output" in text.lower()

    missing_keys = []
    if not has_url:
        missing_keys.append("oem_or_product_link")
    if not has_image_link:
        missing_keys.append("image_link")
    if not has_brand_hint:
        missing_keys.append("brand_or_manufacturer")
    if not has_tech_spec:
        missing_keys.append("technical_specifications")
    if not has_performance:
        missing_keys.append("performance_specifications")

    return {
        "has_url": has_url,
        "has_image_link": has_image_link,
        "has_brand_or_manufacturer": has_brand_hint,
        "has_technical_specs": has_tech_spec,
        "has_performance_specs": has_performance,
        "missing_keys": missing_keys,
        "valid": len(missing_keys) == 0,
    }


def _word_overlap_ratio(a: str, b: str) -> float:
    words_a = {w for w in re.findall(r"[a-zA-Z]{4,}", (a or "").lower())}
    words_b = {w for w in re.findall(r"[a-zA-Z]{4,}", (b or "").lower())}
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / max(1, min(len(words_a), len(words_b)))


def _run_lightweight_quality_checks(section_content: Dict[str, str]) -> Dict[str, Any]:
    warnings: List[str] = []

    overlap = _word_overlap_ratio(
        section_content.get("business_operating_model", ""),
        section_content.get("equipment_profiles", ""),
    )
    if overlap > 0.45:
        warnings.append("high_repetition_between_5_0_and_5_1")

    citation_sections = ["financial_feasibility", "market_assessment", "equipment_profiles"]
    for section_name in citation_sections:
        section_text = section_content.get(section_name, "")
        if _contains_quantitative_claims(section_text):
            passed, _ = _passes_sourcing_rule(section_text)
            if not passed:
                warnings.append(f"citation_missing_for_quant_claims:{section_name}")

    page_targets = {
        "executive_summary": 2,
        "introduction": 6,
        "regulatory_framework": 10,
        "market_assessment": 16,
        "business_operating_model": 23,
        "financial_feasibility": 24,
        "risk_assessment": 6,
        "caveats": 3,
    }
    # Very lightweight proxy: warn when section length is clearly too short for target pages.
    for section_name, pages in page_targets.items():
        text = section_content.get(section_name, "")
        approx_words = len(re.findall(r"\b\w+\b", text))
        if approx_words < pages * 80:
            warnings.append(f"page_intent_low_content:{section_name}")

    return {
        "passed": len(warnings) == 0,
        "warnings": warnings,
        "overlap_ratio_business_vs_equipment": round(overlap, 4),
    }


def _stage_start(submission_id: int, stage_name: str, baseline_hash: str) -> None:
    upsert_stage_checkpoint(
        submission_id=submission_id,
        stage_name=stage_name,
        baseline_hash=baseline_hash,
        status="in_progress",
        error_message=None,
    )


def _stage_complete(submission_id: int, stage_name: str, baseline_hash: str, output_hash: str = "", output_size: int = 0) -> None:
    upsert_stage_checkpoint(
        submission_id=submission_id,
        stage_name=stage_name,
        baseline_hash=baseline_hash,
        status="complete",
        error_message=None,
        output_hash=output_hash,
        output_size=output_size,
    )


def _stage_fail(submission_id: int, stage_name: str, baseline_hash: str, error_message: str) -> None:
    upsert_stage_checkpoint(
        submission_id=submission_id,
        stage_name=stage_name,
        baseline_hash=baseline_hash,
        status="failed",
        error_message=error_message,
    )
    set_submission_last_failed_stage(submission_id, stage_name)


def run_staged_pipeline(submission_id: int, submission_data: Dict[str, Any], force: bool = False) -> bytes:
    """Run staged generation with baseline locking and checkpoint instrumentation."""
    mode = get_submission_execution_mode(submission_id)
    if mode and mode != "staged":
        raise StageError("Submission execution mode mismatch: expected staged")
    set_submission_execution_mode(submission_id, "staged")

    baseline_payload = _canonical_baseline(submission_data)
    baseline_hash = _hash_payload(baseline_payload)
    review: Optional[Dict[str, Any]] = None
    submission_for_generation = dict(submission_data)

    if Config.REQUIRE_CLIENT_REVIEW:
        review = get_assumptions_review(submission_id)
        if not review or not review.get("approved"):
            raise StageError("Client review is required before final report generation")

        reviewed_baseline = review.get("baseline") or {}
        reviewed_hash = review.get("baseline_hash")
        if reviewed_baseline:
            baseline_payload = reviewed_baseline
            baseline_hash = reviewed_hash or _hash_payload(reviewed_baseline)
            submission_for_generation.update(reviewed_baseline)

    # Stage 1: baseline lock
    stage_name = "baseline"
    try:
        _stage_start(submission_id, stage_name, baseline_hash)
        existing_lock = get_submission_baseline_lock(submission_id)
        if existing_lock and existing_lock["baseline_hash"] != baseline_hash:
            raise StageError("Baseline immutability violation: locked baseline differs from current payload")

        if not existing_lock:
            save_submission_baseline_lock(submission_id, baseline_payload, baseline_hash)

        add_validation_event(
            submission_id=submission_id,
            stage_name=stage_name,
            event_type="baseline_lock",
            passed=True,
            details={"locked_at": datetime.utcnow().isoformat()},
        )
        baseline_artifact = _build_stage1_baseline_artifact(submission_for_generation, baseline_payload, review)
        add_validation_event(
            submission_id=submission_id,
            stage_name=stage_name,
            event_type="baseline_artifact",
            passed=len(baseline_artifact.get("missing_inputs", [])) == 0,
            details=baseline_artifact,
        )
        _stage_complete(submission_id, stage_name, baseline_hash)
    except Exception as exc:
        _stage_fail(submission_id, stage_name, baseline_hash, str(exc))
        raise

    # Stage 2: financial prerequisites + sourcing
    stage_name = "financial"
    try:
        _stage_start(submission_id, stage_name, baseline_hash)
        missing = _financial_required_missing(submission_for_generation)
        missing_questions = [_question_for_missing_field(field) for field in missing]
        add_validation_event(
            submission_id=submission_id,
            stage_name=stage_name,
            event_type="financial_input_readiness",
            passed=len(missing) == 0,
            details={
                "missing": missing,
                "questions": missing_questions,
            },
        )
        if missing:
            add_validation_event(
                submission_id=submission_id,
                stage_name=stage_name,
                event_type="required_financial_inputs",
                passed=False,
                details={"missing": missing, "questions": missing_questions},
            )
            raise StageError(f"Missing required financial inputs: {', '.join(missing)}")

        financial_content = _validate_financial_sourcing(submission_id, submission_for_generation, force=force)
        stage2_snapshot = _build_stage2_financial_snapshot(submission_for_generation)
        add_validation_event(
            submission_id=submission_id,
            stage_name=stage_name,
            event_type="financial_model_snapshot",
            passed=True,
            details={"snapshot": stage2_snapshot},
        )

        chapter6_mapping = _validate_chapter6_mapping(financial_content, stage2_snapshot)
        add_validation_event(
            submission_id=submission_id,
            stage_name=stage_name,
            event_type="chapter6_model_mapping",
            passed=chapter6_mapping["match"],
            details=chapter6_mapping,
        )

        # Capture a compact provenance snapshot for material financial/operating numbers.
        provenance_records = _build_material_number_provenance(submission_for_generation, review if Config.REQUIRE_CLIENT_REVIEW else None)
        unable_to_source_count = sum(1 for record in provenance_records if record.get("provenance") == "unable_to_source")
        add_validation_event(
            submission_id=submission_id,
            stage_name=stage_name,
            event_type="material_number_provenance",
            passed=unable_to_source_count == 0,
            details={
                "unable_to_source_count": unable_to_source_count,
                "records": provenance_records,
            },
        )

        add_validation_event(
            submission_id=submission_id,
            stage_name=stage_name,
            event_type="required_financial_inputs",
            passed=True,
            details={"missing": []},
        )
        _stage_complete(submission_id, stage_name, baseline_hash)
    except Exception as exc:
        _stage_fail(submission_id, stage_name, baseline_hash, str(exc))
        raise

    # Stage 3 + 4: chapter generation and final assembly
    stage_name = "assembly"
    try:
        _stage_start(submission_id, stage_name, baseline_hash)

        section_names = [
            "executive_summary",
            "introduction",
            "regulatory_framework",
            "market_assessment",
            "business_operating_model",
            "equipment_profiles",
            "financial_feasibility",
            "risk_assessment",
            "caveats",
        ]
        section_content = {
            section_name: get_or_generate_section(submission_id, section_name, submission_for_generation, force=False)
            for section_name in section_names
        }

        equipment_validation = _validate_equipment_profile_content(section_content.get("equipment_profiles", ""))
        add_validation_event(
            submission_id=submission_id,
            stage_name=stage_name,
            event_type="equipment_profile_validation",
            passed=equipment_validation["valid"],
            details=equipment_validation,
        )

        quality_checks = _run_lightweight_quality_checks(section_content)
        add_validation_event(
            submission_id=submission_id,
            stage_name=stage_name,
            event_type="assembly_quality_checks",
            passed=quality_checks["passed"],
            details=quality_checks,
        )

        doc_bytes = build_doc(submission_for_generation, submission_id, force=force)
        output_hash = hashlib.sha256(doc_bytes).hexdigest()
        _stage_complete(
            submission_id,
            stage_name,
            baseline_hash,
            output_hash=output_hash,
            output_size=len(doc_bytes),
        )
        set_submission_last_failed_stage(submission_id, None)
        return doc_bytes
    except Exception as exc:
        _stage_fail(submission_id, stage_name, baseline_hash, str(exc))
        raise
