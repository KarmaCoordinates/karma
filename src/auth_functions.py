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
        body = f"Your token is {token}"
        msg = f"Subject: {subject}\n\n{body}"

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient, msg)

        sending_email_bar.success("Emailed!")

    except Exception as e:
        sending_email_bar.error(f"Error: {e}")

# Streamlit app
def do_2fa():
    st.markdown("Confirm your identity:")

    if 'auth' in st.session_state and st.session_state.auth:
        reset_data()
        st.markdown(f'You [*{st.session_state.email}*] are authenticated!')
    else:
        show_2fa()

def show_2fa():
    # ele_list = [{'key':'enter_email', 'label':'Enter your email:', 'type':'text_input', 'callback': on_click_callback, 'args': {'ele1'}, 'max-width': '280px'}, 
    #             {'key':'ti_2', 'label':'Send Token', 'type':'button', 'callback': on_click_callback, 'args': {'ele2'}}, 
    #             {'key':'ti_3', 'label':'ele3', 'type':'text_input', 'callback': on_click_callback, 'args': {'ele3'}, 'max-width': '70px'}, 
    #             {'key':'ti_4', 'label':'Verify Token', 'type':'button', 'callback': on_click_callback, 'args': {'ele4'}}]
    # render_elements(ele_list)

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
    with col2:
        if 'enter_email' in st.session_state and st.session_state.enter_email:
            send_token = col2.button(label="Send Token", key='send_token_button', use_container_width=True)

        if 'send_token_button' in st.session_state and st.session_state.send_token_button:
            # Generate a 2FA token
            token = secrets.token_hex(4)  # Generates a secure token
            st.session_state.token = token
            st.session_state.email = email  # Store the email in session state
            send_email(email, token)

    with col3:        
        if 'token' in st.session_state:
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

    with col4:
        if 'enter_token' in st.session_state and st.session_state.enter_token:
            verify_token = col4.button("Verify Token", key='verify_token_button', use_container_width=True)
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
