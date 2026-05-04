"""
Modal deployment — serves the full FastAPI web app AND runs async report jobs.

Setup:
    pip install modal
    modal setup                                    # authenticate
    modal secret create anthropic-secret ANTHROPIC_API_KEY=sk-ant-...
    modal secret create google-maps-secret GOOGLE_MAPS_API_KEY=...  # optional
    modal deploy modal_pipeline.py

The web app is served at the URL printed after deploy.
Report generation runs as a background function on the same app.
"""

import modal
from pathlib import Path

# ---------------------------------------------------------------------------
# Image — includes pip deps + local source files baked in
# ---------------------------------------------------------------------------
_root = Path(__file__).parent
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi",
        "uvicorn[standard]",
        "jinja2",
        "python-docx",
        "python-dotenv",
        "pydantic",
        "anthropic",
        "chromadb",
        "PyPDF2",
        "docx2txt",
        "sentence-transformers",
    )
    .add_local_dir(_root / "app", remote_path="/root/app")
    .add_local_dir(_root / "docs", remote_path="/root/docs")
)

# ---------------------------------------------------------------------------
# Persistent volumes — shared between Railway web server and Modal workers
# ---------------------------------------------------------------------------
# Mount the SQLite database and ChromaDB so the worker can read/write them.
# In production with PostgreSQL, replace the sqlite_vol with your DB URL secret.
sqlite_vol = modal.Volume.from_name("project-automation-db", create_if_missing=True)
chroma_vol = modal.Volume.from_name("project-automation-chroma", create_if_missing=True)

app = modal.App(
    name="project-automation",
    image=image,
)

# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------
secrets = [modal.Secret.from_name("anthropic-secret")]
# Add Google Maps secret if you've created it:
#   modal secret create google-maps-secret GOOGLE_MAPS_API_KEY=...
try:
    _gmaps = modal.Secret.from_name("google-maps-secret")
    secrets = [modal.Secret.from_name("anthropic-secret"), _gmaps]
except Exception:
    pass


@app.function(
    volumes={
        "/data/db": sqlite_vol,
        "/data/chroma": chroma_vol,
    },
    secrets=secrets,
    timeout=600,        # 10 min max per report job
    retries=1,
)
def generate_report_job(submission_id: int, force: bool = False) -> bytes:
    """
    Run the full staged pipeline for a submission and return the .docx bytes.

    Called remotely from the FastAPI web server:
        result = generate_report_job.remote(submission_id)
    """
    import os
    import sys

    # Point the app at the volume-mounted paths
    os.environ.setdefault("CHROMA_DB_PATH", "/data/chroma")
    os.environ.setdefault("DATABASE_PATH", "/data/db/submissions.db")
    os.environ["LLM_PROVIDER"] = "claude"

    # Add project root to path so app.* imports work
    sys.path.insert(0, "/root")

    from app.db import get_submission
    from app.execution_backend import StagedBackend, LegacyBackend
    from app.config import Config

    submission = get_submission(submission_id)
    if submission is None:
        raise ValueError(f"Submission {submission_id} not found")

    submission_data = {k: v for k, v in submission.items() if k not in ("id", "created_at")}

    if Config.USE_STAGED_PIPELINE:
        return StagedBackend().build_report(submission_id, submission_data, force)
    return LegacyBackend().build_report(submission_id, submission_data, force)


# ---------------------------------------------------------------------------
# ASGI web server — serves the full FastAPI app on Modal
# ---------------------------------------------------------------------------
@app.function(
    volumes={
        "/data/db": sqlite_vol,
        "/data/chroma": chroma_vol,
    },
    secrets=secrets,
    min_containers=1,
    timeout=900,  # 15 min — report generation runs synchronously inside the web request
)
@modal.asgi_app()
def web():
    import os
    import sys

    os.environ["DATABASE_PATH"] = "/data/db/submissions.db"
    os.environ.setdefault("CHROMA_DB_PATH", "/data/chroma")
    os.environ["LLM_PROVIDER"] = "claude"

    sys.path.insert(0, "/root")

    from app.main import app as fastapi_app
    return fastapi_app


# ---------------------------------------------------------------------------
# Trigger endpoint — POST to kick off a report job (called from the web app)
# ---------------------------------------------------------------------------
@app.function(
    volumes={
        "/data/db": sqlite_vol,
        "/data/chroma": chroma_vol,
    },
    secrets=secrets,
    timeout=600,
)
@modal.fastapi_endpoint(method="POST")
def trigger_report(submission_id: int, force: bool = False):
    """POST /trigger_report?submission_id=42 — runs report job and returns .docx"""
    import os, sys
    from fastapi.responses import Response

    os.environ["DATABASE_PATH"] = "/data/db/submissions.db"
    os.environ.setdefault("CHROMA_DB_PATH", "/data/chroma")
    os.environ["LLM_PROVIDER"] = "claude"
    sys.path.insert(0, "/root")

    doc_bytes = generate_report_job.local(submission_id, force)
    return Response(
        content=doc_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=report_{submission_id}.docx"},
    )
