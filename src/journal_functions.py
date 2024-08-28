import streamlit as st

def _init():    
    if 'user_answers' not in st.session_state:
        st.session_state['user_answers'] = {}

def journal_entry():
    _init()
    entry = st.text_area("Journal entries are used in calculating your scores.", key="make_journal_entry")
    if entry:
        st.session_state.user_answers.update({'journal_entry' : entry})
        

