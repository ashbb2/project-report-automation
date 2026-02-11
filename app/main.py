from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
import os
import uuid
from app.models import SubmissionCreate, SubmissionResponse

app = FastAPI()

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
    Accept form submission, validate with Pydantic, and return normalized payload.
    """
    # Generate a temporary preview ID
    submission_id = f"preview-{uuid.uuid4().hex[:8]}"
    
    # Return the submission with ID
    return SubmissionResponse(
        id=submission_id,
        **submission.model_dump()
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}
