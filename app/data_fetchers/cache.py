import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional

_CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    ".data_cache",
)
_TTL_HOURS = 24


def _path(key: str) -> str:
    safe = hashlib.md5(key.encode()).hexdigest()
    os.makedirs(_CACHE_DIR, exist_ok=True)
    return os.path.join(_CACHE_DIR, f"{safe}.json")


def get(key: str) -> Optional[Any]:
    try:
        with open(_path(key)) as f:
            entry = json.load(f)
        if datetime.utcnow() > datetime.fromisoformat(entry["expires_at"]):
            return None
        return entry["data"]
    except Exception:
        return None


def set(key: str, data: Any) -> None:
    expires = (datetime.utcnow() + timedelta(hours=_TTL_HOURS)).isoformat()
    try:
        with open(_path(key), "w") as f:
            json.dump({"expires_at": expires, "data": data}, f)
    except Exception:
        pass  # non-fatal
