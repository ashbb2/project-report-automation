"""
Data fetcher orchestrator.

Call fetch_context_for_section(section_name, submission) to get a pre-built
reference context string ready to inject into the {rag_context} prompt field.

Only sections that genuinely benefit from external data get populated context;
others return a no-op string so existing prompts continue to work unchanged.
"""
from typing import Dict, Any, Optional

from app.data_fetchers.benchmarks import classify_industry, get_industry_benchmark_context
from app.data_fetchers.world_bank import get_india_macro_context
from app.data_fetchers.rbi_rates import get_rbi_rates_context

# Sections that have {rag_context} in their prompt templates.
_RAG_SECTIONS = {
    "market_assessment",
    "financial_feasibility",
    "regulatory_framework",
    "risk_assessment",
}

_NO_CONTEXT = "No additional reference data available for this section."


def fetch_context_for_section(
    section_name: str,
    submission: Dict[str, Any],
) -> str:
    """
    Return a formatted reference context block for the given section.

    The returned string is injected into the {rag_context} placeholder in
    the section's prompt template. If the section has no specific context,
    a neutral fallback string is returned.

    Fetch failures (network timeouts, bad API responses) are handled silently
    — the section will still generate using Claude's training knowledge.
    """
    if section_name not in _RAG_SECTIONS:
        return _NO_CONTEXT

    industry_key = classify_industry(submission.get("business_idea", ""))
    industry_context = get_industry_benchmark_context(industry_key)

    if section_name == "market_assessment":
        macro = _safe_fetch(get_india_macro_context)
        return _wrap(f"{macro}\n\n{industry_context}")

    if section_name == "financial_feasibility":
        rbi = _safe_fetch(get_rbi_rates_context)
        return _wrap(f"{rbi}\n\n{industry_context}")

    if section_name == "regulatory_framework":
        return _wrap(industry_context)

    if section_name == "risk_assessment":
        macro = _safe_fetch(get_india_macro_context)
        return _wrap(f"{macro}\n\n{industry_context}")

    return _NO_CONTEXT


def _safe_fetch(fn) -> str:
    try:
        return fn()
    except Exception:
        return "(data fetch failed — use industry knowledge instead)"


def _wrap(content: str) -> str:
    divider = "-" * 60
    return (
        f"{divider}\n"
        f"REFERENCE DATA (grounded — cite sources shown where used):\n"
        f"{divider}\n"
        f"{content}\n"
        f"{divider}"
    )
