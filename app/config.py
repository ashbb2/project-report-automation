import os
import json


class Config:
    """Runtime configuration flags for report generation modes."""

    USE_STAGED_PIPELINE = os.getenv("USE_STAGED_PIPELINE", "false").lower() == "true"
    FALLBACK_TO_LEGACY = os.getenv("FALLBACK_TO_LEGACY", "true").lower() == "true"
    REQUIRE_CLIENT_REVIEW = os.getenv("REQUIRE_CLIENT_REVIEW", "true").lower() == "true"
    MAX_SOURCING_RETRIES = int(os.getenv("MAX_SOURCING_RETRIES", "2"))
    SOURCING_FALLBACK_PHRASE = "reliable public data not available"

    SECTION_GEN_POLICY_ENABLED = os.getenv("SECTION_GEN_POLICY_ENABLED", "true").lower() == "true"
    SECTION_GEN_DEFAULT_MODE = os.getenv("SECTION_GEN_DEFAULT_MODE", "plain").lower()
    MAX_WEB_TOOL_TURNS = int(os.getenv("MAX_WEB_TOOL_TURNS", "3"))

    _DEFAULT_SECTION_POLICY = {
        "market_assessment": "web",
        "regulatory_framework": "web",
        "equipment_profiles": "web",
        "executive_summary": "plain",
        "introduction": "plain",
        "caveats": "plain",
        "appendices": "plain",
        "business_operating_model": "plain",
        "financial_feasibility": "web",
        "risk_assessment": "plain",
    }

    _raw_policy = os.getenv("SECTION_GEN_POLICY_JSON", "")
    if _raw_policy.strip():
        try:
            _parsed_policy = json.loads(_raw_policy)
            if isinstance(_parsed_policy, dict):
                _DEFAULT_SECTION_POLICY.update({k: str(v).lower() for k, v in _parsed_policy.items()})
        except Exception:
            pass

    @classmethod
    def resolve_section_mode(cls, section_name: str) -> str:
        """Resolve generation mode for a section. Returns 'plain' or 'web'."""
        if not cls.SECTION_GEN_POLICY_ENABLED:
            return "web"

        mode = cls._DEFAULT_SECTION_POLICY.get(section_name, cls.SECTION_GEN_DEFAULT_MODE)
        return mode if mode in {"plain", "web"} else "plain"
