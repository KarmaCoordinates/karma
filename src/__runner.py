from storage import s3_functions as sf3
from security import secrets_app as sap
from prompts import prompt_engine as pe

# in order to run programs in the subdirectories, use this util
if __name__ == '__main__': 
    # sap.main()
    # To create prompts file in s3 use the following command
    pe.save_prompt_in_s3()

    # upload secrets file
    # sap.save_to_s3()
    # sender_email = sap.get_value('SENDER_EMAIL')
    # print(f'testing : {sender_email}')