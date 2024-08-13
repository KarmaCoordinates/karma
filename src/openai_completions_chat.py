from openai import OpenAI
import streamlit as st
import streamlit_pills as pills

#st.title("ChatGPT-like clone")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# welcome_prompt = ''' The app's primary goal is to enhance the clarity of thinking in individuals, thus giving them the best chance of succeeding in various aspects of life. The calculated Karma Coordinates, specifically the number of lives to Moksha, serves as an incentive index to track and measure progress towards achieving mental clarity. By focusing on improving clarity of thinking and using the calculated coordinates as a metric for progress, individuals can potentially enhance their decision-making abilities, achieve personal growth, and increase their chances of success in different endeavors.'''
# user_suggestions = ['What is Karma?', 'What is Sankhya?']


def init():

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    selected = pills(welcome_prompt, user_suggestions, clearable=True, index=None,)

def prompt():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(selected):
        print(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})