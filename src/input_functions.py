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
                    flex: unset;
                    width: fit-content !important;
                    justify-content: start !important;
                    margin: -0.3em !important;                
                }
                div[data-testid="column"] * {
                    width: fit-content !important;
                    padding: 0.015em;
                    margin: -0.035em;
                    border-radius: 16px;
                }
                div[data-testid="column"] button {
                    height: 1.9em;
                    padding: 0 0.3em 0 0.3em;
                    align-items: center;
                    justify-content: center;
                }
                div[data-testid="column"] button * {
                    padding: 0;
                    margin: -0.1em;
                }
            </style>
            """, unsafe_allow_html=True)    
    
    len_list = []
    total_len_list = len(button_list)
    for ele in button_list:
        len_list.append(len(ele)/total_len_list)

    # print(len_list)

    for text, col in list(map(list, zip(button_list, st.columns(len_list)))):
        # print(f'text:{text}, col{col}')
        with col:
            st.button(label=text, key=text, on_click=on_click_callback, args={text})
