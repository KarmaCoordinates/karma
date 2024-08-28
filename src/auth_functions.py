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


def send_token():
    b_email = False
        
    if 'enter_email' not in st.session_state:
        st.session_state.enter_email = ''
    # if ('send_token_button' in st.session_state and st.session_state.send_token_button) or ('enter_email' in st.session_state and not st.session_state.enter_email is None):        
        # Generate a 2FA token

    if not st.session_state._enter_email == st.session_state.enter_email and not st.session_state.enter_email is None:
        sending_email_bar = st.warning('Emailing token...')

        token = secrets.token_hex(4)  # Generates a secure token
        # st.session_state.email = email  # Store the email in session state
        b_email = send_email(st.session_state.enter_email, token)

        if b_email:
            st.session_state.token = token
            st.session_state._enter_email = st.session_state.enter_email
            sending_email_bar.success("Emailed!")
        else:
            sending_email_bar.error("Failed.")

    return b_email


# Streamlit app
def do_2fa():
    _init()
    phl = st.empty()
    if st.session_state.auth:
        reset_data()
        phl.markdown(f'Identity: You [*{st.session_state.email}*] are authenticated!')
    else:
        st.markdown("Confirm your identity:")
        show_2fa(phl)

def show_2fa(placeholder):
    col1, col2, col3, col4 = st.columns([4,1,2,1])
    with col1:
        # User input for email
        col1.markdown(
            """
            <style>
                [aria-label="Enter your email:"] {
                        max-width: 150px !important;
                }  
            </style>
            """,
            unsafe_allow_html=True
        )            
        email = col1.text_input("Enter your email:", key='enter_email')

        b_email = False
        if email:
            b_email = send_token()

    with col3:        
        if st.session_state._enter_email and st.session_state.token:
            col3.markdown(
                """
                <style>
                    [aria-label="Enter token:"] {
                            max-width: 70px !important;
                    }  
                </style>
                """,
                unsafe_allow_html=True
            )            
            user_token = col3.text_input("Enter token:", key='enter_token', max_chars=8)

            if user_token:
                if user_token == st.session_state.token:
                    st.session_state['auth']=True
                    st.success("Verified!")
                    st.session_state['email'] = st.session_state._enter_email
                    # reset_data()
                    # placeholder.markdown(f'Identity: You [*{st.session_state.email}*] are authenticated!')
                else:
                    st.error("Failed.")


def reset_data():
    if 'enter_email' in st.session_state: del st.session_state.enter_email 
    if '_enter_email' in st.session_state: del st.session_state._enter_email 
    if 'send_token_button' in st.session_state: del st.session_state.send_token_button
    if 'token' in st.session_state: del st.session_state.token
    if 'enter_token' in st.session_state: del st.session_state.enter_token
    if 'verify_token_button' in st.session_state: del st.session_state.verify_token_button

def main():
    pass

if __name__ == '__main__': main()
