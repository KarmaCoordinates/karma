import streamlit as st
import smtplib
import secrets
import os

# Function to send email
def send_email(recipient, token):
    try:
        # Setup the SMTP server
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = ""  # Change this to your email
        password = ""  # Use environment variables for security

        # Create the email content
        subject = "Your 2FA Token"
        body = f"Your 2FA token is: {token}"
        msg = f"Subject: {subject}\n\n{body}"

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient, msg)

        st.success("Token sent to your email!")

    except Exception as e:
        st.error(f"Error sending email: {e}")

# Streamlit app
def do_2fa():
    st.subheader("Two-Factor Authentication (2FA)")

    # User input for email
    email = st.text_input("Enter your email:")

    if st.button("Send Token"):
        if email:
            # Generate a 2FA token
            token = secrets.token_hex(4)  # Generates a secure token
            st.session_state.token = token
            st.session_state.email = email  # Store the email in session state
            send_email(email, token)
        else:
            st.error("Please provide a valid email!")

    # Token input for verification
    if 'token' in st.session_state:
        user_token = st.text_input("Enter the token you received:")

        if st.button("Verify Token"):
            if user_token == st.session_state.token:
                st.success("Token verified successfully!")
            else:
                st.error("Invalid token. Please try again.")

# if __name__ == "__main__":
#     main()
