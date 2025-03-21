from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from api.ai_assist import cache_questionnaire, stream_assistant_response, clickable_progress_chart, stream_ai_assist_explore_response
import _configs
import _utils
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
import cachetools
from datetime import datetime, timedelta


cache = cachetools.TTLCache(maxsize=1000, ttl=120)

temp_folder = '.tmp'
logging.basicConfig(filename=f'{temp_folder}/kc-app.log', filemode='w', level=logging.INFO)


class UserIdentifier(BaseModel):
    email: str
    phone: str | None = None


class JournalEntry(BaseModel):
    journal_entry: str


app = FastAPI()
app = FastAPI(middleware=[Middleware(AuthenticationMiddleware, backend=JWTAuthBackend())])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# json.dumps -> serialize; python object to JSON string; for e.g. before loading into db or storing in request.session
# json.loads -> deserialize; JSON string to python object; for e.g. after reading from db

@app.get("/")
async def hello():    
    return {"message":"Welcome to Karam Coordinates API"}


@app.post("/get-token")
async def get_token(request: Request, userId: UserIdentifier):
    token = secrets.token_hex(4)  
    auth_code = create_access_token(userId.email, token, 1)
    cache[userId.email]=token
    b_email = send_email(userId.email, token)
    if not b_email:
        return JSONResponse({"message": "Unable to send token"}, status_code=401)    
    return JSONResponse({"Authorization": auth_code}, status_code=200)    


@app.get("/validate-token/{token}")
async def validate_token(request: Request, token: str):

    if not request.user.is_authenticated or token != cache.get(request.user.display_name):
        return JSONResponse({"message": "Not authenticated"}, status_code=401)    
    
    current_datetime = datetime.fromtimestamp(time.time())
    days_to_add = 90
    expiration_datetime = current_datetime + timedelta(days=days_to_add)
    expiration_timestamp = expiration_datetime.timestamp()

    user_answers = db.query(request.user.display_name, 'latest')
    if not user_answers or user_answers == '[]' or user_answers == 'null':
        user_answers = [{'date':str(time.time()), 'expiration_date':str(expiration_timestamp), 'email':request.session['user_id']}]
    else:
        user_answers[0].update({'expiration_date':str(expiration_timestamp), 'date':str(time.time())})
    db.insert(user_activity_data=user_answers[0])

    return JSONResponse({"message": "Authenticated"}, status_code=200)    


@app.post("/journal-entry")
async def journal_entry(request: Request, journalEntry: JournalEntry):
    if not request.user.is_authenticated:
        return JSONResponse({"message": "Not authenticated"}, status_code=401)    

    user_answers = db.query(request.user.display_name, 'latest')
    # if expiration_date old throw error

    user_answers[0].pop('_journal_entry', None)
    user_answers[0].update({'journal_entry': journalEntry.journal_entry, 'date':str(time.time())})

    db.insert(user_activity_data=user_answers[0])

    return JSONResponse({"message": "Successful"}, status_code=200)    


@app.get("/ai-assist/reflect")
async def ai_assist(request: Request):
    if not request.user.is_authenticated:
        return JSONResponse({"message": "Not authenticated"}, status_code=401)    

    user_answers = db.query(request.user.display_name, 'latest')
    # if expiration_date old throw error

    journal_entry = user_answers[0].get('journal_entry')
    query = f'''Analyse impact of journal entry={journal_entry}'''
    features_df, categories_df, features_df_stats = cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
    ai_query = f'''Given the questionnaire={features_df.to_csv()} 
                    and the answers={user_answers[0]}, 
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
    if not request.user.is_authenticated:
        return JSONResponse({"message": "Not authenticated"}, status_code=401)    

    user_answers = db.query(request.user.display_name, 'latest')
    # if expiration_date old throw error

    features_df, categories_df, features_df_stats = cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')

    user_answers_rows = db.query(partition_key_value=request.user.display_name, sort_key_prefix=str(_utils.unix_epoc(months_ago=6))[:2], ascending=False)
    if not user_answers_rows or user_answers_rows == '[]' or user_answers_rows == 'null':
        user_answers_rows = [{'date':str(time.time()), 'email':request.session['user_id']}]
    # user_answers_rows = json.loads(json.dumps(user_answers_rows, cls=_utils.DecimalEncoder))

    journal_entries = user_answers_rows[0]['journal_entry']

    query = f'''Suggest activities to improve Karma Coordinates score'''
    ai_query = f'''Given the questionnaire={features_df.to_csv()} 
                    and all answers={user_answers_rows[0]}, 
                    Suggest activities, events and volunteering opportunities to improve Karma Coordinates score.''' 
                    # Give impacted questions and changed answers (only from valid options of answers) as a dictionary.'''

    client=_configs.get_config().openai_client        
    assistant=_configs.get_config().openai_assistant
    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=ai_query
    )
    return StreamingResponse(stream_assistant_response(request, features_df, categories_df, features_df_stats, assistant.id, thread.id))    


