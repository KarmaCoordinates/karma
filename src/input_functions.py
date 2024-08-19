import streamlit as st

def init_buttons(button_list, button_list_name):
    if button_list_name and button_list_name not in st.session_state:
        st.session_state[button_list_name] = button_list
    return st.session_state[button_list_name]

def render_buttons(on_click_callback, button_list_name):
    if not button_list_name or button_list_name not in st.session_state:
        return

    button_list = st.session_state[button_list_name]

    if not button_list:
        return

    st.markdown("""
        <style>
            div[data-testid="column"] {
                flex: 0 3 max-content !important;  
                min-width: min-content;                   
                justify-content: start !important;
                margin: -0.3em !important;        
                padding: 0;          
                # background-color: gray;
            }
            div[data-testid="column"] * {
                width: fit-content !important;
                padding: 0.015em;
                margin: -0.035em;
                border-radius: 16px;
                # background-color: red;     
            }
            div[data-testid="column"] button {
                height: 1.9em;
                align-items: center;
                justify-content: center;
                padding: 0 0.3em 0 0.3em;
            }
            div[data-testid="column"] button * {
                margin: -0.1em;
                padding: 0;
            }
                
        </style>
        """, unsafe_allow_html=True)    

    plh = plh = st.empty()
    for text, col in list(map(list, zip(button_list, plh.columns(len(button_list))))):
        with col:
            col.button(label=text, key=text, on_click=on_click_callback, args={text})
