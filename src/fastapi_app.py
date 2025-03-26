from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from api.ai_assist import cache_questionnaire, stream_ai_assist_reflect_response, clickable_progress_chart, stream_ai_assist_explore_response
import __configs, __utils, __constants
import storage.dynamodb_functions as db
import json
import secrets
import time
from storage.boto_functions import send_email
from pydantic import BaseModel
from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
import logging
from security.jwt_auth import create_access_token, JWTAuthBackend
from security.jwt_auth import cache
from pydantic import BaseModel, field_validator, ValidationError
from ip2geotools.databases.noncommercial import DbIpCity

temp_folder = '.tmp'
logging.basicConfig(filename=f'{temp_folder}/kc-app.log', filemode='w', level=logging.INFO)


class UserIdentifier(BaseModel):
    email: str
    phone: str | None = None


class JournalEntry(BaseModel):
    journal_entry: str


class Question(BaseModel):
    question: str | None = None


app = FastAPI()
app = FastAPI(middleware=[Middleware(AuthenticationMiddleware, backend=JWTAuthBackend())])
origins = [
    "http://localhost:8100",
    "https://localhost"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def hello():    
    return JSONResponse({"message":"Welcome to Karam Coordinates API"}, status_code=200)


@app.post("/get-token")
async def get_token(request: Request, user_id: UserIdentifier):
    token = secrets.token_hex(4)  
    auth_code = create_access_token(user_id.email, token, 1)
    b_email = send_email(user_id.email, token)
    if not b_email:
        return JSONResponse({"message": "Unable to send token"}, status_code=500)    
    return JSONResponse({"Authorization": auth_code}, status_code=200)    


@app.get("/validate-token/{token}")
async def validate_token(request: Request, token: str):
    if not request.user.is_authenticated or token != cache.get(request.user.display_name)['otp']:
        return JSONResponse({"message": "Failure"}, status_code=401)    
    
    expiration_timestamp = __utils.future_timestamp(90)
    user_answers = db.query(request.user.display_name, 'latest')
    client_ip_details =  __client_ip_details(request) 
    if client_ip_details:
        client_ip_details =  json.loads(__client_ip_details(request).to_json())

    if not user_answers or user_answers == '[]' or user_answers == 'null':
        user_answers = [{'date':str(time.time()), 
                         'auth_code' : cache.get(request.user.display_name)['auth_code'],
                         'expiration_date':str(expiration_timestamp), 
                         'email':request.user.display_name,
                         'client_ip_details':client_ip_details}]
    else:
        user_answers[0].update({'expiration_date':str(expiration_timestamp), 
                                'auth_code' : cache.get(request.user.display_name)['auth_code'],
                                'date':str(time.time()),
                                'client_ip_details':client_ip_details})    
    db.insert(user_activity_data=user_answers[0])
    return JSONResponse({"message": "Successful"}, status_code=200)    


@app.post("/journal-entry")
async def journal_entry(request: Request, journal_entry: JournalEntry):
    user_answers = await __user_latest_record(request)
    user_answers[0].pop('_journal_entry', None)
    user_answers[0].update({'journal_entry': journal_entry.journal_entry, 'date':str(time.time())})
    db.insert(user_activity_data=user_answers[0])
    return JSONResponse({"message": "Successful"}, status_code=200)    


@app.get("/ai-assist/reflect")
async def ai_assist(request: Request):
    user_answers = await __user_latest_record(request)
    journal_entry = user_answers[0].get('journal_entry')
    query = f'''Analyse impact of journal entry={journal_entry}'''
    features_df, categories_df, features_df_stats = cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
    ai_query = f'''Given the questionnaire={features_df.to_csv()} 
                    and the answers={user_answers[0]}, 
                    which answers get changed due to the new journal entry={journal_entry}?
                    Give impacted questions and changed answers (only from valid options of answers) as a dictionary.'''
    client=__configs.get_config().openai_client        
    assistant=__configs.get_config().openai_assistant
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=ai_query
    )
    return StreamingResponse(stream_ai_assist_reflect_response(request, user_answers, features_df, categories_df, features_df_stats, assistant.id, thread.id))    


