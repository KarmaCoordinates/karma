import boto3


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
        print(f"Error: {e}")    


def main():
    insert()

if __name__ == '__main__': main()
