import streamlit as st
import secrets
import time
from boto_functions import send_email, sms_token



def _init():
    if '_enter_email' not in st.session_state:
        st.session_state['_enter_email'] = ''

    if 'token' not in st.session_state:
        st.session_state['token'] = ''

    if 'auth' not in st.session_state:
        st.session_state['auth'] = ''
            

# Function to send email
def _send_token():
    b_email = False
        
    if 'enter_email' not in st.session_state:
        st.session_state.enter_email = ''

    if not st.session_state._enter_email == st.session_state.enter_email and st.session_state.enter_email:
        sending_email_bar = st.warning('Emailing token...')

        st.session_state._enter_email = None       
        token = secrets.token_hex(4)  
        b_email = send_email(st.session_state.enter_email, token)

        # try:
        #     sms_token('+12169266696', token)
        # except Exception as e:
        #     print(f'error: {e}')


        if b_email:
            st.session_state.token = token
            st.session_state._enter_email = st.session_state.enter_email
            sending_email_bar.success("Emailed!")
        else:
            sending_email_bar.error("Failed.")

    return b_email

def identity_msg():    
    _init()
    phl = st.empty()
    checked = phl.checkbox(f''':green-background[Check to confirm your identity to track progress. (Note: This website does not collect any data unless you explicitly confirm your identity.)]''')
    if checked:
        _do_2fa(phl)
        
    return st.session_state.auth

def _do_2fa(placeholder):
    if st.session_state.auth:
        _reset_data()
        placeholder.success(f'Your identity [*{st.session_state._enter_email}*] is confirmed!', icon="✅")
    else:
        _show_2fa(placeholder)

def _show_2fa(placeholder):
    with placeholder.container():
        col1, col2, col3, col4 = st.columns([4,1,2,1])
        with col1:
            col1.markdown(
                """
                <style>
                    [aria-label="Enter your email:"] {
                            max-width: 150px !important;
                            background-color: #023020;
                    }  
                </style>
                """,
                unsafe_allow_html=True
            )            
            email = col1.text_input("Enter your email:", key='enter_email')
            if email: 
                _send_token()

        with col2:
            st.empty()

        with col3:        
            if st.session_state._enter_email:
                col3.markdown(
                    """
                    <style>
                        [aria-label="Enter token:"] {
                            max-width: 70px !important;
                            background-color: #023020;
                        }  
                    </style>
                    """,
                    unsafe_allow_html=True
                )            
                user_token = col3.text_input("Enter token:", key='enter_token', max_chars=8)

                if user_token:
                    if user_token == st.session_state.token:
                        st.session_state.auth=True
                        st.session_state.user_answers.update({'email': st.session_state._enter_email, 'date' : str(time.time())})
                        # print(f'''auth: {st.session_state.user_answers['email']}''')
                        st.success(f'Your identity [*{st.session_state._enter_email}*] is confirmed!')
                    else:
                        st.error("Failed.")

        with col4:
            st.empty()

        if st.session_state.auth:
            placeholder.success(f'Your identity [*{st.session_state.enter_email}*] is confirmed!')


def _reset_data():
    if 'token' in st.session_state: st.session_state.token=None
    if 'enter_email' in st.session_state: st.session_state.enter_email=None
    if 'enter_token' in st.session_state: st.session_state.enter_token=None

def main():
    # pass
    sms()

if __name__ == '__main__': main()
