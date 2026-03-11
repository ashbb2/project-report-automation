from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from jinja2 import Environment, FileSystemLoader
import os
import json
from io import BytesIO
from typing import Optional
from app.models import SubmissionCreate, SubmissionResponse, SubmissionResponseWithValidation, ValidationSummary
from app.db import init_db, save_submission, get_submission
from app.location_service import get_states, search_cities
from app.report_builder import build_doc

app = FastAPI()

# Initialize database on startup
init_db()

# Set up Jinja2 templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_dir = os.path.join(BASE_DIR, "app", "templates")
env = Environment(loader=FileSystemLoader(templates_dir))
HSN_SAC_FILE_PATH = os.path.join(BASE_DIR, "HSN_SAC.json")
_HSN_CATALOG_CACHE: Optional[list[dict]] = None


@app.get("/", response_class=HTMLResponse)
async def get_form():
    template = env.get_template("form.html")
    google_maps_api_key = (
        os.getenv("VITE_GOOGLE_MAPS_API_KEY")
        or os.getenv("GOOGLE_MAPS_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or ""
    )
    return template.render(google_maps_api_key=google_maps_api_key)


@app.get("/api/locations/states")
async def get_location_states(country: str = "India"):
    if country != "India":
        raise HTTPException(status_code=400, detail="Only India is supported at the moment")
    return {"country": country, "states": get_states(country)}


@app.get("/api/locations/cities")
async def get_location_cities(country: str = "India", state: str = "", query: str = ""):
    if country != "India":
        raise HTTPException(status_code=400, detail="Only India is supported at the moment")
    if not state.strip():
        raise HTTPException(status_code=400, detail="state is required")
    return {
        "country": country,
        "state": state,
        "results": search_cities(state=state.strip(), query=query, country=country)
    }


def _normalize_tax_code_item(
    item: dict,
    *,
    code_keys: tuple[str, ...],
    description_keys: tuple[str, ...],
    tax_code_type: str,
    selection_type: str,
    family_label: str,
) -> Optional[dict]:
    raw_code = ""
    for key in code_keys:
        value = item.get(key)
        if value:
            raw_code = str(value).strip()
            break

    code = "".join(ch for ch in raw_code if ch.isdigit())
    if len(code) < 4:
        return None

    raw_description = ""
    for key in description_keys:
        value = item.get(key)
        if value:
            raw_description = value
            break

    description = str(raw_description).strip() or f"HSN {code}"

    family_code = code[:4]
    family_name = description if len(code) == 4 else f"{family_label} {family_code}"

    return {
        "hsnCode": code,
        "description": description,
        "familyCode": family_code,
        "familyName": family_name,
        "taxCodeType": tax_code_type,
        "selectionType": selection_type,
        "familyLabel": family_label,
    }


def _load_hsn_catalog() -> list[dict]:
    global _HSN_CATALOG_CACHE
    if _HSN_CATALOG_CACHE is not None:
        return _HSN_CATALOG_CACHE

    try:
        with open(HSN_SAC_FILE_PATH, "r", encoding="utf-8") as source:
            payload = json.load(source)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="HSN_SAC.json not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="HSN_SAC.json is not valid JSON")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load HSN_SAC.json: {exc}")

    normalized_results: list[dict] = []
    seen_codes: set[str] = set()

    catalog_configs = [
        {
            "rows": payload.get("HSN_MSTR") if isinstance(payload, dict) else [],
            "code_keys": ("hsnCode", "hsn_code", "code", "HSN_CD"),
            "description_keys": (
                "description",
                "itemDescription",
                "title",
                "productDescription",
                "name",
                "HSN_Description",
            ),
            "tax_code_type": "HSN",
            "selection_type": "product",
            "family_label": "Chapter",
        },
        {
            "rows": payload.get("SAC_MSTR") if isinstance(payload, dict) else [],
            "code_keys": ("sacCode", "sac_code", "code", "SAC_CD"),
            "description_keys": (
                "description",
                "itemDescription",
                "title",
                "serviceDescription",
                "name",
                "SAC_Description",
            ),
            "tax_code_type": "SAC",
            "selection_type": "service",
            "family_label": "Group",
        },
    ]

    for catalog_config in catalog_configs:
        rows = catalog_config["rows"]
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            normalized = _normalize_tax_code_item(
                row,
                code_keys=catalog_config["code_keys"],
                description_keys=catalog_config["description_keys"],
                tax_code_type=catalog_config["tax_code_type"],
                selection_type=catalog_config["selection_type"],
                family_label=catalog_config["family_label"],
            )
            if not normalized:
                continue
            code_key = f"{normalized['taxCodeType']}::{normalized['hsnCode']}"
            if code_key in seen_codes:
                continue
            seen_codes.add(code_key)
            normalized_results.append(normalized)

    _HSN_CATALOG_CACHE = normalized_results
    return _HSN_CATALOG_CACHE


