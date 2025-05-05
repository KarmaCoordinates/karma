import json

import aiohttp
import __utils, __configs
import assessment.score_functions as sf
import storage.dynamodb_functions as db
from fastapi import Request
from pandas import DataFrame
import pandas as pd
import ast
import re
import time
import storage.s3_functions as s3f
import asyncio
import plotly.io as pio
import plotly.graph_objects as go
from io import StringIO
import math
from urllib.parse import urljoin


def cache_questionnaire(
    bucket_name, features_data_dict_object_key, categories_data_dict_object_key
):
    features_df = s3f.cache_csv_from_s3(
        bucket_name=bucket_name, object_key=features_data_dict_object_key
    )
    key_value_columns = [
        "Option_1",
        "Value_1",
        "Option_2",
        "Value_2",
        "Option_3",
        "Value_3",
        "Option_4",
        "Value_4",
    ]
    features_df["options_dict"] = [
        {k: v for k, v in zip(row[::2], row[1::2]) if pd.notna(k) and pd.notna(v)}
        for row in features_df[key_value_columns].values
    ]
    key_columns = ["Option_1", "Option_2", "Option_3", "Option_4"]
    features_df["options_list"] = [
        list(filter(pd.notna, item)) for item in zip(*features_df[key_columns].values.T)
    ]
    categories_df = s3f.cache_csv_from_s3(
        bucket_name=bucket_name, object_key=categories_data_dict_object_key
    )

    value_columns = features_df[["Value_1", "Value_2", "Value_3", "Value_4"]]
    minimum_score = value_columns.min(axis=1).sum()
    maximum_score = value_columns.max(axis=1).sum()

    return (
        features_df,
        categories_df,
        {
            "minimum_score": minimum_score,
            "maximum_score": maximum_score,
            "number_of_questions": len(features_df),
        },
    )


def __score_summary(category_score):
    clarity_of_thinking_index = sum(category_score.values())
    clarity_of_thinking_index_dict = {
        "clarity_of_thinking_index": str(sum(category_score.values()))
    }
    category_score_str = ""
    category_score_dict = {}
    for category, score in category_score.items():
        category_score_str = category_score_str + f"""{category}:{round(score, 1)}, """
        category_score_dict.update({category: str(round(score, 1))})

    # score_md is for backward-compatibility
    score_md = f"""Your **Clarity of Thinking** score: **{clarity_of_thinking_index}** [{category_score_str}] """

    category_score_array = [
        {"category": k, "score": category_score_dict[k]} for k in category_score_dict
    ]

    return (
        score_md,
        {"assessment_score": category_score_array},
        clarity_of_thinking_index_dict,
    )


def __calc_category_score(features_df, categories_df, user_answers):
    category_score = {}
    for category_tpl in categories_df.itertuples():
        category_score[category_tpl.category_name] = 0
        for feature_tpl in features_df.loc[
            features_df["Category"] == category_tpl.category_name
        ].itertuples():
            default_index = 0
            default_selected_option = None
            if feature_tpl.Question in user_answers:
                default_selected_option = user_answers[feature_tpl.Question]
            else:
                default_selected_option = feature_tpl.options_list[default_index]

            # st.session_state.user_answers.update({feature_tpl.Question:default_selected_option})
            selected_option_score = feature_tpl.options_dict.get(
                default_selected_option
            )

            if selected_option_score:
                category_score[category_tpl.category_name] += selected_option_score

    return category_score


