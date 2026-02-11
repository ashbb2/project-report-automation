import os
from typing import Dict, Any


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
        return template.format(**safe_variables)
    except KeyError as e:
        raise ValueError(f"Missing required variable in template: {e}")


def get_section_prompt(section_name: str, submission_data: Dict[str, Any]) -> str:
    """
    Load and render a prompt for a specific report section.
    
    Args:
        section_name: Name of the section (e.g., 'executive_summary')
        submission_data: Dictionary containing submission data
        
    Returns:
        Fully rendered prompt ready for LLM
    """
    template = load_prompt(section_name)
    return render_prompt(template, submission_data)