@app.get("/api/hsn/catalog")
async def get_hsn_catalog():
    return {"results": _load_hsn_catalog()}


def validate_critical_inputs(submission: SubmissionCreate) -> ValidationSummary:
    """
    Validate critical vs optional inputs per Policy C.
    Returns summary of missing critical and optional fields.
    """
    critical_missing = []
    optional_missing = []
    assumptions_used = []
    
    # Check sizing mode specific requirements
    if submission.sizing_mode.value == "capacity_driven" and not submission.target_capacity:
        critical_missing.append("target_capacity (required for capacity-driven mode)")
    if submission.sizing_mode.value == "budget_driven" and not submission.total_investment:
        critical_missing.append("total_investment (required for budget-driven mode)")
    
    # Check optional fields
    if not submission.product_mix:
        optional_missing.append("product_mix")
        assumptions_used.append("Single product line assumed")
    
    if not submission.utilities_consumption:
        optional_missing.append("utilities_consumption")
        assumptions_used.append("Industry standard utility consumption rates will be applied")
    
    if not submission.moratorium_period:
        optional_missing.append("moratorium_period")
        assumptions_used.append("No moratorium period assumed")
    
    if not submission.preferred_manufacturer_geography:
        optional_missing.append("preferred_manufacturer_geography")
    
    if not submission.brand_preferences:
        optional_missing.append("brand_preferences")
    
    if not submission.technology_exclusions:
        optional_missing.append("technology_exclusions")
    
    if not submission.promoter_background:
        optional_missing.append("promoter_background")
    
    if not submission.start_date:
        optional_missing.append("start_date")
    
    if not submission.target_launch_date:
        optional_missing.append("target_launch_date")
    
    return ValidationSummary(
        critical_missing=critical_missing,
        optional_missing=optional_missing,
        assumptions_used=assumptions_used
    )


@app.post("/api/submit", response_model=SubmissionResponseWithValidation)
async def submit_form(submission: SubmissionCreate):
    """
    Accept form submission, validate with Pydantic, save to database, and return ID.
    Implements Policy C: strict validation for critical fields, permissive for optional.
    """
    # Validate inputs per Policy C
    validation_summary = validate_critical_inputs(submission)
    
    # Policy C: Block submission if critical fields are missing
    if validation_summary.critical_missing:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Critical fields missing",
                "critical_missing": validation_summary.critical_missing
            }
        )
    
    # Convert submission to dict and save to database
    payload = submission.model_dump()
    submission_id = save_submission(payload)
    
    # Return the submission with ID and validation summary
    return SubmissionResponseWithValidation(
        id=str(submission_id),
        validation_summary=validation_summary,
        **payload
    )


@app.get("/api/submission/{submission_id}", response_model=SubmissionResponse)
async def get_submission_by_id(submission_id: int):
    """
    Retrieve a stored submission by ID.
    """
    submission = get_submission(submission_id)
    
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return SubmissionResponse(**submission)


@app.get("/api/report/{submission_id}")
@app.post("/api/report/{submission_id}")
async def generate_report(submission_id: int, force: bool = False):
    """
    Generate a Word document report for a submission.
    
    Args:
        submission_id: The ID of the submission
        force: If True, regenerate all sections even if cached (default: False)
    """
    # Retrieve submission from database
    submission = get_submission(submission_id)
    
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Remove 'id' and 'created_at' from submission for report generation
    submission_data = {k: v for k, v in submission.items() if k not in ['id', 'created_at']}
    
    # Generate Word document with AI content and caching
    doc_bytes = build_doc(submission_data, submission_id, force)
    
    # Return as streaming response (downloadable file)
    return StreamingResponse(
        iter([doc_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=report_{submission_id}.docx"}
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}