async def __update_ai_assessment(
    request: Request,
    user_answers,
    features_df: DataFrame,
    categories_df: DataFrame,
    features_df_stats,
    analysis,
):
    ai_assessment = {}
    rx = r"(\{[^{}]+\})"
    matches = re.findall(rx, analysis)
    if matches and len(matches) > 0:
        updated_dict = ast.literal_eval(matches[0])
        for q in updated_dict.keys():
            matched_question = features_df.loc[features_df["Question"] == q]
            if len(matched_question) == 1:
                ai_answer = updated_dict.get(q)
                if any(
                    answer_option.startswith(ai_answer)
                    for answer_option in matched_question.get("options_list").values[0]
                ):
                    ai_assessment.update({q: ai_answer})

        if ai_assessment:
            user_answers[0].update(ai_assessment)
            user_answers[0].update({"date": str(time.time())})

            category_score = __calc_category_score(
                features_df, categories_df, user_answers[0]
            )
            score_md, assessment_score_dict, clarity_of_thinking_index_dict = (
                __score_summary(category_score)
            )
            lives_to_moksha = sf.calculate_karma_coordinates(
                category_score, features_df_stats
            )

            user_answers[0].update(
                {
                    "score_ai_analysis_query": score_md,
                    "lives_to_moksha": lives_to_moksha,
                }
            )

            user_answers[0].update(assessment_score_dict)
            user_answers[0].update(clarity_of_thinking_index_dict)

            db.insert(user_activity_data=user_answers[0])


async def stream_ai_assist_reflect_response(
    request: Request,
    user_answers,
    features_df: DataFrame,
    categories_df: DataFrame,
    features_df_stats,
    assistant_id,
    thread_id,
):
    async_client = __configs.get_config().openai_async_client

    stream = async_client.beta.threads.runs.stream(
        assistant_id=assistant_id, thread_id=thread_id
    )

    complete_text = ""
    async with stream as stream:
        async for text in stream.text_deltas:
            # formatted_text = text.replace('\n', '\\n')
            complete_text += text
            yield f"{text}"
            # yield f"data: {text}\n\n"

    asyncio.create_task(
        __update_ai_assessment(
            request,
            user_answers,
            features_df,
            categories_df,
            features_df_stats,
            complete_text,
        )
    )


async def stream_ai_assist_explore_response(
    request: Request,
    features_df,
    categories_df,
    features_df_stats,
    assistant_id,
    thread_id,
):
    async_client = __configs.get_config().openai_async_client

    # Ensure no active run before starting a new one
    existing_runs = await async_client.beta.threads.runs.list(
        thread_id=thread_id, limit=1
    )
    if existing_runs.data and existing_runs.data[0].status in [
        "in_progress",
        "queued",
        "requires_action",
    ]:
        raise Exception("Thread already has an active run.")

    # Start new run with streaming
    stream = await async_client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=thread_id,
        tool_choice="auto",
        stream=True,
    )

    tool_call_ids_to_output = {}
    complete_text = ""
    tool_output_yielded = False

    async with stream as event_stream:
        async for event in event_stream:
            if event.event == "thread.message.delta":
                delta = event.data.delta
                if hasattr(delta, "content") and delta.content:
                    if isinstance(delta.content, list):
                        for part in delta.content:
                            if hasattr(part, "text") and part.text.value:
                                complete_text += part.text.value
                                yield part.text.value
                    elif isinstance(delta.content, str):
                        complete_text += delta.content
                        yield delta.content

            elif event.event == "thread.run.requires_action":
                # Handle function/tool calls
                async for text in __handleRequiresActions(
                    async_client, thread_id, event, request
                ):
                    tool_output_yielded = True
                    yield text

            elif event.event == "thread.run.completed":
                break

            elif event.event in [
                "thread.run.failed",
                "thread.run.expired",
                "thread.run.cancelled",
            ]:
                yield "[Assistant run failed or was cancelled]"
                break

    if not complete_text and not tool_output_yielded:
        yield "[No response received from assistant]"


async def __handleRequiresActions(async_client, thread_id, event, request):
    tool_calls = event.data.required_action.submit_tool_outputs.tool_calls
    tool_outputs = []

    for tool_call in tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if name == "delete_account":
            confirm_text = args.get("delete_confirmation")
            required_text = f"I ({request.user.display_name}) hereby confirm my request to delete my account permanently. I understand that all my journal entries, AI assessments, and scores will be lost forever."
            if confirm_text == required_text:
                delete_url = urljoin(str(request.base_url), "delete-account")
                token = request.headers.get("authorization")
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{delete_url}",
                        json={"delete_confirmation": confirm_text},
                        headers={"Authorization": token},
                    ) as resp:
                        result = await resp.json()
                        if resp.status == 200:
                            result = {"message": "Account successfully deleted."}
                            yield "\n✅ Account successfully deleted.\n"
                        else:
                            result = {"message": "Account deletion failed."}
                            yield f"\n❌ Deletion failed: {result.get('message')}\n"
            else:
                result = {"message": "Invalid confirmation string."}
                yield "\n❌ Invalid confirmation string. Please type the exact phrase to proceed.\n"

            tool_outputs.append(
                {
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(result),
                }
            )

    await async_client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id, run_id=event.data.id, tool_outputs=tool_outputs
    )


