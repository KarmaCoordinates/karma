from fastapi import FastAPI, Request
from mangum import Mangum
import assessment.questionnaire_pratyay_sargah as qps
import numpy as np
import pandas as pd
import storage.s3_functions as s3f
import assessment.score_functions as sf
import _configs
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
from starlette.middleware.sessions import SessionMiddleware


class UserIdentifier(BaseModel):
    email: str
    phone: str | None = None


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
# handler = Mangum(app)

@app.get("/")
async def hello():    
    return {"message": "Welcome to Karam Coordinates API"}


@app.post("/send_token")
async def send_token(request: Request, userId: UserIdentifier):
    token = secrets.token_hex(4)  
    request.session['_token'] = token
    request.session['_userId'] = userId.email
    print(f"token:{token}, _token: {request.session.get('_token')}")
    b_email = send_email(userId.email, token)
    return {"status": b_email}

@app.post("/validate_token/{token}")
async def validate_token(request: Request, token: str):
    print(f"token:{token}, _token: {request.session.get('_token')}")
    b_valid = token == request.session.get('_token')
    if b_valid:
        request.session['userId'] = request.session.get('_userId')
    return {"status": b_valid}
    
   
@app.post("/login")
async def login():
    # send token
    # if successful, establish session/context for logged in user
    return {"status": "login implementation is in progress"}

@app.get("/assessment_questionnaire")
async def assessment_questionnaire():
    # if user context is established then
    # qps.retrieve_previous_assessment()    
    features_df, categories_df, features_df_stats = _cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
    return {features_df.to_json(orient="records")}


#
# | category | question | answer_option |
@app.post("/assessment_answers")
async def questionnaire_answers():
    # calculate score
    # if user context is established then 
    # save/update the assessment
    # else 
    # do not save the assessment

    # show the score and graphs

    return {"status": "assessment_answers implementation is in progress"}

@app.post("/journal_entry")
async def journal_entry():
    return {"status": "journal_entry implementation is in progress"}



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
