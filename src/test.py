import streamlit as st

def init_buttons(button_list):
    if 'button_list' not in st.session_state:
        st.session_state.button_list = button_list

def remove_button(key):
    # if st.session_state.my_page_init:
    st.session_state.button_list.remove(key)

def render_buttons():
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
            st.button(label=text, key=text, on_click=remove_button, args={text})

print(f'starting...')

# if 'my_page_init' not in st.session_state:
#     st.session_state.my_page_init = False

init_buttons(['one', 'two', 'three'])

# user_suggestion_pills_label = "Let's get started:"
# user_selected_pill = stp.pills(user_suggestion_pills_label, st.session_state.user_suggestion_pills, clearable=None, index=None)

render_buttons()

# for pill in st.session_state.user_suggestion_pills:
#     st.button(label=pill, key=pill, on_click=refresh, args={pill})

# st.session_state.my_page_init = True

print(f'ended.')
