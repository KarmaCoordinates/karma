from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from mangum import Mangum
import assessment.questionnaire_pratyay_sargah as qps
import numpy as np
import pandas as pd
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

@app.get("/")
async def hello():    
    return {"message":"Welcome to Karam Coordinates API"}


@app.post("/get-token")
async def get_token(request: Request, userId: UserIdentifier):
    token = secrets.token_hex(4)  
    request.session['_token'] = token
    request.session['_userId'] = userId.email
    b_email = send_email(userId.email, token)
    return f'{{"message":"{b_email}"}}'

@app.get("/validate-token/{token}")
async def validate_token(request: Request, token: str):
    b_valid = token == request.session.get('_token')
    if b_valid:
        request.session['userId'] = request.session.get('_userId')
        request.session['userAnswers'] = json.dumps(db.query(request.session.get('userId'), 'latest'), cls=_utils.DecimalEncoder)

        request.session['_token'] = None
        request.session['_userId'] = None
    return f'{{"message":"{b_valid}"}}'
    
@app.get("/session-info") 
async def session_info(request: Request):
    return f'{{"userId":"{request.session.get("userId")}"}}'

@app.get("/assessment-questionnaire")
async def assessment_questionnaire(request: Request):
    features_df, categories_df, features_df_stats = _cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
    return {features_df.to_json(orient="records")}

@app.get("/assessment-answers/latest")
async def assessment_questionnaire(request: Request):
    if request.session.get('userId'):
        userAnswers = json.loads(request.session.get('userAnswers'))
        userAnswers[0].pop('email', None)
        userAnswers[0].pop('_journal_entry', None)
        userAnswers[0].pop('journal_entry', None)
        userAnswers[0].pop('feedback', None)
        userAnswers[0].pop('rating', None)
        return json.dumps(userAnswers)
    else:
        return {}


@app.post("/journal-entry")
async def journal_entry(request: Request, journalEntry: JournalEntry):
    if request.session.get('userId'):
        userAnswers = json.loads(request.session.get('userAnswers'))
        userAnswers[0].pop('_journal_entry', None)
        userAnswers[0].update({'journal_entry': journalEntry.journal_entry, 'date':str(time.time())})
        db.insert(user_activity_data=userAnswers[0])
        request.session['userAnswers'] = json.dumps(db.query(request.session.get('userId'), 'latest'), cls=_utils.DecimalEncoder)
        # perform openAI analysis
        # asyncio.create_task(_ask_ai(request, journalEntry.journal_entry))        
        return {"message":f"{True}"}
    else: 
        return {"message":f'{False}'}

@app.get("/ai-assist")
async def ai_assist(request: Request):
    features_df, categories_df, features_df_stats = _cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')

    userAnswers = json.loads(request.session.get('userAnswers'))
    journal_entry = userAnswers[0].get('journal_entry')

    query = f'''Analyse impact of journal entry={journal_entry}'''
    ai_query = f'''Given the questionnaire={features_df.to_csv()} 
                    and the answers={json.dumps(userAnswers[0])}, 
                    which answers get changed due to the new journal entry={journal_entry}?
                    Give impacted questions and changed answers (only from valid options of answers) as a dictionary.'''

    # print(request.session.get('_assistantReply'))
    # print(userAnswers[0].get('journal_entry'))
    # ai_response = await _ask_ai(request, userAnswers[0].get('journal_entry'))    
    # return StreamingResponse(_ask_ai(request, userAnswers[0].get('journal_entry')))

    # make sure thread exist
    client=_configs.get_config().openai_client        
    assistant=_configs.get_config().openai_assistant
    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=ai_query
    )

    return StreamingResponse(stream_assistant_response(assistant.id, thread.id))    
    # return ai_response

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
    if request.session.get('userId'):
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


async def stream_assistant_response(assistant_id, thread_id):
    async_client=_configs.get_config().openai_async_client        

    stream = async_client.beta.threads.runs.stream(
        assistant_id=assistant_id,
        thread_id=thread_id
    )

    async with stream as stream:
        async for text in stream.text_deltas:
            # formatted_text = text.replace('\n', '\\n')
            yield f"{text}"
            # yield f"data: {text}\n\n"


async def _ask_ai(request: Request, ai_query: str):        
    client=_configs.get_config().openai_client        
    assistant=_configs.get_config().openai_assistant
    thread = client.beta.threads.create()

    try:
        # Add user query to the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=ai_query
            )

        stream = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            stream=True
            )
        
        # A blank string to store the assistant's reply
        assistant_reply = ''

        # Iterate through the stream 
        for event in stream:
            # There are various types of streaming events
            # See here: https://platform.openai.com/docs/api-reference/assistants-streaming/events

            # Here, we only consider if there's a delta text
            if isinstance(event, ThreadMessageDelta):
                if isinstance(event.data.delta.content[0], TextDeltaBlock):
                    # add the new text
                    assistant_reply += event.data.delta.content[0].text.value
        
        # Once the stream is over, return the reply
        return assistant_reply
        # print(request.session.get('_assistantReply'))
    
    except Exception as e:
        print(f'Failed to process_prompt {e}')

