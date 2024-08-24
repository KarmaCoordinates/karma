import streamlit as st
import openai
from openai import OpenAI
# import stripe
import secrets_app

class Configuration:
    def __init__(self, openai_client, openai_assistant, stripe_api_key, smtp_server, smtp_port, smtp_username, smtp_password, sender_email):
        self.openai_client = openai_client
        self.openai_assistant = openai_assistant
        self.stripe_api_key = stripe_api_key
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.sender_email = sender_email

# Initialise the OpenAI client, and retrieve the assistant
@st.cache_resource
def get_config():
    try:
        client = OpenAI(api_key=secrets_app.get_value("OPENAI_API_KEY"))
        assistant = client.beta.assistants.retrieve(assistant_id=secrets_app.get_value("ASSISTANT_ID"))
        stripe_api_key = secrets_app.get_value("STRIPE_API_KEY")
        smtp_server = secrets_app.get_value('SMTP_SERVER')
        smtp_port = secrets_app.get_value('SMTP_PORT')
        smtp_username = secrets_app.get_value('SMTP_USERNAME')
        smtp_password = secrets_app.get_value('SMTP_PASSWORD')
        sender_email = secrets_app.get_value('SENDER_EMAIL')

        return Configuration(openai_client=client, openai_assistant=assistant, stripe_api_key=stripe_api_key,
                smtp_server=smtp_server, smtp_port=smtp_port, smtp_username=smtp_username, smtp_password=smtp_password, sender_email=sender_email )
    except Exception as e:
        print(f'error: {e}. Check if data exists!')
        return False

def main():
    _config = get_config()
    print(f'sender_email: {_config.sender_email}')

if __name__ == '__main__': main()
