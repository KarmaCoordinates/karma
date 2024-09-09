import streamlit as st
import state_mgmt_functions as smf
import dynamodb_functions as db
import _utils

def _init():    
    if 'user_answers' not in st.session_state:
        st.session_state['user_answers'] = {}

    if 'journal_entry' not in st.session_state:
        st.session_state.user_answers['journal_entry'] = ''


def journal_entry():
    _init()
    entry = st.text_area("Journal entries are used in calculating your scores.", key="make_journal_entry", placeholder='What are your feelings/mood/thoughts today?', height=150)
    if entry:
        st.session_state.user_answers.update({'journal_entry' : entry})
        smf.save()

def previous_month_journal_entries():
    return db.query_by_sort_key_between(st.session_state._enter_email, *_utils.previous_month_timestamp())
    # print(f'items: {items_df['journal_entry']}')
