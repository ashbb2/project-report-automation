import json
import sqlite3
from typing import Optional

from app.db import DB_PATH


MAX_CITY_RESULTS = 20


def get_states(country: str = "India") -> list[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT DISTINCT state
        FROM locations
        WHERE country = ?
        ORDER BY state ASC
        """,
        (country,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def search_cities(state: str, query: str = "", country: str = "India", limit: int = MAX_CITY_RESULTS) -> list[dict[str, object]]:
    normalized_query = query.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT city, aliases_json
        FROM locations
        WHERE country = ? AND state = ?
        ORDER BY city ASC
        """,
        (country, state),
    )
    rows = cursor.fetchall()
    conn.close()

    results: list[dict[str, object]] = []
    for city, aliases_json in rows:
        aliases = json.loads(aliases_json)
        searchable_terms = [city, *aliases]
        if normalized_query and not any(normalized_query in term.lower() for term in searchable_terms):
            continue
        results.append({"city": city, "aliases": aliases})
        if len(results) >= limit:
            break

    return results


def get_canonical_city(state: str, city_or_alias: str, country: str = "India") -> Optional[str]:
    lookup = city_or_alias.strip().lower()
    if not lookup:
        return None

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT city, aliases_json
        FROM locations
        WHERE country = ? AND state = ?
        ORDER BY city ASC
        """,
        (country, state),
    )
    rows = cursor.fetchall()
    conn.close()

    for city, aliases_json in rows:
        aliases = json.loads(aliases_json)
        if city.lower() == lookup:
            return city
        if any(alias.lower() == lookup for alias in aliases):
            return city

    return None
