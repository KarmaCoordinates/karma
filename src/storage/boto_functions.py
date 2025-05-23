import smtplib
import boto3

import __configs
from __utils import is_valid_email

def sms_opt_in(number):
    response = boto3.client('sns').opt_in_phone_number(
        phoneNumber=f'{number}'    
    )    
    print(f'response: {response}')

def sms_token(number, token):
    sns = boto3.client('sns')
    sns.set_sms_attributes(attributes={'DefaultSenderID': 'SankhyaApp', 'DefaultSMSType': 'Transactional'})
    # number = '+12169266696'
    sms_opt_in(number=number)
    sns.publish(PhoneNumber = number, Message=token )


def send_email(recipient, token):
    # sending_email_bar = st.progress(0, 'Sending...')
    if not is_valid_email(recipient):
        return False

    try:
        # Setup the SMTP server
        smtp_server = __configs.get_config().smtp_server
        smtp_port = __configs.get_config().smtp_port
        smtp_username = __configs.get_config().smtp_username
        sender_email = __configs.get_config().sender_email
        smtp_password = __configs.get_config().smtp_password

        # Create the email content
        subject = "KarmaCoordinates 2FA Token"
        body = f"Your token is {token}"
        msg = f"Subject: {subject}\n\n{body}"

        print(f'{smtp_server}:{smtp_port}:{smtp_username}:{sender_email}:{smtp_password}')
        try:
        # Connect to the SMTP server
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(sender_email, recipient, msg)
        except Exception as e:
            print(f'Error({e}):{smtp_server}:{smtp_port}:{smtp_username}:{sender_email}:{smtp_password}')


        # sending_email_bar.success("Emailed!")

        return True

    except Exception as e:
        # sending_email_bar.error(f"Error: {e}")
        # print(f'error sending email {e}')
        return False