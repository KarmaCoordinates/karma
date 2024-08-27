import boto3
import logging

temp_folder = '.tmp'
logging.basicConfig(filename=f'{temp_folder}/kc-app.log', filemode='w', level=logging.INFO)

def insert(user_activity_data):
    # Attempt to create a session
    try:
        session = boto3.Session()  # This uses the default profile
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table('kc_user_activity')
        response = table.put_item(
            Item=user_activity_data
        )
    except Exception as e:
        logging.error(f'Unable to insert:{e}.')
        # print(f"Error: {e}")    


def main():
    insert()

if __name__ == '__main__': main()
