import streamlit as st
from openai import OpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 
import streamlit_pills as stp
import time
import secrets_app
import functions
import configs

# from collections import deque 

user_suggestion_pills_label = "Let's get started:"
user_suggestion_pills = ['What is Karma Coordinates calculator app?', 'How does Karma Coordinates calculate a score?', 'What activities can I do at my age and in my city to improve my score?', 'What is Karma?', 'What is Sankhya?', 'What are Gunas?', 'What shloka explain sattva?', 'What are Sankhya shlokas on Purusha?']    
ai_default_question = 'How can I help you?'

# Initialise the OpenAI client, and retrieve the assistant
# @st.cache_resource
# def config():
#     client = OpenAI(api_key=secrets_app.cache_from_s3("OPENAI_API_KEY"))
#     assistant = client.beta.assistants.retrieve(assistant_id=secrets_app.cache_from_s3("ASSISTANT_ID"))
#     return client, assistant

def init():
    # Initialise session state to store conversation history locally to display on UI
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "user_suggestion_pills" not in st.session_state:
        st.session_state.user_suggestion_pills = user_suggestion_pills

    if "queue" not in st.session_state:
        st.session_state.queue = []

    # Title
    st.subheader("Your AI Assistant")


def draw_chat_ui():
    # 
    if not st.session_state.user_suggestion_pills:
        pass
    else:
        user_selected_pill = stp.pills(user_suggestion_pills_label, st.session_state.user_suggestion_pills, clearable=True, index=None)

        if user_selected_pill and user_selected_pill != 'None':
            st.session_state.user_selected_pill = user_selected_pill
        else:
            st.session_state.user_selected_pill = ''

    # Textbox and either pill or typed query - add to FIFO
    if st.session_state.user_selected_pill:
        st.chat_input(st.session_state.user_selected_pill)
        st.session_state.queue.append(st.session_state.user_selected_pill)
    else: 
        user_query = st.chat_input(ai_default_question)
        if user_query is not None:
            st.session_state.queue.append(user_query)


def draw_chat_history():
    # Display messages in chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    


# Function to check if there is an active run
def check_active_run(client, thread_id):
    try:
        # Fetch runs for the thread and check their status
        active_runs = client.beta.threads.runs.list(thread_id=thread_id)
        for run in active_runs.data:
            if run.status in ["in_progress", "queued"]:
                return True
        return False
    except OpenAIError as e:
        print(f"Failed to check runs: {str(e)}")
        return False



def process_prompt(client, assistant, user_query):    
    # Display the user's query
    with st.chat_message("user"):
        st.markdown(user_query)

    # Store the user's query into the history
    st.session_state.chat_history.append({"role": "user",
                                        "content": user_query})
    
    try:
        # Add user query to the thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_query
            )

        # Stream the assistant's reply
        with st.chat_message("assistant"):
            stream = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant.id,
                stream=True
                )
            
            # Empty container to display the assistant's reply
            assistant_reply_box = st.empty()
            assistant_reply_box.text("Retrieving...")
            
            # A blank string to store the assistant's reply
            assistant_reply = ""

            # Iterate through the stream 
            for event in stream:
                # There are various types of streaming events
                # See here: https://platform.openai.com/docs/api-reference/assistants-streaming/events

                # Here, we only consider if there's a delta text
                if isinstance(event, ThreadMessageDelta):
                    if isinstance(event.data.delta.content[0], TextDeltaBlock):
                        # empty the container
                        assistant_reply_box.empty()
                        # add the new text
                        assistant_reply += event.data.delta.content[0].text.value
                        # display the new text
                        assistant_reply_box.markdown(assistant_reply)
            
            # Once the stream is over, update chat history
            st.session_state.chat_history.append({"role": "assistant",
                                                "content": assistant_reply})
            
            if user_query in st.session_state.user_suggestion_pills:
                # print(f'removing pill:{user_query}')
                st.session_state.user_suggestion_pills.remove(user_query)

    except Exception as e:
        print(f'Failed to process_prompt {e}')


def process_queue(client, assistant):
    # print(f'queue: {st.session_state.queue}')

    # Create a new thread if it does not exist
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    while len(st.session_state.queue) > 0:
        # Wait until there is no active run
        while check_active_run(client, st.session_state.thread_id):
            time.sleep(1)  # Wait for 10 seconds before checking again      

        queued_user_query = st.session_state.queue.pop(0)

        # Streaming process
        process_prompt(client, assistant, queued_user_query)      


def prompt():
    _configs = configs.config()
    init()
    with st.container(border=True):
        draw_chat_ui()
        process_queue(client=_configs['openai_client'], assistant=_configs['openai_assistant'])
        draw_chat_history()
    