@app.get("/ai-assist/journey")
async def ai_assist(request: Request):
    user_answers = await __user_latest_record(request)
    features_df, categories_df, features_df_stats = cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
    user_answers_rows = db.query(partition_key_value=request.user.display_name, sort_key_prefix=str(__utils.unix_epoc(months_ago=6))[:2], ascending=False)
    if not user_answers_rows or user_answers_rows == '[]' or user_answers_rows == 'null':
        user_answers_rows = [{'date':str(time.time()), 'email':request.user.display_name}]
    journal_entries = user_answers_rows[0]['journal_entry']
    client_ip_details = user_answers[0]['client_ip_details']
    query = f'''Suggest activities to improve Karma Coordinates score'''
    ai_query = f'''Given the questionnaire={features_df.to_csv()} 
                    and all answers={user_answers_rows[0]}, 
                    and geographic location={client_ip_details}
                    Suggest activities, events and volunteering opportunities with dates and locations to improve Karma Coordinates score.''' 
    client=__configs.get_config().openai_client        
    assistant=__configs.get_config().openai_assistant
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=ai_query
    )
    return StreamingResponse(stream_ai_assist_explore_response(request, features_df, categories_df, features_df_stats, assistant.id, thread.id))    


@app.get("/score/latest")
async def journal_entry(request: Request):
    user_answers = await __user_latest_record(request)
    assessment_score = user_answers[0].pop('assessment_score', None)
    lives_to_moksha = user_answers[0].pop('lives_to_moksha', None)
    assessment_percent_completion = int((len(user_answers[0])/__constants.NUMBER_OF_ASSESSMENT_QUESTIONS)*100)
    return JSONResponse(json.dumps({"assessment_score":assessment_score, 
                         "assessment_percent_completion":assessment_percent_completion, 
                         "lives_to_moksha":lives_to_moksha}, cls=__utils.DecimalEncoder).encode('ascii').decode('unicode-escape'), status_code=200)
    
    
@app.get("/plot/journey/json")
async def get_plot(request: Request):
    user_answers = await __user_latest_record(request)
    user_answers_rows = db.query(partition_key_value=request.user.display_name, sort_key_prefix=str(__utils.unix_epoc(months_ago=6))[:2], ascending=False)
    if not user_answers_rows or user_answers_rows == '[]' or user_answers_rows == 'null':
        user_answers_rows = [{'date':str(time.time()), 'email':request.user.display_name}]
    return HTMLResponse(clickable_progress_chart(json.dumps(user_answers_rows, cls=__utils.DecimalEncoder)))


@app.post("/ai-assist/explore")
async def ai_assist(request: Request, question: Question):
    user_answers = await __user_latest_record(request)
    features_df, categories_df, features_df_stats = cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
    query = f'''Analyse impact of all journal entry'''
    ai_query = f'''Given the questionnaire={features_df.to_csv()} 
                    and the thought={question}
                    provide an answer and/or an insight and/or a solution''' 
    client=__configs.get_config().openai_client        
    assistant=__configs.get_config().openai_assistant
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=ai_query
    )
    return StreamingResponse(stream_ai_assist_explore_response(request, features_df, categories_df, features_df_stats, assistant.id, thread.id))    


async def __user_latest_record(request: Request):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=401, detail="Failure")
    user_answers = db.query(request.user.display_name, 'latest')
    if not user_answers[0]['auth_code'] or user_answers[0]['auth_code'] != cache.get(request.user.display_name)['auth_code']:
        raise HTTPException(status_code=401, detail="Token Mismatch")
    return user_answers


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc):
        return JSONResponse(status_code=exc.status_code, content={"message": exc.detail},
    )


def __client_ip_details(request: Request):
    client_ip = request.headers.get("X-Forwarded-For") or request.client.host
    if client_ip:
        response = DbIpCity.get(client_ip, api_key='free')
    return response
