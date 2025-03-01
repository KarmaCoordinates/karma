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
        self._journal_entry = '_journal_entry' #deprecated
        self.score_ai_analysis_query = 'score_ai_analysis_query'
        self.percent_completed = 'percent_completed'
        self.rating = 'rating'
        self.feedback = 'feedback'

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
        return None

def query_by_sort_key_between(partition_key_value, sort_key_start, sort_key_end):
    try:
        dynamodb = boto3.resource(resource_name)
        table = dynamodb.Table(table_name)
        response = table.query(
            KeyConditionExpression=Key(partition_key_name).eq(partition_key_value) & Key(sort_key_name).between(str(sort_key_start), str(sort_key_end))
        )
        return pd.DataFrame(response['Items'])
    except:
        return None

def query_columns(columns_to_fetch=['lives_to_moksha']):
    try:
        dynamodb = boto3.resource(resource_name)
        table = dynamodb.Table(table_name)
        response = table.scan()
        return pd.DataFrame(response['Items'], columns=columns_to_fetch)
    except:
        return None
    

def main():
    insert()

if __name__ == '__main__': main()
