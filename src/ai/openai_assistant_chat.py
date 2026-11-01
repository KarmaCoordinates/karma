import streamlit as st
from openai import OpenAIError
import time
import storage.s3_functions as s3f
import __configs
from ai_assist import assistant
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
    

def __process_prompt(client, user_query, random_key=generate_random_string()):    
    # print(f'random_key@user:{random_key}')
    # Display the user's query
    with st.chat_message("user"):
        st.markdown(user_query.query)
    
    # Store the user's query into the history
    st.session_state.chat_history.append({"role": "user",
                                        "content": user_query.query,
                                        "key":random_key})

    try:
        # Stream the assistant's reply, continuing the conversation so far
        with st.chat_message("assistant"):
            stream = client.responses.create(
                # The account tools need the API's handlers, so this chat only searches the knowledge base
                **{**assistant.response_args(user_query.ai_query, tools=[assistant.FILE_SEARCH_TOOL]), "store": True},
                previous_response_id=st.session_state.get("previous_response_id"),
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
                # See here: https://platform.openai.com/docs/api-reference/responses-streaming

                # Here, we only consider if there's a delta text
                if event.type == "response.output_text.delta":
                    # empty the container
                    assistant_reply_box.empty()
                    # add the new text
                    assistant_reply += event.delta
                    # display the new text
                    assistant_reply_box.markdown(assistant_reply)

                elif event.type == "response.completed":
                    st.session_state.previous_response_id = event.response.id

                # check for steps
            
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

def __process_queue(client, process_prompt_container):
    # print(f'queue: {st.session_state.queue}')

    try:
        while st.session_state.query_queue and len(st.session_state.query_queue) > 0:
            queued_user_query = st.session_state.query_queue.pop(0)
            # print(f'processing queued_user_query:{queued_user_query}')

            # Streaming process
            with process_prompt_container:
                __process_prompt(client, queued_user_query)      
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
        processing = __process_queue(client=__configs.get_config().openai_client, process_prompt_container=process_prompt_container)


def prompt_specific(query, ai_query, plh):
    if not __configs.get_config():
        return

    __init()

    cached_result = get_assistant_answer_from_cache(query)
    if not cached_result:
        st.session_state.query_queue.append(Query(query=query, ai_query=ai_query))
        processing = __process_queue(client=__configs.get_config().openai_client, process_prompt_container=plh)


def main():
    pass

if __name__ == '__main__': main()
