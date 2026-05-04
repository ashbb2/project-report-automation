import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from app.location_seed import INDIA_LOCATION_SEED

# Database path — can be overridden via DATABASE_PATH env var (used in Modal)
DB_PATH = os.environ.get("DATABASE_PATH") or os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.db")


def init_db():
    """Initialize database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS report_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            section_name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (submission_id) REFERENCES submissions(id),
            UNIQUE(submission_id, section_name)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS baseline_locks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL UNIQUE,
            baseline_json TEXT NOT NULL,
            baseline_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (submission_id) REFERENCES submissions(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stage_checkpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            stage_name TEXT NOT NULL,
            baseline_hash TEXT NOT NULL,
            status TEXT NOT NULL,
            attempt_count INTEGER NOT NULL DEFAULT 0,
            error_message TEXT,
            output_hash TEXT,
            output_size INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (submission_id) REFERENCES submissions(id),
            UNIQUE(submission_id, stage_name)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS validation_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            stage_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            passed INTEGER NOT NULL,
            details_json TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (submission_id) REFERENCES submissions(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assumptions_review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL UNIQUE,
            ai_defaults_json TEXT NOT NULL,
            sources_json TEXT NOT NULL,
            client_overrides_json TEXT,
            approved INTEGER NOT NULL DEFAULT 0,
            notes TEXT,
            baseline_json TEXT,
            baseline_hash TEXT,
            approved_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (submission_id) REFERENCES submissions(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generated_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'pending',
            doc_bytes BLOB,
            error_message TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (submission_id) REFERENCES submissions(id)
        )
    """)

    cursor.execute("PRAGMA table_info(submissions)")
    submission_columns = [row[1] for row in cursor.fetchall()]
    if "execution_mode" not in submission_columns:
        cursor.execute("ALTER TABLE submissions ADD COLUMN execution_mode TEXT")
    if "last_failed_stage" not in submission_columns:
        cursor.execute("ALTER TABLE submissions ADD COLUMN last_failed_stage TEXT")

    cursor.execute("PRAGMA table_info(generated_reports)")
    report_columns = [row[1] for row in cursor.fetchall()]
    if "sections_done" not in report_columns:
        cursor.execute("ALTER TABLE generated_reports ADD COLUMN sections_done INTEGER DEFAULT 0")
    if "sections_total" not in report_columns:
        cursor.execute("ALTER TABLE generated_reports ADD COLUMN sections_total INTEGER DEFAULT 0")
    if "current_section" not in report_columns:
        cursor.execute("ALTER TABLE generated_reports ADD COLUMN current_section TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL,
            state TEXT NOT NULL,
            city TEXT NOT NULL,
            aliases_json TEXT NOT NULL,
            UNIQUE(country, state, city)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM locations")
    location_count = cursor.fetchone()[0]
    if location_count == 0:
        for state, cities in INDIA_LOCATION_SEED.items():
            for city, aliases in cities.items():
                cursor.execute(
                    """
                    INSERT INTO locations (country, state, city, aliases_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("India", state, city, json.dumps(aliases))
                )
    
    conn.commit()
    conn.close()


def save_submission(payload: Dict[str, Any]) -> int:
    """
    Save submission to database and return the submission ID.
    
    Args:
        payload: Dictionary containing submission data
        
    Returns:
        The submission ID
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    created_at = datetime.utcnow().isoformat()
    # Convert date objects to ISO format strings for JSON serialization
    payload_dict = {}
    for key, value in payload.items():
        if hasattr(value, 'isoformat'):  # Handle date/datetime objects
            payload_dict[key] = value.isoformat()
        else:
            payload_dict[key] = value
    
    payload_json = json.dumps(payload_dict)
    
    cursor.execute(
        "INSERT INTO submissions (created_at, payload_json) VALUES (?, ?)",
        (created_at, payload_json)
    )
    
    submission_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return submission_id


def get_submission(submission_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve submission from database by ID.
    
    Args:
        submission_id: The submission ID
        
    Returns:
        Dictionary with submission data or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, created_at, payload_json FROM submissions WHERE id = ?",
        (submission_id,)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    submission_id, created_at, payload_json = row
    payload = json.loads(payload_json)
    
    return {
        "id": str(submission_id),  # Convert to string
        "created_at": created_at,
        **payload
    }


def update_submission_fields(submission_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update specific keys in the stored payload_json for a submission.

    Args:
        submission_id: The submission ID
        updates: Dictionary of keys/values to merge into payload_json

    Returns:
        Updated submission payload with id/created_at, or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT created_at, payload_json FROM submissions WHERE id = ?",
        (submission_id,)
    )
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return None

    created_at, payload_json = row
    payload = json.loads(payload_json)
    payload.update(updates)

    cursor.execute(
        "UPDATE submissions SET payload_json = ? WHERE id = ?",
        (json.dumps(payload), submission_id)
    )

    conn.commit()
    conn.close()

    return {
        "id": str(submission_id),
        "created_at": created_at,
        **payload,
    }


def get_cached_section(submission_id: int, section_name: str) -> Optional[str]:
    """
    Retrieve cached section content from database.
    
    Args:
        submission_id: The submission ID
        section_name: Name of the section (e.g., 'executive_summary', 'market_assessment')
        
    Returns:
        Section content string or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT content FROM report_sections WHERE submission_id = ? AND section_name = ?",
        (submission_id, section_name)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    return row[0] if row else None


def save_section(submission_id: int, section_name: str, content: str) -> None:
    """
    Save or update a report section in the database.
    
    Args:
        submission_id: The submission ID
        section_name: Name of the section
        content: Generated content for the section
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    created_at = datetime.utcnow().isoformat()
    
    cursor.execute(
        """
        INSERT INTO report_sections (submission_id, section_name, content, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(submission_id, section_name) 
        DO UPDATE SET content = excluded.content, created_at = excluded.created_at
        """,
        (submission_id, section_name, content, created_at)
    )
    
    conn.commit()
    conn.close()


def get_submission_baseline_lock(submission_id: int) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT baseline_json, baseline_hash, created_at FROM baseline_locks WHERE submission_id = ?",
        (submission_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    baseline_json, baseline_hash, created_at = row
    return {
        "baseline": json.loads(baseline_json),
        "baseline_hash": baseline_hash,
        "created_at": created_at,
    }


def save_submission_baseline_lock(submission_id: int, baseline: Dict[str, Any], baseline_hash: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    cursor.execute(
        """
        INSERT INTO baseline_locks (submission_id, baseline_json, baseline_hash, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(submission_id)
        DO UPDATE SET
            baseline_json = excluded.baseline_json,
            baseline_hash = excluded.baseline_hash,
            created_at = excluded.created_at
        """,
        (submission_id, json.dumps(baseline, default=str), baseline_hash, created_at),
    )
    conn.commit()
    conn.close()


def upsert_stage_checkpoint(
    submission_id: int,
    stage_name: str,
    baseline_hash: str,
    status: str,
    error_message: Optional[str] = None,
    output_hash: str = "",
    output_size: int = 0,
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()

    cursor.execute(
        """
        INSERT INTO stage_checkpoints (
            submission_id, stage_name, baseline_hash, status, attempt_count,
            error_message, output_hash, output_size, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
        ON CONFLICT(submission_id, stage_name)
        DO UPDATE SET
            baseline_hash = excluded.baseline_hash,
            status = excluded.status,
            attempt_count = stage_checkpoints.attempt_count + 1,
            error_message = excluded.error_message,
            output_hash = excluded.output_hash,
            output_size = excluded.output_size,
            updated_at = excluded.updated_at
        """,
        (
            submission_id,
            stage_name,
            baseline_hash,
            status,
            error_message,
            output_hash,
            output_size,
            now,
            now,
        ),
    )

    conn.commit()
    conn.close()


def add_validation_event(
    submission_id: int,
    stage_name: str,
    event_type: str,
    passed: bool,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    cursor.execute(
        """
        INSERT INTO validation_events (submission_id, stage_name, event_type, passed, details_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            submission_id,
            stage_name,
            event_type,
            1 if passed else 0,
            json.dumps(details or {}, default=str),
            created_at,
        ),
    )
    conn.commit()
    conn.close()


def get_stage_checkpoints(submission_id: int) -> list[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT stage_name, baseline_hash, status, attempt_count, error_message, output_hash, output_size, created_at, updated_at
        FROM stage_checkpoints
        WHERE submission_id = ?
        ORDER BY created_at ASC
        """,
        (submission_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "stage_name": row[0],
            "baseline_hash": row[1],
            "status": row[2],
            "attempt_count": row[3],
            "error_message": row[4],
            "output_hash": row[5],
            "output_size": row[6],
            "created_at": row[7],
            "updated_at": row[8],
        }
        for row in rows
    ]


def get_validation_events(submission_id: int) -> list[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT stage_name, event_type, passed, details_json, created_at
        FROM validation_events
        WHERE submission_id = ?
        ORDER BY created_at ASC
        """,
        (submission_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "stage_name": row[0],
            "event_type": row[1],
            "passed": bool(row[2]),
            "details": json.loads(row[3]) if row[3] else {},
            "created_at": row[4],
        }
        for row in rows
    ]


def set_submission_execution_mode(submission_id: int, mode: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE submissions SET execution_mode = ? WHERE id = ?",
        (mode, submission_id),
    )
    conn.commit()
    conn.close()


def get_submission_execution_mode(submission_id: int) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT execution_mode FROM submissions WHERE id = ?",
        (submission_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return row[0]


def set_submission_last_failed_stage(submission_id: int, stage_name: Optional[str]) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE submissions SET last_failed_stage = ? WHERE id = ?",
        (stage_name, submission_id),
    )
    conn.commit()
    conn.close()


def upsert_assumptions_review(
    submission_id: int,
    ai_defaults: Dict[str, Any],
    sources: Dict[str, Any],
    client_overrides: Optional[Dict[str, Any]] = None,
    approved: bool = False,
    notes: Optional[str] = None,
    baseline: Optional[Dict[str, Any]] = None,
    baseline_hash: Optional[str] = None,
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    approved_at = now if approved else None
    cursor.execute(
        """
        INSERT INTO assumptions_review (
            submission_id, ai_defaults_json, sources_json, client_overrides_json,
            approved, notes, baseline_json, baseline_hash, approved_at,
            created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(submission_id)
        DO UPDATE SET
            ai_defaults_json = excluded.ai_defaults_json,
            sources_json = excluded.sources_json,
            client_overrides_json = excluded.client_overrides_json,
            approved = excluded.approved,
            notes = excluded.notes,
            baseline_json = excluded.baseline_json,
            baseline_hash = excluded.baseline_hash,
            approved_at = excluded.approved_at,
            updated_at = excluded.updated_at
        """,
        (
            submission_id,
            json.dumps(ai_defaults, default=str),
            json.dumps(sources, default=str),
            json.dumps(client_overrides or {}, default=str),
            1 if approved else 0,
            notes,
            json.dumps(baseline or {}, default=str) if baseline is not None else None,
            baseline_hash,
            approved_at,
            now,
            now,
        ),
    )
    conn.commit()
    conn.close()


def get_assumptions_review(submission_id: int) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT ai_defaults_json, sources_json, client_overrides_json, approved,
               notes, baseline_json, baseline_hash, approved_at, created_at, updated_at
        FROM assumptions_review
        WHERE submission_id = ?
        """,
        (submission_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None

    return {
        "ai_defaults": json.loads(row[0]) if row[0] else {},
        "sources": json.loads(row[1]) if row[1] else {},
        "client_overrides": json.loads(row[2]) if row[2] else {},
        "approved": bool(row[3]),
        "notes": row[4],
        "baseline": json.loads(row[5]) if row[5] else {},
        "baseline_hash": row[6],
        "approved_at": row[7],
        "created_at": row[8],
        "updated_at": row[9],
    }


def upsert_report_status(
    submission_id: int,
    status: str,
    doc_bytes: Optional[bytes] = None,
    error_message: Optional[str] = None,
    sections_done: Optional[int] = None,
    sections_total: Optional[int] = None,
    current_section: Optional[str] = None,
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """
        INSERT INTO generated_reports
            (submission_id, status, doc_bytes, error_message, sections_done, sections_total, current_section, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(submission_id) DO UPDATE SET
            status = excluded.status,
            doc_bytes = COALESCE(excluded.doc_bytes, generated_reports.doc_bytes),
            error_message = excluded.error_message,
            sections_done = COALESCE(excluded.sections_done, generated_reports.sections_done),
            sections_total = COALESCE(excluded.sections_total, generated_reports.sections_total),
            current_section = COALESCE(excluded.current_section, generated_reports.current_section),
            updated_at = excluded.updated_at
        """,
        (submission_id, status, doc_bytes, error_message, sections_done, sections_total, current_section, now, now),
    )
    conn.commit()
    conn.close()


def get_report_record(submission_id: int) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status, doc_bytes, error_message, sections_done, sections_total, current_section FROM generated_reports WHERE submission_id = ?",
        (submission_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "status": row[0],
        "doc_bytes": row[1],
        "error_message": row[2],
        "sections_done": row[3] or 0,
        "sections_total": row[4] or 0,
        "current_section": row[5],
    }


def get_any_generating_submission_id() -> Optional[int]:
    """Return any submission_id currently in generating status (if present)."""
    lock = get_any_generating_report_lock()
    return lock["submission_id"] if lock else None


def get_any_generating_report_lock() -> Optional[Dict[str, Any]]:
    """Return metadata for the most recently updated generating report lock."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT submission_id, sections_done, sections_total, current_section, updated_at
        FROM generated_reports
        WHERE status = 'generating'
        ORDER BY updated_at DESC
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "submission_id": row[0],
        "sections_done": row[1] or 0,
        "sections_total": row[2] or 0,
        "current_section": row[3],
        "updated_at": row[4],
    }
