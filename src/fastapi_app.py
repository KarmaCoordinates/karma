from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from mangum import Mangum
import assessment.questionnaire_pratyay_sargah as qps
import numpy as np
import pandas as pd
from pandas import DataFrame
import storage.s3_functions as s3f
import assessment.score_functions as sf
import _configs
import _utils
import random
import storage.dynamodb_functions as db
# import streamlit_functions.state_mgmt_functions as smf
import ai.openai_assistant_chat as oac
import re
import ast
import journal.journal_functions as jf
import json
import secrets
import time
from storage.boto_functions import send_email, sms_token
from pydantic import BaseModel
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from openai import OpenAI, AsyncOpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 
import asyncio


class UserIdentifier(BaseModel):
    email: str
    phone: str | None = None

class JournalEntry(BaseModel):
    journal_entry: str


app = FastAPI()
app = FastAPI(middleware=[Middleware(SessionMiddleware, secret_key="kc-0001-001")])


# json.dumps -> python object to JSON string; before loading into db for e.g.
# json.loads -> JSON string to python object; after reading from db for e.g.

@app.get("/")
async def hello():    
    return {"message":"Welcome to Karam Coordinates API"}


@app.post("/get-token")
async def get_token(request: Request, userId: UserIdentifier):
    token = secrets.token_hex(4)  
    request.session['_token'] = token
    request.session['_user_id'] = userId.email
    b_email = send_email(userId.email, token)
    return f'{{"message":"{b_email}"}}'

@app.get("/validate-token/{token}")
async def validate_token(request: Request, token: str):
    b_valid = token == request.session.get('_token')

    if b_valid:
        request.session['user_id'] = request.session.get('_user_id')

        user_answers = db.query(request.session.get('user_id'), 'latest')
        if not user_answers or user_answers == '[]' or user_answers == 'null':
            user_answers = [{'date':str(time.time()), 'email':request.session['user_id']}]

        request.session['user_answers'] = json.dumps(user_answers, cls=_utils.DecimalEncoder)

        request.session['_token'] = None
        request.session['_user_id'] = None

    return f'{{"message":"{b_valid}"}}'
    
@app.get("/session-info") 
async def session_info(request: Request):
    return f'{{"user_id":"{request.session.get("user_id")}"}}'

@app.get("/assessment-questionnaire", deprecated=True)
async def assessment_questionnaire(request: Request):
    features_df, categories_df, features_df_stats = _cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
    return {features_df.to_json(orient="records")}

@app.get("/assessment-answers/latest",  deprecated=True)
async def assessment_questionnaire(request: Request):
    if request.session.get('user_id'):
        user_answers = json.loads(request.session.get('user_answers'))
        user_answers[0].pop('email', None)
        user_answers[0].pop('_journal_entry', None)
        user_answers[0].pop('journal_entry', None)
        user_answers[0].pop('feedback', None)
        user_answers[0].pop('rating', None)
        return json.dumps(user_answers)
    else:
        return {}

@app.get("/assessment-answers/latest",  deprecated=True)
async def assessment_questionnaire(request: Request):
    if request.session.get('user_id'):
        user_answers = json.loads(request.session.get('user_answers'))
        user_answers[0].pop('email', None)
        user_answers[0].pop('_journal_entry', None)
        user_answers[0].pop('journal_entry', None)
        user_answers[0].pop('feedback', None)
        user_answers[0].pop('rating', None)
        return json.dumps(user_answers)
    else:
        return {}


@app.post("/journal-entry")
async def journal_entry(request: Request, journalEntry: JournalEntry):
    if request.session.get('user_id'):
        user_answers = json.loads(request.session.get('user_answers'))
        user_answers[0].pop('_journal_entry', None)
        user_answers[0].update({'journal_entry': journalEntry.journal_entry, 'date':str(time.time())})

        db.insert(user_activity_data=user_answers[0])
        request.session['user_answers'] = json.dumps(db.query(request.session.get('user_id'), 'latest'), cls=_utils.DecimalEncoder)

        return {"message":f"{True}"}
    else: 
        return {"message":f'{False}'}

