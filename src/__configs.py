from openai import OpenAI, AsyncOpenAI
import security.secrets_app as secrets_app
from functools import lru_cache

class Configuration:
    def __init__(self, openai_client, openai_async_client, openai_assistant, stripe_api_key, 
                 smtp_server, smtp_port, smtp_username, smtp_password, sender_email,
                 jwt_secret, jwt_algorithm, pinpoint_application_id, pinpoint_region, boto3_region,
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
        self.pinpoint_application_id=pinpoint_application_id
        self.pinpoint_region=pinpoint_region
        self.boto3_region=boto3_region


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
        jwt_secret = secrets_app.get_value('JWT_SECRET')
        jwt_algorithm = secrets_app.get_value('JWT_ALGORITHM')
        pinpoint_application_id=secrets_app.get_value('PINPOINT_APPLICATION_ID')
        pinpoint_region=secrets_app.get_value('PINPOINT_REGION')
        boto3_region=secrets_app.get_value("BOTO3_REGION")


        return Configuration(openai_client=client, openai_async_client=async_client, openai_assistant=assistant, stripe_api_key=stripe_api_key,
                smtp_server=smtp_server, smtp_port=smtp_port, smtp_username=smtp_username, smtp_password=smtp_password, sender_email=sender_email,
                jwt_secret=jwt_secret, jwt_algorithm=jwt_algorithm, pinpoint_application_id=pinpoint_application_id, pinpoint_region=pinpoint_region, boto3_region=boto3_region)
    except Exception as e:
        print(f'error: {e}. Check if data exists!')
        return False

def main():
    cfg = get_config()
    print(f'sender_email: {cfg.sender_email}')

if __name__ == '__main__': main()
