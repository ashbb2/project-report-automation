import os
from typing import Dict, Any





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


def get_section_prompt(section_name: str, submission_data: Dict[str, Any], extra_context: Dict[str, Any] = None) -> str:
    """Load and render a prompt for a specific report section."""
    template = load_prompt(section_name)
    prompt_data = {
        **submission_data,
        "output_specification": load_output_specification(),
        "rag_context": "No reference documents available.",
    }
    if extra_context:
        prompt_data.update(extra_context)
    return render_prompt(template, prompt_data)
