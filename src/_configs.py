import streamlit as st
import openai
from openai import OpenAI, AsyncOpenAI
import security.secrets_app as secrets_app
from functools import lru_cache

class Configuration:
    def __init__(self, openai_client, openai_async_client, openai_assistant, stripe_api_key, 
                 smtp_server, smtp_port, smtp_username, smtp_password, sender_email,
                 jwt_secret, jwt_algorithm,
                 minimum_assessment_completion_percent=50):
        self.openai_client = openai_client
        self.openai_async_client = openai_async_client
        self.openai_assistant = openai_assistant
        self.stripe_api_key = stripe_api_key
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.sender_email = sender_email
        self.jwt_secret=jwt_secret
        self.jwt_algorithm=jwt_algorithm
        self.minimum_assessment_completion_percent = minimum_assessment_completion_percent


# Initialise the OpenAI client, and retrieve the assistant
# @st.cache_resource
@lru_cache
def get_config():
    try:
        client = OpenAI(api_key=secrets_app.get_value("OPENAI_API_KEY"))
        async_client = AsyncOpenAI(api_key=secrets_app.get_value("OPENAI_API_KEY"))
        assistant = client.beta.assistants.retrieve(assistant_id=secrets_app.get_value("ASSISTANT_ID"))
        stripe_api_key = secrets_app.get_value("STRIPE_API_KEY")
        smtp_server = secrets_app.get_value('SMTP_SERVER')
        smtp_port = secrets_app.get_value('SMTP_PORT')
        smtp_username = secrets_app.get_value('SMTP_USERNAME')
        smtp_password = secrets_app.get_value('SMTP_PASSWORD')
        sender_email = secrets_app.get_value('SENDER_EMAIL')
        #TODO move to secret file
        jwt_secret='kc-0001-001'
        jwt_algorithm='HS256'


        return Configuration(openai_client=client, openai_async_client=async_client, openai_assistant=assistant, stripe_api_key=stripe_api_key,
                smtp_server=smtp_server, smtp_port=smtp_port, smtp_username=smtp_username, smtp_password=smtp_password, sender_email=sender_email,
                jwt_secret=jwt_secret, jwt_algorithm=jwt_algorithm)
    except Exception as e:
        print(f'error: {e}. Check if data exists!')
        return False

def main():
    cfg = get_config()
    print(f'sender_email: {cfg.sender_email}')

if __name__ == '__main__': main()
