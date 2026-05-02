import os


class Config:
    """Runtime configuration flags for report generation modes."""

    USE_STAGED_PIPELINE = os.getenv("USE_STAGED_PIPELINE", "false").lower() == "true"
    FALLBACK_TO_LEGACY = os.getenv("FALLBACK_TO_LEGACY", "true").lower() == "true"
    REQUIRE_CLIENT_REVIEW = os.getenv("REQUIRE_CLIENT_REVIEW", "true").lower() == "true"
    MAX_SOURCING_RETRIES = int(os.getenv("MAX_SOURCING_RETRIES", "2"))
    SOURCING_FALLBACK_PHRASE = "reliable public data not available"
