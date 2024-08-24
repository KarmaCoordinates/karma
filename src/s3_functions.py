import pickle
import boto3
import pandas as pd
from pathlib import Path
import logging
import requests
import socket


temp_folder = '.tmp'
pickle_file_extension = 'pkl'
logging.basicConfig(filename=f'{temp_folder}/kc-app.log', filemode='w', level=logging.INFO)

# return df
def cache_csv_from_s3(bucket_name, object_key):
    logging.info('calling cache_csv_from_s3...')
    local_uri = f'{temp_folder}/{object_key}.{pickle_file_extension}'
    objfile = Path(local_uri)
    if objfile.is_file():
        logging.info(f'using cached file:{local_uri}.')
        return pickle.load(open(local_uri, 'rb'))
    else:
        s3_uri = f's3://{bucket_name}/{object_key}'
        logging.info(f'using s3 file:{s3_uri} and caching at {local_uri}.')
        df = pd.read_csv(s3_uri)
        pickle.dump(df, open(local_uri, 'wb'))
        return df

def save_pickle_obj_to_s3(obj, bucket_name, object_key):
    logging.info('calling save_pickle_obj_to_s3...')
    local_uri = f'{temp_folder}/{object_key}.{pickle_file_extension}'
    pickle.dump(obj, open(local_uri, 'wb'))
    s3 = boto3.client("s3")
    s3.upload_file(local_uri, bucket_name, object_key)
    
def cache_pickle_obj_from_s3(bucket_name, object_key):
    logging.info('calling cache_pickle_obj_from_s3')
    local_uri = f'{temp_folder}/{object_key}.{pickle_file_extension}'
    objfile = Path(local_uri)
    if objfile.is_file():
        logging.info(f'using cached file:{local_uri}.')
        return pickle.load(open(local_uri, 'rb'))
    else:
        s3_uri = f's3://{bucket_name}/{object_key}'
        logging.info(f'reading s3 file:{s3_uri} and caching at {local_uri}.')
        data = pd.read_pickle(s3_uri)
        pickle.dump(data, open(local_uri, 'wb'))
        return data

def save_html_to_s3(filename, bucket_name, object_key):
    logging.info('calling save_file_to_s3')
    s3 = boto3.client("s3")
    s3.upload_file(filename, bucket_name, object_key, ExtraArgs={'ContentType': 'text/html', "ContentEncoding" : "utf-8"})


def main():
    pass

if __name__ == '__main__': main()
