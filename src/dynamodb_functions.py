import boto3


def insert(user_activity_data):
    # dynamodb = boto3.resource('dynamodb', region_name='us-east-2' )
    dynamodb = boto3.client('dynamodb')

    # table = dynamodb.Table('kc_user_activity')
    response = dynamodb.put_item(
        TableName='kc_user_activity',
        Item={
           'email': {'S': 'deleteme'},
            'date': {'S': 'deleteme'},
            'name': {'S': 'SomeName'}           
            }
    )

def main():
    insert()

if __name__ == '__main__': main()
