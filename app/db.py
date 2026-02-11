import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.db")


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
