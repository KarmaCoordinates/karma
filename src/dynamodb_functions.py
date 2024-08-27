import boto3


def insert(user_activity_data):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2' )
    table = dynamodb.Table('kc_user_activity')
    response = table.put_item(
        Item=user_activity_data
    )

def main():
    insert()

if __name__ == '__main__': main()
