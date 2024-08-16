import streamlit as st
from openai import OpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 
import streamlit_pills as stp
import time
import secrets_app
import functions
import file_functions as ff
import configs
import pandas as pd
import numpy

# Initialise session state to store conversation history locally to display on UI
def init():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    if "user_suggestion_pills" not in st.session_state:
        bucket_name = 'karmacoordinates'
        object_key = 'karma_coordinates_prompts.csv'
        st.session_state.user_suggestion_pills = ff.cache_csv_from_s3(bucket_name, object_key).iloc[1:, 0].to_list()

    if "query_queue" not in st.session_state:
        st.session_state.query_queue = []

    # Title
    st.subheader("Your AI Assistant")


def draw_user_input(user_query_container):
    ai_default_question = 'How can I help you?'
    with user_query_container:
        # draw user input box
        user_query = st.chat_input(ai_default_question)

        # draw pills
        # Textbox and either pill or typed query - add to FIFO
        if not st.session_state.user_suggestion_pills:
            # print(f'1')
            pass
        elif st.session_state.user_suggestion_pills:
            # print(f'2')
            user_suggestion_pills_label = "Let's get started:"
            user_selected_pill = stp.pills(user_suggestion_pills_label, st.session_state.user_suggestion_pills, clearable=True, index=None)

            if user_selected_pill and not (user_selected_pill == 'None') and not (user_selected_pill in st.session_state.query_history):
                # st.session_state.user_selected_pill = user_selected_pill
                st.session_state.query_queue.append(user_selected_pill)
                st.session_state.query_history.append(user_selected_pill)

            # return

        # print(f'3. user_query : {user_query}')
        # user_query = st.chat_input(ai_default_question)
        if (user_query is not None) and not (user_query in st.session_state.query_history):
            st.session_state.query_queue.append(user_query)
            st.session_state.query_history.append(user_query)

        # print(f'added query: {user_selected_pill}')
        # st.session_state.queue = list(set(st.session_state.queue)) # remove dups

# Display messages in chat history
def draw_chat_history():
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


def process_queue(client, assistant, process_prompt_container):
    # print(f'queue: {st.session_state.queue}')

    # Create a new thread if it does not exist
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    while st.session_state.query_queue and len(st.session_state.query_queue) > 0:
        # Wait until there is no active run
        while check_active_run(client, st.session_state.thread_id):
            time.sleep(1)  # Wait for 10 seconds before checking again      

        queued_user_query = st.session_state.query_queue.pop(0)
        # print(f'processing queued_user_query:{queued_user_query}')

        # Streaming process
        with process_prompt_container:
            process_prompt(client, assistant, queued_user_query)      


def prompt():
    _configs = configs.config()
    init()
    with st.container(border=True):
        # print(f'1. queue at start: {st.session_state.query_queue}')
        user_query_container = st.container()
        process_prompt_container = st.container() # placeholder to keep current response above history
        st.divider()
        draw_chat_history()        
        # print(f'2. queue after history: {st.session_state.query_queue}')
        draw_user_input(user_query_container=user_query_container)
        # process and write response in process_prompt_container
        # print(f'3. queue after user input: {st.session_state.query_queue}')
        process_queue(client=_configs['openai_client'], assistant=_configs['openai_assistant'], process_prompt_container=process_prompt_container)
    

