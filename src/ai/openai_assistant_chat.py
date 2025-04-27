import streamlit as st
from openai import OpenAIError
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 
import time
import storage.s3_functions as s3f
import __configs
import pandas as pd
import streamlit_functions.streamlit_button_list as ifunc
import random
import string
import unicodedata
from prompts.prompt_engine import popular_questions

class Query:
    def __init__(self, query, ai_query=None, status=None):
        self.query=query
        if ai_query:
            self.ai_query=ai_query
        else:
            self.ai_query=query
        self.status = status

# Initialise session state to store conversation history locally to display on UI
def __init():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    if "query_queue" not in st.session_state:
        st.session_state.query_queue = []

def generate_random_string(length=8):
    # Create a pool of characters: lowercase + uppercase + digits
    characters = string.ascii_letters + string.digits
    # Generate a random string
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def normalize_text(text):
    """Normalize text to NFC format."""
    return unicodedata.normalize('NFC', text)


def __callback_button_on_click(key):
    st.session_state.query_queue.append(Query(query=key))
    st.session_state.query_history.append(Query(query=key))

def __render_user_input(user_query_container):
    ai_default_question = 'How can I help you?'
    with user_query_container:

        # show suggested options (if auth=false)
        # if not st.session_state.auth:
        st.markdown('FAQs')
        ifunc.render_buttons(button_list=[item for item in popular_questions().get("popular_questions") if item not in st.session_state.query_history], on_click_callback=__callback_button_on_click)

        # draw user input box
        user_query = st.chat_input(ai_default_question)        
        if (user_query is not None) and not (user_query in st.session_state.query_history):
            st.session_state.query_queue.append(Query(query=user_query))
            st.session_state.query_history.append(Query(query=user_query))


# Display messages in chat history
def __render_chat_history():
    show_history = st.toggle('Show history')
    # st.markdown('History')
    if show_history:
        for message in (st.session_state.chat_history):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    

# Function to check if there is an active run
def __check_active_run(client, thread_id):
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


def __process_prompt(client, assistant, user_query, random_key=generate_random_string()):    
    # print(f'random_key@user:{random_key}')
    # Display the user's query
    with st.chat_message("user"):
        st.markdown(user_query.query)
    
    # Store the user's query into the history
    st.session_state.chat_history.append({"role": "user",
                                        "content": user_query.query,
                                        "key":random_key})

    try:
        # Add user query to the thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_query.ai_query
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
            # print(f'random_key@assistant:{random_key}')
            st.session_state.chat_history.append({"role": "assistant",
                                                "content": assistant_reply,
                                                "key": random_key})
            
            # if user_query in st.session_state.button_list:
            #     # print(f'removing pill:{user_query}')
            #     st.session_state.button_list.remove(user_query)

        # return random_key
    
    except Exception as e:
        print(f'Failed to process_prompt {e}')

def __process_queue(client, assistant, process_prompt_container):
    # print(f'queue: {st.session_state.queue}')

    try:
        # Create a new thread if it does not exist
        if "thread_id" not in st.session_state:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id

        while st.session_state.query_queue and len(st.session_state.query_queue) > 0:
            # Wait until there is no active run
            while __check_active_run(client, st.session_state.thread_id):
                time.sleep(1)  # Wait for 10 seconds before checking again      

            queued_user_query = st.session_state.query_queue.pop(0)
            # print(f'processing queued_user_query:{queued_user_query}')

            # Streaming process
            with process_prompt_container:
                __process_prompt(client, assistant, queued_user_query)      
    except:
        with process_prompt_container:
            st.markdown('Unable to connect.')
        return False

def get_assistant_answer_from_cache(content):
    df = pd.DataFrame(st.session_state.chat_history, columns=['role', 'content', 'key'])
    df['normalized_content'] = df['content'].apply(normalize_text)
    try:
        key = df.loc[df['normalized_content'] == normalize_text(content), 'key'].values[0]
        return df.loc[(df['key'] == key) & (df['role'] == 'assistant'), 'content'].values[0]
    except:
        # print(f'ai analysis query={content} not found in cache.')
        pass

def prompt():
    if not __configs.get_config():
        return
    
    __init()
    st.subheader("Your AI Assistant")
    with st.container(border=True):
        user_query_container = st.container()
        process_prompt_container = st.container() # placeholder to keep current response above history

        if len(st.session_state.chat_history) > 0:
            st.divider()
            __render_chat_history()        
        __render_user_input(user_query_container=user_query_container)
        processing = __process_queue(client=__configs.get_config().openai_client, assistant=__configs.get_config().openai_assistant, process_prompt_container=process_prompt_container)


def prompt_specific(query, ai_query, plh):
    if not __configs.get_config():
        return

    __init()

    cached_result = get_assistant_answer_from_cache(query)
    if not cached_result:
        st.session_state.query_queue.append(Query(query=query, ai_query=ai_query))
        processing = __process_queue(client=__configs.get_config().openai_client, assistant=__configs.get_config().openai_assistant, process_prompt_container=plh)


def main():
    pass

if __name__ == '__main__': main()
