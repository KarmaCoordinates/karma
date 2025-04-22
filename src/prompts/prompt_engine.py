from jinja2 import Template
from .base_prompt_templates import PROMPT_TEMPLATES
from storage.s3_functions import save_csv_to_s3, cache_csv_from_s3
from __utils import safe_eval, is_none_or_empty

bucket_name = 'karmacoordinates'
csv_filename = 'karma_coordinates_prompts.csv'
object_key = 'karma_coordinates_prompts.csv'

def save_prompt_in_s3():
    save_csv_to_s3(csv_filename=csv_filename, csv_seperator=",", bucket_name=bucket_name, object_key=object_key)


def generate_prompt(question: str, variables: dict) -> str:

    df = cache_csv_from_s3(bucket_name=bucket_name, object_key=object_key)

    popular_questions = df[df["popular_questions"].str.contains(question, na=False)]
    popular_question = popular_questions.iloc[0] if not popular_questions.empty else None

    if is_none_or_empty(popular_question):
        raw_template = PROMPT_TEMPLATES.get("default_prompt")
    else: 
       raw_template = popular_question["prompt"]

    template = Template(raw_template)
    return template.render(**variables)

def popular_questions():
    df = cache_csv_from_s3(bucket_name=bucket_name, object_key=object_key)

    df['popular_questions'] = df['popular_questions'].dropna().apply(
        lambda x: safe_eval(x) if isinstance(x, str) else x
    )
    flat_list = [item for sublist in df['popular_questions'].to_list() for item in sublist]

    return {"popular_questions" : flat_list}



