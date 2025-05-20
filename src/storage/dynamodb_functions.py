import random
import time
import boto3
from boto3.dynamodb.conditions import Key
import logging
import pandas as pd
from botocore.exceptions import ClientError
import __configs

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
    dynamodb = boto3.resource(resource_name, __configs.get_config().boto3_region)
    table = dynamodb.Table(table_name)
    response = table.put_item(
        Item=user_activity_data
    )
    latest_dict = dict(user_activity_data)
    latest_dict.update({'date': 'latest'})
    table.put_item(
        Item=latest_dict
    )

def query(partition_key_value, sort_key_prefix=17, ascending=True, numer_of_rows=250):
    try:
        dynamodb = boto3.resource(resource_name, __configs.get_config().boto3_region)
        table = dynamodb.Table(table_name)
        response = table.query(
            KeyConditionExpression=Key(partition_key_name).eq(partition_key_value) & Key(sort_key_name).begins_with(str(sort_key_prefix)),
            ScanIndexForward=ascending,
            Limit=numer_of_rows
        )
        return response['Items']
    except:
        return None

def query_by_sort_key_between(partition_key_value, sort_key_start, sort_key_end):
    try:
        dynamodb = boto3.resource(resource_name, __configs.get_config().boto3_region)
        table = dynamodb.Table(table_name)
        response = table.query(
            KeyConditionExpression=Key(partition_key_name).eq(partition_key_value) & Key(sort_key_name).between(str(sort_key_start), str(sort_key_end))
        )
        return pd.DataFrame(response['Items'])
    except:
        return None

def query_columns(columns_to_fetch=['lives_to_moksha']):
    try:
        dynamodb = boto3.resource(resource_name, __configs.get_config().boto3_region)
        table = dynamodb.Table(table_name)
        response = table.scan()
        return pd.DataFrame(response['Items'], columns=columns_to_fetch)
    except:
        return None
    
def query_index(
    index_name="date-index", key="date", value="latest"
):
    try:
        dynamodb = boto3.resource(resource_name, __configs.get_config().boto3_region)
        table = dynamodb.Table(table_name)

        response = table.query(
            IndexName=index_name, KeyConditionExpression=Key(key).eq(value)
        )
        return response
    except Exception as e:
        print(f"Error querying index: {e}")
        return None


def delete(partition_key_value):
    try:
        dynamodb = boto3.resource(resource_name)
        table = dynamodb.Table(table_name)

        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(partition_key_value)
        )

        items = response['Items']


        # Constants
        BATCH_SIZE = 25
        MAX_RETRIES = 5

        # Helper: retry logic with exponential backoff
        def retry_delete(item, attempt=1):
            try:
                table.delete_item(
                    Key={'email': item['email'], 'date': item['date']}
                )
            except ClientError as e:
                if attempt <= MAX_RETRIES and "ProvisionedThroughputExceededException" in str(e):
                    wait = 2 ** attempt + random.uniform(0, 1)
                    # print(f"Retrying {item['date']} (Attempt {attempt}) in {wait:.2f}s...")
                    time.sleep(wait)
                    retry_delete(item, attempt + 1)
                else:
                    print(f"Failed to delete {item['email']}{item['date']}: {e}")

        # Process batches
        for i in range(0, len(items), BATCH_SIZE):
            batch = items[i:i + BATCH_SIZE]
            # print(f"Processing batch {i // BATCH_SIZE + 1}")
            for item in batch:
                retry_delete(item)
            time.sleep(1)  # Throttle        
            
        return "Successful"
    except Exception as e:
        print(f"Error {e} occurred while deleting items.")
        return None

def main():
    insert()

if __name__ == '__main__': main()