@app.get("/ai-assist/explore/{thought}")
async def ai_assist(request: Request, thought: str):
    if not request.user.is_authenticated:
        return JSONResponse({"message": "Not authenticated"}, status_code=401)    

    user_answers = db.query(request.user.display_name, 'latest')
    # if expiration_date old throw error

    features_df, categories_df, features_df_stats = cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')

    # user_answers_rows = db.query(partition_key_value=request.session.get('user_id'), sort_key_prefix=str(_utils.unix_epoc(months_ago=6))[:2], ascending=False)
    # if not user_answers_rows or user_answers_rows == '[]' or user_answers_rows == 'null':
    #     user_answers_rows = [{'date':str(time.time()), 'email':request.session['user_id']}]
    # user_answers_rows = json.loads(json.dumps(user_answers_rows, cls=_utils.DecimalEncoder))

    # user_answers = json.loads(request.session.get('user_answers'))
    # journal_entry = user_answers[0].get('journal_entry')
    # journal_entries = user_answers_rows[0]['journal_entry']

    query = f'''Analyse impact of all journal entry'''
    ai_query = f'''Given the questionnaire={features_df.to_csv()} 
                    and the thought={thought}
                    provide an answer and/or an insight and/or a solution''' 
                    # Give impacted questions and changed answers (only from valid options of answers) as a dictionary.'''

    client=_configs.get_config().openai_client        
    assistant=_configs.get_config().openai_assistant
    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=ai_query
    )
    return StreamingResponse(stream_ai_assist_explore_response(request, features_df, categories_df, features_df_stats, assistant.id, thread.id))    


@app.get("/score/latest")
async def journal_entry(request: Request):
    if not request.user.is_authenticated:
        return JSONResponse({"message": "Not authenticated"}, status_code=401)    

    user_answers = db.query(request.user.display_name, 'latest')
    # if expiration_date old throw error

    assessment_score = user_answers[0].pop('assessment_score', None)
    lives_to_moksha = user_answers[0].pop('lives_to_moksha', None)
    assessment_percent_completion = int((len(user_answers)/50)*100)

    return {'assessment_score':assessment_score, 'assessment_percent_completion':assessment_percent_completion, 'lives_to_moksha':{lives_to_moksha}}
    
    
@app.get("/plot/journey/html")
async def get_plot(request: Request):
    if not request.user.is_authenticated:
        return JSONResponse({"message": "Not authenticated"}, status_code=401)    

    user_answers = db.query(request.user.display_name, 'latest')
    # if expiration_date old throw error

    user_answers_rows = db.query(partition_key_value=request.user.display_name, sort_key_prefix=str(_utils.unix_epoc(months_ago=6))[:2], ascending=False)
    if not user_answers_rows or user_answers_rows == '[]' or user_answers_rows == 'null':
        user_answers_rows = [{'date':str(time.time()), 'email':request.session['user_id']}]

    return HTMLResponse(clickable_progress_chart(json.dumps(user_answers_rows, cls=_utils.DecimalEncoder)))
