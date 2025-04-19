from jinja2 import Template
from .base_prompt_templates import PROMPT_TEMPLATES

def generate_prompt(prompt_key: str, variables: dict) -> str:
    raw_template = PROMPT_TEMPLATES.get(prompt_key)
    if not raw_template:
        raw_template = PROMPT_TEMPLATES.get('question')
    if not raw_template:
        raise ValueError(f"No prompt found for key: {prompt_key}")

    template = Template(raw_template)
    return template.render(**variables)