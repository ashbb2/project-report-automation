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
    GENERATION_ROUND_COOLDOWN_SEC = float(os.getenv("GENERATION_ROUND_COOLDOWN_SEC", "20.0"))
    REPORT_LOCK_STALE_SECONDS = int(os.getenv("REPORT_LOCK_STALE_SECONDS", "1200"))
    # How many report sections to generate at the same time.
    # 3 is the safe default — enough to be ~3x faster than sequential without
    # hammering the Anthropic TPM (tokens-per-minute) limit.
    # Raise to 4-5 only if you have a higher-tier API plan.
    PARALLEL_SECTION_WORKERS = int(os.getenv("PARALLEL_SECTION_WORKERS", "3"))

    # Maps section names to the model that should generate them.
    # Format: "provider:model-name"  — "claude" means use the default Claude model.
    # GitHub Models are free (within rate limits) and require a GITHUB_TOKEN env var.
    # Override any entry via env var: e.g. MODEL_caveats=claude to force Claude for caveats.
    # GitHub Models API docs: https://docs.github.com/en/github-models
    _DEFAULT_SECTION_MODEL_MAP = {
        "caveats":           "github:Phi-4",
        "appendices":        "github:Phi-4",
        "equipment_profiles":"github:Meta-Llama-3.3-70B-Instruct",
        # All other sections default to Claude (highest quality where it matters most)
    }

    # Allow per-section env var overrides: MODEL_<section_name>=<provider:model>
    _SECTION_MODEL_MAP: dict = {}
    for _sec in list(_DEFAULT_SECTION_MODEL_MAP.keys()):
        _env_val = os.getenv(f"MODEL_{_sec}", "").strip()
        _SECTION_MODEL_MAP[_sec] = _env_val if _env_val else _DEFAULT_SECTION_MODEL_MAP[_sec]

    @classmethod
    def resolve_section_model(cls, section_name: str) -> str:
        """Return 'claude' or 'github:ModelName' for the given section."""
        return cls._SECTION_MODEL_MAP.get(section_name, "claude")

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
