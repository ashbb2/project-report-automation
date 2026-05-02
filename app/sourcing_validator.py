import re
from typing import Tuple


def has_quantitative_claims(text: str) -> bool:
    return bool(re.search(r"\b\d+(?:\.\d+)?%?\b", text or ""))


def validate_sourcing_text(text: str, fallback_phrase: str) -> Tuple[bool, str]:
    if not text:
        return False, "empty_text"

    has_link = bool(re.search(r"https?://\S+", text))
    has_fallback = fallback_phrase.lower() in text.lower()

    if has_link or has_fallback:
        return True, "ok"
    return False, "missing_link_or_fallback"
