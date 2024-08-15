import streamlit as st
import openai
from openai import OpenAI
# import stripe
import secrets_app

# Initialise the OpenAI client, and retrieve the assistant
@st.cache_resource
def config():
    client = OpenAI(api_key=secrets_app.cache_from_s3("OPENAI_API_KEY"))
    assistant = client.beta.assistants.retrieve(assistant_id=secrets_app.cache_from_s3("ASSISTANT_ID"))
    stripe_api_key = secrets_app.cache_from_s3("STRIPE_API_KEY")
    return {'openai_client':client, 'openai_assistant':assistant, 'stripe_api_key':stripe_api_key}
