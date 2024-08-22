import streamlit as st

page_init = False
# only act on one key at a time
# don't do anything during first page loading
# once page is loaded, reset the key remembered in session.loading
def update_ui_status(key, value):
    if key == 'loading':
        if value == 'Complete':
            if 'loading' in st.session_state: 
                del st.session_state['loading'] 
        else:
            return
    else: 
        global page_init
        if page_init:
            if 'loading' not in st.session_state:  
                st.session_state['loading'] = key
        else:
            page_init = True

def page_init():
    global page_init
    return page_init

def is_loading(key_startswith_str):
    return 'loading' in st.session_state and st.session_state.loading.startswith('key_startswith_str')