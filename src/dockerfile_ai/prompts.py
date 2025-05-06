"""Module for managing Dockerfile analysis prompts."""
from pathlib import Path
from typing import Optional

def get_prompt_path() -> Path:
    """Get the path to the prompts directory."""
    # Get the package root directory
    package_root = Path(__file__).parent.parent.parent
    return package_root / "ai" / "prompts"

def read_prompt(prompt_name: str = "v2") -> str:
    """Read a prompt from the prompts directory.
    
    Args:
        prompt_name: Name of the prompt file to read (default: v2)
        
    Returns:
        The contents of the prompt file
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompt_path = get_prompt_path() / prompt_name
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text()

def format_prompt(dockerfile_content: str, prompt_template: Optional[str] = None) -> str:
    """Format the prompt template with the Dockerfile content.
    
    Args:
        dockerfile_content: The content of the Dockerfile to analyze
        prompt_template: Optional custom prompt template. If None, uses the default prompt.
        
    Returns:
        The formatted prompt ready to send to Ollama
    """
    if prompt_template is None:
        prompt_template = read_prompt()
    
    return f"{prompt_template}\n\n{dockerfile_content}" 