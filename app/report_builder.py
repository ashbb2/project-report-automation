from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any, List
from io import BytesIO
from app.llm_client import llm_client
from app.prompt_renderer import get_section_prompt
from app.db import get_cached_section, save_section


def identify_missing_inputs(submission: Dict[str, Any]) -> List[str]:
    """
    Identify which fields are missing or blank in the submission.
    
    Args:
        submission: Dictionary containing submission data
        
    Returns:
        List of missing field names
    """
    required_fields = [
        'business_idea', 'location_land', 'promoter_background',
        'goals', 'start_date', 'target_launch_date', 'budget', 'target_market'
    ]
    
    missing = []
    for field in required_fields:
        value = submission.get(field)
        if not value or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    
    return missing


def get_or_generate_section(
    submission_id: int, 
    section_name: str, 
    submission_data: Dict[str, Any],
    force: bool = False
) -> str:
    """
    Get cached section or generate new one using LLM.
    
    Args:
        submission_id: The submission ID
        section_name: Name of the section to generate
        submission_data: Dictionary containing submission data
        force: If True, regenerate even if cached
        
    Returns:
        Generated or cached section content
    """
    # Check cache unless force is True
    if not force:
        cached = get_cached_section(submission_id, section_name)
        if cached:
            return cached
    
    # Generate new content
    rendered_prompt = get_section_prompt(section_name, submission_data)
    content = llm_client.generate(rendered_prompt)
    
    # Cache the result
    save_section(submission_id, section_name, content)
    
    return content


def build_doc(submission: Dict[str, Any], submission_id: int, force: bool = False) -> bytes:
    """
    Build a Word document from submission data with AI-generated content.
    
    Args:
        submission: Dictionary containing submission data
        submission_id: The submission ID for caching
        force: If True, regenerate sections even if cached
        
    Returns:
        Bytes of the generated .docx file
    """
    # Identify missing inputs for assumptions
    missing_inputs = identify_missing_inputs(submission)
    
    # Add missing_inputs info to submission data for prompt rendering
    submission_with_context = {**submission}
    if missing_inputs:
        submission_with_context['missing_inputs'] = ', '.join(missing_inputs)
    else:
        submission_with_context['missing_inputs'] = 'None'
    
    # Generate or retrieve cached sections
    exec_summary = get_or_generate_section(
        submission_id, 'executive_summary', submission_with_context, force
    )
    market = get_or_generate_section(
        submission_id, 'market_assessment', submission_with_context, force
    )
    risk = get_or_generate_section(
        submission_id, 'risk_assessment', submission_with_context, force
    )
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    # Title
    title = doc.add_heading('Project Feasibility Report', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Subtitle with project name
    subtitle = doc.add_paragraph(f"Project: {submission.get('business_idea', 'N/A')}")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_format = subtitle.runs[0]
    subtitle_format.font.size = Pt(12)
    subtitle_format.font.italic = True
    
    doc.add_paragraph()  # Spacing
    
    # Executive Summary
    doc.add_heading('Executive Summary', level=1)
    doc.add_paragraph(exec_summary)
    
    # Introduction
    doc.add_heading('Introduction', level=1)
    
    doc.add_heading('Background & Context', level=2)
    doc.add_paragraph(
        f"The project centers on the following business idea: {submission.get('business_idea', 'N/A')}. "
        f"This initiative aims to operate in the {submission.get('target_market', 'N/A')} market segment."
    )
    
    doc.add_heading('Value Proposition', level=2)
    doc.add_paragraph(
        f"Project Goals: {submission.get('goals', 'N/A')}\n\n"
        f"The proposed venture seeks to address market needs while achieving the stated objectives within "
        f"the planned timeline and budget of {submission.get('budget', 'N/A')} currency units."
    )
    
    doc.add_heading('Promoter Background', level=2)
    doc.add_paragraph(
        f"Team & Experience: {submission.get('promoter_background', 'N/A')}"
    )
    
    # Market Assessment
    doc.add_heading('Market Assessment', level=1)
    doc.add_paragraph(market)
    
    # Risk Assessment & Mitigation
    doc.add_heading('Risk Assessment & Mitigation', level=1)
    doc.add_paragraph(risk)
    
    # Caveats
    doc.add_heading('Caveats', level=1)
    doc.add_paragraph(
        "This feasibility assessment is based on the information provided by the proposer. "
        "Additional due diligence and market research may be required. Assumptions should be validated "
        "with external market data and expert consultation."
    )
    
    # Timeline
    doc.add_heading('Project Timeline', level=1)
    timeline_para = doc.add_paragraph()
    timeline_para.add_run(f"Start Date: ").bold = True
    timeline_para.add_run(f"{submission.get('start_date', 'N/A')}\n")
    timeline_para.add_run(f"Target Launch Date: ").bold = True
    timeline_para.add_run(f"{submission.get('target_launch_date', 'N/A')}")
    
    # Budget
    doc.add_heading('Budget Overview', level=1)
    budget_para = doc.add_paragraph()
    budget_para.add_run(f"Total Project Budget: ").bold = True
    budget_para.add_run(f"{submission.get('budget', 'N/A')} currency units")
    
    # Appendices
    doc.add_heading('Appendices', level=1)
    doc.add_paragraph(
        "A. Additional Notes:\n"
        f"{submission.get('notes', 'No additional notes provided')}\n\n"
        "B. Supporting Documentation:\n"
        "• Market research reports\n"
        "• Financial projections\n"
        "• Organizational structure"
    )
    
    # Footer
    doc.add_paragraph()
    footer = doc.add_paragraph("---")
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_text = doc.add_paragraph(
        "This report was generated automatically by the Project Report Automation system."
    )
    footer_text.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_text.runs[0].font.size = Pt(9)
    footer_text.runs[0].font.italic = True
    
    # Save to bytes
    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output.getvalue()
