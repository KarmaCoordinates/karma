import storage.dynamodb_functions as db
import time
from functools import lru_cache 
import logging

@lru_cache()
async def user_answers(user_id:str):
    if not user_id:
        return None
    user_answers = db.query(user_id, 'latest')
    if not user_answers or user_answers == '[]' or user_answers == 'null':
        user_answers = [{'date':str(time.time()), 'email':user_id}]
