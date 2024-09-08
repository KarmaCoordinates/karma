import streamlit as st
import pandas as pd
import dynamodb_functions as df

class SessionVariables:
    def __init__(self):
        self._enter_email = '_enter_email'

        # if not '_enter_email' in st.session_state:
        #     st.session_state['_enter_email'] = None


def init():
    if 'auth' not in st.session_state:
        st.session_state['auth'] = False

    if 'user_answers' not in st.session_state:
        st.session_state['user_answers'] = {}

    if 'journal_entry' not in st.session_state.user_answers:
        st.session_state.user_answers['journal_entry'] = ''

    if 'score_ai_analysis_query' not in st.session_state.user_answers:
        st.session_state.user_answers['score_ai_analysis_query'] = None

    if 'lives_to_moksha' not in st.session_state.user_answers:
        st.session_state.user_answers['lives_to_moksha'] = None



def is_set(str):
    return st.session_state[str]

def get_session_vars():
    return SessionVariables()

# page_init = False
# statuses = ("page_init", "page_loaded")
# only act on one key at a time
# don't do anything during first page loading
# once page is loaded, reset the key remembered in session.loading
def update_ui_status(key, value=None):
    # st.markdown(f'update_ui_status: {key}')
    if key == "page_init":
        if not 'loading' in st.session_state: 
            # print(f'page_init')
            st.session_state['loading'] = None
        st.session_state['loading'] == "page_init" 
    elif key == "page_loaded":
        if 'loading' in st.session_state: 
            del st.session_state['loading'] 
    else: 
        if not 'loading' in st.session_state or st.session_state.loading is None: 
            # print(f'key_init')
            st.session_state['loading'] = None
        st.session_state['loading'] = key


def is_loading(key_startswith_str = None):
    # print(f'key_startswith_str: {key_startswith_str}')
    if key_startswith_str is None:
        return 'loading' in st.session_state
    else:
        # print(f'is_loading: {st.session_state.loading}, key_startswith_str: {key_startswith_str}')
        return 'loading' in st.session_state and not st.session_state.loading is None and st.session_state.loading.startswith(key_startswith_str)
    
def save(placeholder=None, msg='activity'):
    if st.session_state.auth:
        try:
            df.insert(user_activity_data=st.session_state.user_answers)
            if placeholder:
                placeholder.success(f'''Your {msg} is saved.''')
        except Exception as e:
            if placeholder:
                placeholder.error(f'''Error{e} saving {msg}.''')

        return True

def main():
    pass

if __name__ == '__main__': main()
