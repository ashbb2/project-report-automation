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
    ENABLE_CLAUDE_WEB_SEARCH = os.getenv("ENABLE_CLAUDE_WEB_SEARCH", "false").lower() == "true"
    MAX_WEB_TOOL_TURNS = int(os.getenv("MAX_WEB_TOOL_TURNS", "2"))
    PLAIN_SECTION_MAX_TOKENS = int(os.getenv("PLAIN_SECTION_MAX_TOKENS", "1200"))
    WEB_SECTION_MAX_TOKENS = int(os.getenv("WEB_SECTION_MAX_TOKENS", "1500"))
    CLAUDE_RATE_LIMIT_RETRIES = int(os.getenv("CLAUDE_RATE_LIMIT_RETRIES", "4"))
    CLAUDE_RATE_LIMIT_BASE_SLEEP_SEC = float(os.getenv("CLAUDE_RATE_LIMIT_BASE_SLEEP_SEC", "2.0"))
    GENERATION_ROUND_COOLDOWN_SEC = float(os.getenv("GENERATION_ROUND_COOLDOWN_SEC", "90.0"))
    REPORT_LOCK_STALE_SECONDS = int(os.getenv("REPORT_LOCK_STALE_SECONDS", "1200"))

    _DEFAULT_SECTION_POLICY = {
        "market_assessment": "web",
        "regulatory_framework": "web",
        "equipment_profiles": "plain",
        "executive_summary": "plain",
        "introduction": "plain",
        "caveats": "plain",
        "appendices": "plain",
        "business_operating_model": "plain",
        "financial_feasibility": "plain",
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
