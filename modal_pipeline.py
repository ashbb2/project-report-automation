"""
Modal deployment for the async report generation pipeline.

The FastAPI web server stays on Railway. When a report is requested,
it enqueues a Modal job instead of running the pipeline synchronously.
The job writes the finished .docx back to the database so the web server
can serve it on demand.

Setup:
    pip install modal
    modal setup          # authenticates your account
    modal deploy modal_pipeline.py

Environment variables needed in Modal (set via `modal secret create`):
    ANTHROPIC_API_KEY
    DATABASE_URL  (or leave blank to use SQLite path via volume)
"""

import modal

# ---------------------------------------------------------------------------
# Image — mirrors requirements.txt so the worker has the same deps
# ---------------------------------------------------------------------------
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
# Secrets — add ANTHROPIC_API_KEY via `modal secret create anthropic-secret`
# ---------------------------------------------------------------------------
secrets = [modal.Secret.from_name("anthropic-secret")]


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
# Optional: expose a Modal web endpoint so Railway can trigger via HTTP
# ---------------------------------------------------------------------------
@app.function(
    volumes={
        "/data/db": sqlite_vol,
        "/data/chroma": chroma_vol,
    },
    secrets=secrets,
    timeout=600,
)
@modal.web_endpoint(method="POST")
def trigger_report(submission_id: int, force: bool = False):
    """
    HTTP endpoint alternative — POST /trigger_report?submission_id=42
    Returns the .docx file directly.
    """
    from fastapi.responses import Response

    doc_bytes = generate_report_job.local(submission_id, force)
    return Response(
        content=doc_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=report_{submission_id}.docx"},
    )
