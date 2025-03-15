import _utils, _configs
import assessment.score_functions as sf
import storage.dynamodb_functions as db
from fastapi import Request
from pandas import DataFrame
import pandas as pd
import ast
import json
import re
import time
import storage.s3_functions as s3f
import asyncio
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from io import StringIO



def cache_questionnaire(bucket_name, features_data_dict_object_key, categories_data_dict_object_key):
    features_df = s3f.cache_csv_from_s3(bucket_name=bucket_name, object_key=features_data_dict_object_key)
    key_value_columns = ['Option_1', 'Value_1', 'Option_2', 'Value_2', 'Option_3', 'Value_3', 'Option_4', 'Value_4']
    features_df['options_dict'] = [{ k: v for k, v in zip(row[::2], row[1::2]) if pd.notna(k) and pd.notna(v) } for row in features_df[key_value_columns].values]
    key_columns = ['Option_1', 'Option_2', 'Option_3', 'Option_4']
    features_df['options_list'] = [list(filter(pd.notna, item)) for item in zip(*features_df[key_columns].values.T)]
    categories_df = s3f.cache_csv_from_s3(bucket_name=bucket_name, object_key=categories_data_dict_object_key)

    value_columns = features_df[['Value_1', 'Value_2', 'Value_3', 'Value_4']]
    minimum_score = value_columns.min(axis=1).sum()
    maximum_score = value_columns.max(axis=1).sum()

    return features_df, categories_df, {'minimum_score':minimum_score, 'maximum_score':maximum_score, 'number_of_questions':len(features_df)}


def __score_summary(category_score):
    clarity_of_thinking_index = sum(category_score.values())
    clarity_of_thinking_index_dict = {'clarity_of_thinking_index':str(sum(category_score.values()))}
    category_score_str = ''
    category_score_dict = {}
    for category, score in category_score.items():
        category_score_str = category_score_str + f'''{category}:{round(score, 1)}, '''
        category_score_dict.update({category:str(round(score, 1))})

    # score_md is for backward-compatibility
    score_md = f'''Your **Clarity of Thinking** score: **{clarity_of_thinking_index}** [{category_score_str}] '''

    category_score_array = [ {'category' : k, 'score' : category_score_dict[k]} for k in category_score_dict]

    return score_md, {'assessment_score':category_score_array}, clarity_of_thinking_index_dict


def __calc_category_score(features_df, categories_df, user_answers):
    category_score={}
    for category_tpl in categories_df.itertuples():
        category_score[category_tpl.category_name] = 0
        for feature_tpl in features_df.loc[features_df['Category'] == category_tpl.category_name].itertuples():
            default_index = 0
            default_selected_option = None
            if feature_tpl.Question in user_answers:
                default_selected_option = user_answers[feature_tpl.Question]
            else:
                default_selected_option = feature_tpl.options_list[default_index]

            # st.session_state.user_answers.update({feature_tpl.Question:default_selected_option})
            selected_option_score = feature_tpl.options_dict.get(default_selected_option)

            if selected_option_score:
                category_score[category_tpl.category_name] += selected_option_score

    return category_score


async def __update_ai_assessment(request: Request, features_df: DataFrame, categories_df: DataFrame, features_df_stats, analysis):
    ai_assessment = {}
    rx = r'(\{[^{}]+\})'
    matches = re.findall(rx, analysis)
    if matches and len(matches) > 0:
        updated_dict = ast.literal_eval(matches[0])
        for q in updated_dict.keys():
            matched_question = features_df.loc[features_df['Question'] == q]
            if len(matched_question) == 1:
                ai_answer = updated_dict.get(q)

                if any(answer_option.startswith(ai_answer) for answer_option in matched_question.get('options_list').values[0]):
                    ai_assessment.update({q:ai_answer})


        if (ai_assessment):
            user_answers = json.loads(request.session.get('user_answers'))
            user_answers[0].update(ai_assessment)
            user_answers[0].update({'date':str(time.time())})

            category_score = __calc_category_score(features_df, categories_df, user_answers[0])
            score_md, assessment_score_dict, clarity_of_thinking_index_dict = __score_summary(category_score)
            lives_to_moksha = sf.calculate_karma_coordinates(category_score, features_df_stats)

            user_answers[0].update({'score_ai_analysis_query':score_md, 'lives_to_moksha':lives_to_moksha})

            user_answers[0].update(assessment_score_dict)
            user_answers[0].update(clarity_of_thinking_index_dict)

            db.insert(user_activity_data=user_answers[0])

            request.session['user_answers'] = json.dumps(user_answers, cls=_utils.DecimalEncoder)


async def stream_assistant_response(request: Request, features_df: DataFrame, categories_df: DataFrame, features_df_stats, assistant_id, thread_id):
    async_client=_configs.get_config().openai_async_client

    stream = async_client.beta.threads.runs.stream(
        assistant_id=assistant_id,
        thread_id=thread_id
    )

    complete_text = ''
    async with stream as stream:
        async for text in stream.text_deltas:
            # formatted_text = text.replace('\n', '\\n')
            complete_text += text
            yield f"{text}"
            # yield f"data: {text}\n\n"

    asyncio.create_task(__update_ai_assessment(request, features_df, categories_df, features_df_stats, complete_text))


def clickable_progress_chart(rows: str):
    if rows is None:
        return
    
    json_file = StringIO(rows)
    df = pd.read_json(json_file)

    df = df[[db.Columns().date, db.Columns().lives_to_moksha, db.Columns().journal_entry]].dropna()
    # df['Timeline'] = df['date'].astype(float).dt.strftime('%m/%d/%Y %H:%M')    
    # df['Timeline'] = pd.to_datetime(pd.to_numeric(df['date'], errors='coerce'), unit='s', )
    df['Timeline'] = pd.to_datetime(df['date'])
    df['Journal'] = df[db.Columns().journal_entry].apply(lambda x: _utils.insert_line_breaks(x))

    fig = px.scatter(df, x='Timeline', y=db.Columns().lives_to_moksha, 
            labels={
                "lives_to_moksha": "Lives to Moksha"},
            title="My progress", 
            hover_data=df[['Journal']], trendline="ols")

    fig = go.Figure(data=[go.Scatter(x=df['Timeline'], y=df[db.Columns().lives_to_moksha], 
                                     text=df[db.Columns().journal_entry].str.slice(0, 50),
                                     mode='lines+markers',
                                     line=dict(color='green'),
                                     hovertemplate="<b>%{text}</b>")])

    fig.update_layout({
        'title_text':"My progress<br><sup>on path to Moksha</sup>",
        'plot_bgcolor':'lightgrey',
        'hoverlabel.align':'left',
        'xaxis_title':'Timeline',
        'yaxis_title':'Lives to Moksha'}
    )    
    # fig.data[1].line.color = 'gold'
    return pio.to_html(fig, full_html=False)
