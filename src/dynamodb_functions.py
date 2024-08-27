import boto3
import logging

temp_folder = '.tmp'
logging.basicConfig(filename=f'{temp_folder}/kc-app.log', filemode='w', level=logging.INFO)

def insert(user_activity_data):
    session = boto3.Session()  # This uses the default profile
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('kc_user_activity')
    response = table.put_item(
        Item=user_activity_data
    )

def main():
    insert()

if __name__ == '__main__': main()
