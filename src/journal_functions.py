import streamlit as st
import state_mgmt_functions as smf
import dynamodb_functions as db
import _utils

def _init():    
    if 'journal_entry' not in st.session_state.user_answers:
        st.session_state.user_answers['journal_entry'] = None

    if '_journal_entry' not in st.session_state:
        st.session_state['_journal_entry'] = {'value':None, 'status':None}

def journal_entry():
    _init()
    plh = st.empty()
    plh_msg = st.empty()
    with plh.container():
        entry = st.text_area("Journal entries are used in calculating your scores.", key="make_journal_entry", placeholder='What are your feelings/mood/thoughts today?', height=150)

    # print(f'entry is {entry} {st.session_state.make_journal_entry}')
    if entry:
        if not st.session_state['_journal_entry'] or not st.session_state._journal_entry['value'] == entry:
            st.session_state.user_answers.update({'journal_entry' : entry})
            st.session_state._journal_entry = {'value':entry, 'status':'New'}
            # print(f'journal entry is new')
            smf.save(plh_msg, 'Journal Entry')
        else:
            st.session_state._journal_entry['status'] = None


def is_new():
    _init()
    if st.session_state._journal_entry['status'] == 'New':
        return True

def previous_month_journal_entries():
    return db.query_by_sort_key_between(st.session_state._enter_email, *_utils.previous_month_timestamp())
    # print(f'items: {items_df['journal_entry']}')

def current_month_journal_entries():
    return db.query_by_sort_key_between(st.session_state._enter_email, *_utils.current_month_timestamp())
