"""
Fetches India macro indicators from the World Bank Open Data API.
No API key required. Results are cached for 24 hours.
API docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/898590
"""
import json
import urllib.request
from typing import List, Dict

from app.data_fetchers import cache

_BASE = "https://api.worldbank.org/v2"
_COUNTRY = "IN"

_INDICATORS = {
    "gdp_growth":       ("NY.GDP.MKTP.KD.ZG", "GDP Growth Rate (annual %)"),
    "inflation":        ("FP.CPI.TOTL.ZG",     "Inflation / CPI (annual %)"),
    "industry_pct_gdp": ("NV.IND.TOTL.ZS",     "Industry Value Added (% of GDP)"),
    "gdp_per_capita":   ("NY.GDP.PCAP.CD",      "GDP per Capita (current USD)"),
}


def _fetch(indicator_id: str) -> List[Dict]:
    cache_key = f"wb_{_COUNTRY}_{indicator_id}"
    hit = cache.get(cache_key)
    if hit is not None:
        return hit

    url = (
        f"{_BASE}/country/{_COUNTRY}/indicator/{indicator_id}"
        f"?format=json&mrv=3&per_page=5"
    )
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            payload = json.loads(resp.read())
        records = [
            {"year": r["date"], "value": round(r["value"], 2)}
            for r in (payload[1] or [])
            if r.get("value") is not None
        ]
        cache.set(cache_key, records)
        return records
    except Exception:
        return []


def _fmt(records: list, suffix: str = "") -> str:
    if not records:
        return "data unavailable"
    return "  /  ".join(f"{r['year']}: {r['value']}{suffix}" for r in records[:2])


def get_india_macro_context() -> str:
    lines = ["INDIA MACROECONOMIC INDICATORS (Source: World Bank Open Data — data.worldbank.org):"]
    for slug, (ind_id, label) in _INDICATORS.items():
        records = _fetch(ind_id)
        suffix = "%" if "pct" in slug or "growth" in slug or "inflation" in slug else " USD"
        lines.append(f"• {label}: {_fmt(records, suffix)}")
    return "\n".join(lines)
