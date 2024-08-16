import streamlit as st

def init_buttons(button_list):
    if 'button_list' not in st.session_state:
        st.session_state.button_list = button_list
    return st.session_state.button_list

def remove_button(key):
    if 'button_list' in st.session_state:
        st.session_state.button_list.remove(key)

def render_buttons(on_click_callback):
    button_list = st.session_state.button_list

    if not button_list:
        return

    st.markdown("""
            <style>
                div[data-testid="column"] {
                    width: fit-content !important;
                    flex: unset;
                }
                div[data-testid="column"] * {
                    width: fit-content !important;
                }
            </style>
            """, unsafe_allow_html=True)    
    
    for text, col in list(map(list, zip(button_list, st.columns(len(button_list))))):
        with col:
            st.button(label=text, key=text, on_click=on_click_callback, args={text})
