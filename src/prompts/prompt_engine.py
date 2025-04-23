from jinja2 import Template
from storage.s3_functions import save_csv_to_s3, cache_pickle_obj_from_s3
from __utils import safe_eval, is_none_or_empty

bucket_name = "karmacoordinates"
csv_filename = "karma_coordinates_prompts.csv"
object_key = "karma_coordinates_prompts.csv"


# Remember:
# call this from __runner.py to load the file in s3
# remember to delete the current .pkl file from the aws karma/.tmp as wll so it fetches the new file
def save_prompt_in_s3():
    save_csv_to_s3(
        csv_filename=csv_filename,
        csv_seperator=",",
        bucket_name=bucket_name,
        object_key=object_key,
        header=0,
        index_col=0,
    )


def generate_prompt(question: str, variables: dict) -> str:

    df = cache_pickle_obj_from_s3(bucket_name=bucket_name, object_key=object_key)

    contains_question = df['questions'].str.contains(question, na=False, case=False)
    contains_star = df['questions'].str.contains(r'\*', na=False)

    filtered_df = df[contains_question | (~contains_question & contains_star)]

    question = filtered_df.iloc[0] if not filtered_df.empty else None

    if is_none_or_empty(question):
        raise ValueError("Prompt engine unable to determine an appropriate prompt.")
    else:
        raw_template = question["prompt"]

    template = Template(raw_template)
    return template.render(**variables)


def popular_questions():
    df = cache_pickle_obj_from_s3(bucket_name=bucket_name, object_key=object_key)

    df["popular_questions"] = (
        df["popular_questions"]
        .dropna()
        .apply(lambda x: safe_eval(x) if isinstance(x, str) else x)
    )

    flat_list = [
        item
        for sublist in df["popular_questions"]
        if isinstance(sublist, list)
        for item in sublist
    ]

    return {"popular_questions": flat_list}
