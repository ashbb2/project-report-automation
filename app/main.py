from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
import os
from app.models import SubmissionCreate, SubmissionResponse
from app.db import init_db, save_submission, get_submission

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


@app.get("/health")
def health_check():
    return {"status": "ok"}
