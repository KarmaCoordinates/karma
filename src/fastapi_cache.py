import _utils
import storage.dynamodb_functions as db
import json
import time
from storage.boto_functions import send_email
from pydantic import BaseModel
from functools import lru_cache 
import logging

@lru_cache()
async def user_answers(user_id:str):
    if not user_id:
        return None
    user_answers = db.query(user_id, 'latest')
    if not user_answers or user_answers == '[]' or user_answers == 'null':
        user_answers = [{'date':str(time.time()), 'email':user_id}]
