import boto3
from boto3.dynamodb.conditions import Key
import logging
import pandas as pd

temp_folder = '.tmp'
logging.basicConfig(filename=f'{temp_folder}/kc-app.log', filemode='w', level=logging.INFO)

class Columns:
    def __init__(self):
        self.email = 'email'
        self.partition_key_name = 'email'
        self.date = 'date'
        self.sort_key_name = 'date'
        self.lives_to_moksha = 'lives_to_moksha'
        self.journal_entry = 'journal_entry'
        self.score_ai_analysis_query = 'score_ai_analysis_query'

resource_name = 'dynamodb'
table_name = 'kc_user_activity'
partition_key_name = 'email'
sort_key_name = 'date'

def insert(user_activity_data):
    # session = boto3.Session()
    dynamodb = boto3.resource(resource_name)
    table = dynamodb.Table(table_name)
    response = table.put_item(
        Item=user_activity_data
    )
    latest_dict = dict(user_activity_data)
    latest_dict.update({'date': 'latest'})
    table.put_item(
        Item=latest_dict
    )

def query(partition_key_value, sort_key_prefix=17):
    try:
        dynamodb = boto3.resource(resource_name)
        table = dynamodb.Table(table_name)
        response = table.query(
            KeyConditionExpression=Key(partition_key_name).eq(partition_key_value) & Key(sort_key_name).begins_with(str(sort_key_prefix))
        )
        return response['Items']
    except:
        return False

def query_columns(columns_to_fetch=['lives_to_moksha']):
    try:
        dynamodb = boto3.resource(resource_name)
        table = dynamodb.Table(table_name)
        response = table.scan()
        return pd.DataFrame(response['Items'], columns=columns_to_fetch)
    except:
        return False


def get_column_names():
    return Columns()
# # Get the items
# items = response['Items']
    

def main():
    insert()

if __name__ == '__main__': main()
