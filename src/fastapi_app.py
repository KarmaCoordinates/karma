from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from api.ai_assist import cache_questionnaire, stream_assistant_response, clickable_progress_chart
import _configs
import _utils
import storage.dynamodb_functions as db
# import streamlit_functions.state_mgmt_functions as smf
import json
import secrets
import time
from storage.boto_functions import send_email
from pydantic import BaseModel
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware


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
    features_df, categories_df, features_df_stats = cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
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
    features_df, categories_df, features_df_stats = cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')

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
    features_df, categories_df, features_df_stats = cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')

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
        lives_to_moksha = user_answers[0].pop('lives_to_moksha', None)

        return {'assessment_score':assessment_score, 'lives_to_moksha':{lives_to_moksha}}
    else: 
        return {"message":f'{False}'}
    
@app.get("/plot/journey/html")
async def get_plot(request: Request):
    user_answers_rows = db.query(partition_key_value=request.session.get('user_id'))
    if not user_answers_rows or user_answers_rows == '[]' or user_answers_rows == 'null':
        user_answers_rows = [{'date':str(time.time()), 'email':request.session['user_id']}]
    user_answers_rows = json.dumps(user_answers_rows, cls=_utils.DecimalEncoder)   
    # print(f'user_answers_rows: {user_answers_rows}, {type(user_answers_rows)}')    
    return HTMLResponse(clickable_progress_chart(user_answers_rows))
#
# [{question1:answer1,...,date:today}}
@app.post("/assessment-answers")
async def questionnaire_answers(request: Request):
    # receive: [{questions: answers}]
    if request.session.get('user_id'):
        pass
    return {"status":"assessment_answers implementation is in progress"}
