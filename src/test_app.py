import streamlit as st
import questionnaire_pratyay_sargah as qps
import s3_functions as s3f
import pandas as pd
import unicodedata
import secrets_app as sa
import configs as cfg
import smtplib

def test1(token):
    try:
        # sending_email_bar = st.progress(0, 'Sending...')
        _configs = cfg.get_config()
        smtp_server = _configs.smtp_server
        smtp_port = _configs.smtp_port
        smtp_username = _configs.smtp_username
        sender_email = _configs.sender_email
        smtp_password = _configs.smtp_password


        # print(f'{smtp_server}, {smtp_username}, {smtp_password}, {smtp_port}')
        # Create the email content
        subject = "KarmaCoordinates 2FA Token"
        body = f"Your 2FA token is: {token}"
        msg = f"Subject: {subject}\n\n{body}"

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.set_debuglevel(1)
            result1 = server.starttls()
            result2 = server.login(smtp_username, smtp_password)
            server.sendmail(from_addr=sender_email, to_addrs=recipient, msg=msg)

        # sending_email_bar.success("Emailed!")
    except Exception as e:
        print(e)

def main():
    content = test1('123abcd')

if __name__ == '__main__': main()
