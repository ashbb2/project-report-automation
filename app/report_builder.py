from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any
from io import BytesIO


def build_doc(submission: Dict[str, Any]) -> bytes:
    """
    Build a Word document from submission data.
    
    Args:
        submission: Dictionary containing submission data
        
    Returns:
        Bytes of the generated .docx file
    """
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
    exec_summary = doc.add_paragraph()
    exec_summary.add_run(f"Business Idea: ").bold = True
    exec_summary.add_run(f"{submission.get('business_idea', 'N/A')}\n\n")
    exec_summary.add_run(f"Target Market: ").bold = True
    exec_summary.add_run(f"{submission.get('target_market', 'N/A')}\n\n")
    exec_summary.add_run(
        "This report evaluates the feasibility of the proposed project based on market conditions, "
        "resource requirements, and strategic alignment."
    )
    
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
    doc.add_paragraph(
        f"Target Market: {submission.get('target_market', 'N/A')}\n\n"
        f"Location & Resources: {submission.get('location_land', 'N/A')}\n\n"
        "The market assessment evaluates demand, competition, and growth opportunities within the identified "
        "market segment. Further detailed analysis is required to validate market assumptions."
    )
    
    # Risk Assessment & Mitigation
    doc.add_heading('Risk Assessment & Mitigation', level=1)
    doc.add_paragraph(
        "Key Risks Identified:\n"
        "• Market adoption risk\n"
        "• Operational execution risk\n"
        "• Financial sustainability risk\n\n"
        "Mitigation Strategies:\n"
        "• Phased implementation approach\n"
        "• Regular progress monitoring\n"
        "• Contingency planning"
    )
    
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
