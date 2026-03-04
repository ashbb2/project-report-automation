from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from jinja2 import Environment, FileSystemLoader
import os
from io import BytesIO
from app.models import SubmissionCreate, SubmissionResponse, SubmissionResponseWithValidation, ValidationSummary
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


def validate_critical_inputs(submission: SubmissionCreate) -> ValidationSummary:
    """
    Validate critical vs optional inputs per Policy C.
    Returns summary of missing critical and optional fields.
    """
    critical_missing = []
    optional_missing = []
    assumptions_used = []
    
    # Check sizing mode specific requirements
    if submission.sizing_mode.value == "capacity_driven" and not submission.target_capacity:
        critical_missing.append("target_capacity (required for capacity-driven mode)")
    if submission.sizing_mode.value == "budget_driven" and not submission.total_investment:
        critical_missing.append("total_investment (required for budget-driven mode)")
    
    # Check optional fields
    if not submission.product_mix:
        optional_missing.append("product_mix")
        assumptions_used.append("Single product line assumed")
    
    if not submission.utilities_consumption:
        optional_missing.append("utilities_consumption")
        assumptions_used.append("Industry standard utility consumption rates will be applied")
    
    if not submission.moratorium_period:
        optional_missing.append("moratorium_period")
        assumptions_used.append("No moratorium period assumed")
    
    if not submission.preferred_manufacturer_geography:
        optional_missing.append("preferred_manufacturer_geography")
    
    if not submission.brand_preferences:
        optional_missing.append("brand_preferences")
    
    if not submission.technology_exclusions:
        optional_missing.append("technology_exclusions")
    
    if not submission.promoter_background:
        optional_missing.append("promoter_background")
    
    if not submission.start_date:
        optional_missing.append("start_date")
    
    if not submission.target_launch_date:
        optional_missing.append("target_launch_date")
    
    return ValidationSummary(
        critical_missing=critical_missing,
        optional_missing=optional_missing,
        assumptions_used=assumptions_used
    )


@app.post("/api/submit", response_model=SubmissionResponseWithValidation)
async def submit_form(submission: SubmissionCreate):
    """
    Accept form submission, validate with Pydantic, save to database, and return ID.
    Implements Policy C: strict validation for critical fields, permissive for optional.
    """
    # Validate inputs per Policy C
    validation_summary = validate_critical_inputs(submission)
    
    # Policy C: Block submission if critical fields are missing
    if validation_summary.critical_missing:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Critical fields missing",
                "critical_missing": validation_summary.critical_missing
            }
        )
    
    # Convert submission to dict and save to database
    payload = submission.model_dump()
    submission_id = save_submission(payload)
    
    # Return the submission with ID and validation summary
    return SubmissionResponseWithValidation(
        id=str(submission_id),
        validation_summary=validation_summary,
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


@app.get("/api/report/{submission_id}")
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