def clickable_progress_chart(rows: str):
    if rows is None:
        return

    json_file = StringIO(rows)
    df = pd.read_json(json_file)

    if (
        not db.Columns().lives_to_moksha in df.columns
        or not db.Columns().journal_entry in df.columns
        or not db.Columns().date in df.columns
    ):
        return

    df = df[
        [db.Columns().date, db.Columns().lives_to_moksha, db.Columns().journal_entry]
    ].dropna()
    df["Timeline"] = pd.to_datetime(df["date"])
    df["Journal"] = df[db.Columns().journal_entry].apply(
        lambda x: __utils.insert_line_breaks(x)
    )

    layout = go.Layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    fig = go.Figure(
        data=[
            go.Scatter(
                x=df["Timeline"],
                y=df[db.Columns().lives_to_moksha],
                text=df[db.Columns().journal_entry].str.slice(0, 50),
                mode="lines+markers",
                line=dict(color="gold"),
                hovertemplate="<b>%{text}</b>",
            )
        ],
        layout=layout,
    )
    fig.update_layout(
        {
            "title_text": "My progress<br><sup>on path to Moksha</sup>",
            "hoverlabel.align": "left",
            "xaxis_title": "Timeline",
            "yaxis_title": "Lives to Moksha",
        }
    )

    return pio.to_json(fig)


def clickable_score_diagram(score_df, assessment_percent_completion):
    layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
        showlegend=False,
    )

    moksha_row_df = score_df[score_df["category"] == "Moksha"]
    moksha_score = moksha_row_df["score"].values[0]
    score_df = score_df[score_df["category"] != "Moksha"]
    labels = score_df["category"]
    original_values = score_df["score"]
    # score_df["score"] = pd.to_numeric(score_df["score"], errors="coerce")
    score_df.loc[:, "score"] = pd.to_numeric(score_df["score"], errors="coerce")
    # custom_colors = ["#FF5733", "#33FF57", "#3357FF", "#F39C12", "#9B59B6"]
    custom_colors = ["#FF5733", "#1E90FF", "#228B22", "#D35400", "#8E44AD"]
    custom_text = [
        f"{label}:<br>{value}" for label, value in zip(labels, original_values)
    ]

    # Create donut chart (using abs value if you want positive slices)
    fig = go.Figure(
        data=[
            go.Pie(
                labels=score_df["category"],
                values=score_df["score"].abs(),  # or .score if values are positive
                text=custom_text,
                textinfo="text",
                # "textinfo": "label+value",  // Display only the label and actual value on the chart itself
                hoverinfo="text",  # // Display only the label and actual value on hover
                hole=0.5,
                marker=dict(colors=custom_colors),
            )
        ],
        layout=layout,
    )

    # Add Moksha score as center text
    fig.update_layout(
        title_text="# of Lives to Moksha <br>and Contributing Factors",
        annotations=[
            dict(
                text=f"<b>{moksha_score}</b><br>Lives to<br> Moksha",
                x=0.5,
                y=0.5,
                font_size=20,
                showarrow=False,
            ),
            dict(
                text=f"""\u002aBased on {assessment_percent_completion}% assessment completion.""",  # Footnote text
                x=0.5,  # Center horizontally
                y=-0.2,  # Position below the donut chart
                font_size=14,
                showarrow=False,
                # font=dict(color="black"),  # Adjust color based on your theme
                align="center",
            ),
        ],
    )
    return fig.to_json()