@app.get("/ai-assist/reflect")
async def ai_assist(request: Request):
    features_df, categories_df, features_df_stats = _cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')

    user_answers = json.loads(request.session.get('user_answers'))
    journal_entry = user_answers[0].get('journal_entry')

    query = f'''Analyse impact of journal entry={journal_entry}'''
    ai_query = f'''Given the questionnaire={features_df.to_csv()} 
                    and the answers={json.dumps(user_answers[0])}, 
                    which answers get changed due to the new journal entry={journal_entry}?
                    Give impacted questions and changed answers (only from valid options of answers) as a dictionary.'''

    client=_configs.get_config().openai_client        
    assistant=_configs.get_config().openai_assistant
    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=ai_query
    )

    return StreamingResponse(stream_assistant_response(request, features_df, categories_df, features_df_stats, assistant.id, thread.id))    

@app.get("/ai-assist/journey")
async def ai_assist(request: Request):
    features_df, categories_df, features_df_stats = _cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')

    user_answers = json.loads(request.session.get('user_answers'))
    journal_entry = user_answers[0].get('journal_entry')

    query = f'''Analyse impact of journal entry={journal_entry}'''
    ai_query = f'''Given the questionnaire={features_df.to_csv()} 
                    and the answers={json.dumps(user_answers[0])}, 
                    and the journal entry={journal_entry},
                    what local (determine region based on IP Address) volunteering opportunities, local activities, local physical and mental well-being options, local events I can participate in? 
                    Give impacted questions and changed answers (only from valid options of answers) as a dictionary.'''

    client=_configs.get_config().openai_client        
    assistant=_configs.get_config().openai_assistant
    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=ai_query
    )

    return StreamingResponse(stream_assistant_response(request, features_df, categories_df, features_df_stats, assistant.id, thread.id))    


@app.get("/score/latest")
async def journal_entry(request: Request):
    if request.session.get('user_id'):
        # user_answers = json.loads(request.session.get('user_answers'))
        request.session['user_answers'] = json.dumps(db.query(request.session.get('user_id'), 'latest'), cls=_utils.DecimalEncoder)

        user_answers = json.loads(request.session.get('user_answers'))
        # print(f'user_answers:{user_answers}')
        assessment_score = user_answers[0].pop('assessment_score', None)
        clarity_of_thinking_index = user_answers[0].pop('clarity_of_thinking_index', None)

        return {'assessment_score':assessment_score, 'clarity_of_thinking_index':{clarity_of_thinking_index}}
    else: 
        return {"message":f'{False}'}

#
# [{question1:answer1,...,date:today}}
@app.post("/assessment-answers")
async def questionnaire_answers(request: Request):
    # receive: [{questions: answers}]
    # calculate score
    # if user context is established then 
    # save/update the assessment
    # else 
    # do not save the assessment
    if request.session.get('user_id'):
        pass

    # show the score and graphs

    return {"status":"assessment_answers implementation is in progress"}


def _cache_questionnaire(bucket_name, features_data_dict_object_key, categories_data_dict_object_key):
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


def _score_summary(category_score):
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
    # return score_md, category_score_dict, clarity_of_thinking_index_dict

def _calc_category_score(features_df, categories_df, user_answers):
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


async def _update_ai_assessment(request: Request, features_df: DataFrame, categories_df: DataFrame, features_df_stats, analysis):
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

            category_score = _calc_category_score(features_df, categories_df, user_answers[0])
            score_md, category_score_dict, clarity_of_thinking_index_dict = _score_summary(category_score)
            lives_to_moksha = sf.calculate_karma_coordinates(category_score, features_df_stats)

            user_answers[0].update({'score_ai_analysis_query':score_md, 'lives_to_moksha':lives_to_moksha})  

            user_answers[0].update(category_score_dict)
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

    asyncio.create_task(_update_ai_assessment(request, features_df, categories_df, features_df_stats, complete_text))


async def stream_assistant_journey_response(request: Request, features_df: DataFrame, categories_df: DataFrame, features_df_stats, assistant_id, thread_id):
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
