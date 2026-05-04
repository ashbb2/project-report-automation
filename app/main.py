from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from jinja2 import Environment, FileSystemLoader
import os
import asyncio
from app.models import SubmissionCreate, SubmissionResponse, SubmissionResponseWithValidation, ValidationSummary
from app.db import init_db, save_submission, get_submission, upsert_report_status, get_report_record
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
    google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    return template.render(google_maps_api_key=google_maps_api_key)


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


async def _run_report_background(submission_id: int, submission_data: dict, force: bool):
    """Background task: generate report and save bytes to DB."""
    try:
        upsert_report_status(submission_id, "generating")
        doc_bytes = await asyncio.to_thread(build_doc, submission_data, submission_id, force)
        upsert_report_status(submission_id, "done", doc_bytes=doc_bytes)
    except Exception as e:
        upsert_report_status(submission_id, "failed", error_message=str(e))


@app.post("/api/report/{submission_id}/start")
async def start_report(submission_id: int, background_tasks: BackgroundTasks, force: bool = False):
    """Start background report generation. Returns immediately."""
    submission = get_submission(submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    record = get_report_record(submission_id)
    if record and record["status"] == "done" and not force:
        return {"status": "done"}
    if record and record["status"] == "generating":
        return {"status": "generating"}

    submission_data = {k: v for k, v in submission.items() if k not in ["id", "created_at"]}
    background_tasks.add_task(_run_report_background, submission_id, submission_data, force)
    return {"status": "generating"}


@app.get("/api/report/{submission_id}/status")
async def report_status(submission_id: int):
    """Poll report generation status."""
    record = get_report_record(submission_id)
    if not record:
        return {"status": "not_started", "sections_done": 0, "sections_total": 0, "current_section": None}
    return {
        "status": record["status"],
        "error": record.get("error_message"),
        "sections_done": record.get("sections_done", 0),
        "sections_total": record.get("sections_total", 0),
        "current_section": record.get("current_section"),
    }


@app.get("/api/report/{submission_id}/download")
async def download_report(submission_id: int):
    """Download the completed report."""
    record = get_report_record(submission_id)
    if not record or record["status"] != "done" or not record["doc_bytes"]:
        raise HTTPException(status_code=404, detail="Report not ready yet")
    return StreamingResponse(
        iter([record["doc_bytes"]]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=report_{submission_id}.docx"},
    )


@app.get("/api/report/{submission_id}")
@app.post("/api/report/{submission_id}")
async def generate_report(submission_id: int, force: bool = False):
    """Legacy sync endpoint — kept for compatibility."""
    submission = get_submission(submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    submission_data = {k: v for k, v in submission.items() if k not in ["id", "created_at"]}
    doc_bytes = await asyncio.to_thread(build_doc, submission_data, submission_id, force)
    return StreamingResponse(
        iter([doc_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=report_{submission_id}.docx"},
    )


@app.get("/api/market-interest-rate")
def market_interest_rate():
    return {"rate": 10.5, "source": "RBI indicative rate", "note": "Indicative only — confirm with your lender"}


@app.get("/api/pricing-estimate/{submission_id}")
async def pricing_estimate(submission_id: int):
    return {"available": False}


@app.get("/health")
def health_check():
    return {"status": "ok"}
