from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from jinja2 import Environment, FileSystemLoader
import os
from io import BytesIO
from app.models import SubmissionCreate, SubmissionResponse
from app.db import init_db, save_submission, get_submission
from app.report_builder import build_doc

app = FastAPI()

# Initialize database on startup
init_db()

# Set up Jinja2 templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_dir = os.path.join(BASE_DIR, "app", "templates")
env = Environment(loader=FileSystemLoader(templates_dir))


@app.get("/", response_class=HTMLResponse)
async def get_form():
    template = env.get_template("form.html")
    return template.render()


@app.post("/api/submit", response_model=SubmissionResponse)
async def submit_form(submission: SubmissionCreate):
    """
    Accept form submission, validate with Pydantic, save to database, and return ID.
    """
    # Convert submission to dict and save to database
    payload = submission.model_dump()
    submission_id = save_submission(payload)
    
    # Return the submission with ID
    return SubmissionResponse(
        id=str(submission_id),
        **payload
    )


@app.get("/api/submission/{submission_id}", response_model=SubmissionResponse)
async def get_submission_by_id(submission_id: int):
    """
    Retrieve a stored submission by ID.
    """
    submission = get_submission(submission_id)
    
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return SubmissionResponse(**submission)


@app.post("/api/report/{submission_id}")
async def generate_report(submission_id: int, force: bool = False):
    """
    Generate a Word document report for a submission.
    
    Args:
        submission_id: The ID of the submission
        force: If True, regenerate all sections even if cached (default: False)
    """
    # Retrieve submission from database
    submission = get_submission(submission_id)
    
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Remove 'id' and 'created_at' from submission for report generation
    submission_data = {k: v for k, v in submission.items() if k not in ['id', 'created_at']}
    
    # Generate Word document with AI content and caching
    doc_bytes = build_doc(submission_data, submission_id, force)
    
    # Return as streaming response (downloadable file)
    return StreamingResponse(
        iter([doc_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=report_{submission_id}.docx"}
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}
