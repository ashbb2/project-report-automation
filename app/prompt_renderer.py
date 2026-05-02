import os
from typing import Dict, Any

from app.rag import retrieve


# Map each report section to the most useful RAG query
_SECTION_RAG_QUERIES = {
    "executive_summary": "business feasibility overview India",
    "introduction": "project introduction business plan India",
    "regulatory_framework": "Indian regulations licenses permits sector compliance",
    "market_assessment": "Indian market size growth trends sector",
    "business_operating_model": "business operating model India production process",
    "equipment_profiles": "equipment machinery specifications manufacturers India",
    "financial_feasibility": "financial projections feasibility India investment",
    "risk_assessment": "business risks India regulatory market financial",
    "caveats": "report limitations assumptions caveats India",
    "appendices": "supporting data references appendix India",
}


class SafePromptVariables(dict):
    """Return a fallback string for missing prompt variables."""

    def __missing__(self, key):
        return "Not provided"


def load_output_specification() -> str:
    """
    Load the editable report output specification markdown.

    Returns:
        Markdown content from docs/report-output-specification.md
    """
    docs_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "docs",
        "report-output-specification.md",
    )
    if not os.path.exists(docs_path):
        return "Output specification file not found."

    with open(docs_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt template file from the prompts directory.
    
    Args:
        prompt_name: Name of the prompt file (without .txt extension)
        
    Returns:
        The prompt template content as a string
    """
    prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
    prompt_path = os.path.join(prompts_dir, f"{prompt_name}.txt")
    
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt template not found: {prompt_path}")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def render_prompt(template: str, variables: Dict[str, Any]) -> str:
    """
    Render a prompt template by substituting variables.
    
    Args:
        template: The prompt template string with {variable} placeholders
        variables: Dictionary of variable names to values
        
    Returns:
        The rendered prompt with variables substituted
    """
    # Convert all values to strings and handle None values
    safe_variables = {}
    for key, value in variables.items():
        if value is None:
            safe_variables[key] = "Not provided"
        else:
            safe_variables[key] = str(value)
    
    try:
        return template.format_map(SafePromptVariables(safe_variables))
    except Exception as e:
        raise ValueError(f"Failed to render template: {e}")


def get_section_prompt(section_name: str, submission_data: Dict[str, Any]) -> str:
    """
    Load and render a prompt for a specific report section.
    Injects relevant RAG context from reference reports and Indian regulations.
    """
    template = load_prompt(section_name)

    # Build a targeted query combining the section intent with the business context
    base_query = _SECTION_RAG_QUERIES.get(section_name, section_name)
    business_idea = submission_data.get("business_idea", "")
    sector = submission_data.get("product_service", "")
    rag_query = f"{base_query} {business_idea} {sector}".strip()

    rag_context = retrieve(rag_query, n_results=4)

    prompt_data = {
        **submission_data,
        "output_specification": load_output_specification(),
        "rag_context": rag_context or "No reference documents available.",
    }
    return render_prompt(template, prompt_data)
