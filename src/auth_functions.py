import streamlit as st
import smtplib
import secrets
import configs
import re

def is_valid_email(email):
    # """Check if the email is a valid format."""
    # Regular expression for validating an Email
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    # If the string matches the regex, it is a valid email
    if re.match(regex, email):
        return True
    else:
        return False
    
# Function to send email
def send_email(recipient, token):
    # sending_email_bar = st.progress(0, 'Sending...')
    if not is_valid_email(recipient):
        return False

    try:
        # Setup the SMTP server
        _configs = configs.get_config()

        smtp_server = _configs.smtp_server
        smtp_port = _configs.smtp_port
        smtp_username = _configs.smtp_username
        sender_email = _configs.sender_email
        smtp_password = _configs.smtp_password

        # Create the email content
        subject = "KarmaCoordinates 2FA Token"
        body = f"Your token is {token}"
        msg = f"Subject: {subject}\n\n{body}"

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient, msg)

        # sending_email_bar.success("Emailed!")

        return True

    except Exception as e:
        # sending_email_bar.error(f"Error: {e}")
        return False


def _init():
    if '_enter_email' not in st.session_state:
        st.session_state['_enter_email'] = ''

    if 'token' not in st.session_state:
        st.session_state['token'] = ''

    if 'auth' not in st.session_state:
        st.session_state['auth'] = ''


def _send_token():
    b_email = False
        
    if 'enter_email' not in st.session_state:
        st.session_state.enter_email = ''

    if not st.session_state._enter_email == st.session_state.enter_email and st.session_state.enter_email:
        sending_email_bar = st.warning('Emailing token...')

        st.session_state._enter_email = None       
        token = secrets.token_hex(4)  
        b_email = send_email(st.session_state.enter_email, token)

        if b_email:
            st.session_state.token = token
            st.session_state._enter_email = st.session_state.enter_email
            sending_email_bar.success("Emailed!")
        else:
            sending_email_bar.error("Failed.")

    return b_email

def identity_msg():    
    phl = st.empty()
    checked = phl.checkbox(f''':green-background[Check to confirm your identity to track progress. (Note: This website does not collect any data unless you explicitly confirm your identity.)]''')
    if checked:
        do_2fa(phl)

# Streamlit app
def do_2fa(placeholder):
    _init()
    if st.session_state.auth:
        reset_data()
        placeholder.success(f'Your identity [*{st.session_state.email}*] is confirmed!')
    else:
        show_2fa(placeholder)

def show_2fa(placeholder):
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
            if st.session_state._enter_email and st.session_state.token:
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
                        st.session_state['email'] = st.session_state._enter_email
                        st.success(f'Your identity [*{st.session_state.email}*] is confirmed!')
                    else:
                        st.error("Failed.")

        with col4:
            # print(f'at 4...')
            st.empty()

        if st.session_state.auth:
            # print(f'at 5...')
            placeholder.success(f'Your identity [*{st.session_state.email}*] is confirmed!')


def reset_data():
    if '_enter_email' in st.session_state: st.session_state._enter_email=None
    if 'token' in st.session_state: st.session_state.token=None
    if 'enter_email' in st.session_state: st.session_state.enter_email=None
    if 'enter_token' in st.session_state: st.session_state.enter_token=None

def main():
    pass

if __name__ == '__main__': main()
