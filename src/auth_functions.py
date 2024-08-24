import streamlit as st
import smtplib
import secrets
import os
import configs

# Function to send email
def send_email(recipient, token):
    sending_email_bar = st.progress(0, 'Sending...')

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
        body = f"Your 2FA token is: {token}"
        msg = f"Subject: {subject}\n\n{body}"

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient, msg)

        sending_email_bar.success("Token emailed!")

    except Exception as e:
        sending_email_bar.error(f"Error emailing: {e}")

# Streamlit app
def do_2fa():
    st.markdown("Confirm identity:")

    if 'auth' in st.session_state and st.session_state.auth:
        reset_data()
        st.markdown(f'You [*{st.session_state.email}*] are authenticated!')
    else:
        show_2fa()

def show_2fa():
    col1, col2, col3, col4 = st.columns([.45, .15, .25, .15])
    with col1:
        # User input for email
        email = col1.text_input("Enter your email:", key='enter_email')
    with col2:
        if 'enter_email' in st.session_state and st.session_state.enter_email:
            send_token = col2.button("Send Token", key='send_token_button')

        if 'send_token_button' in st.session_state and st.session_state.send_token_button:
            # Generate a 2FA token
            token = secrets.token_hex(4)  # Generates a secure token
            st.session_state.token = token
            st.session_state.email = email  # Store the email in session state
            send_email(email, token)

    with col3:        
        if 'token' in st.session_state:
            user_token = col3.text_input("Enter received token:", key='enter_token', max_chars=8)

    with col4:
        if 'enter_token' in st.session_state and st.session_state.enter_token:
            verify_token = col4.button("Verify Token", key='verify_token_button')
            if verify_token:
                if user_token == st.session_state.token:
                    st.session_state['auth']=True
                    st.success("Verified!")
                else:
                    st.error("Failed.")


def reset_data():
    if 'enter_email' in st.session_state: del st.session_state.enter_email 
    if 'send_token_button' in st.session_state: del st.session_state.send_token_button
    if 'token' in st.session_state: del st.session_state.token
    if 'enter_token' in st.session_state: del st.session_state.enter_token
    if 'verify_token_button' in st.session_state: del st.session_state.verify_token_button

def main():
    pass

if __name__ == '__main__': main()
