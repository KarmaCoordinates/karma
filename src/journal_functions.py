import streamlit as st
import state_mgmt_functions as smf

def _init():    
    if 'user_answers' not in st.session_state:
        st.session_state['user_answers'] = {}

    if 'journal_entry' not in st.session_state:
        st.session_state.user_answers['journal_entry'] = ''

def journal_entry():
    _init()
    entry = st.text_area("Journal entries are used in calculating your scores.", key="make_journal_entry", placeholder='What are your feelings/mood today?')
    if entry:
        st.session_state.user_answers.update({'journal_entry' : entry})
        smf.save()


