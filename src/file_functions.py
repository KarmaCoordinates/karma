import pickle
import boto3
import pandas as pd
from pathlib import Path
import logging

temp_folder = '.tmp'
logging.basicConfig(filename=f'{temp_folder}/streamlit-app.log', filemode='w', level=logging.INFO)

# return df
def load_csv(bucket_name, object_key):
    logging.info('calling load_csv')
    s3_uri = f's3://{bucket_name}/{object_key}'
    # s3file = ff.read_from_s3('karmacoordinates', 'kc3_synthout_chunk_0.csv')
    # df = pd.read_csv(f'{resources_folder}/kc3_synthout_chunk_0.csv')
    return pd.read_csv(s3_uri)


def save_pickle_obj_to_s3(obj, bucket_name, object_key):
    logging.info('calling save_obj')
    # save the model to disk
    local_uri = f'{temp_folder}/{object_key}'
    pickle.dump(obj, open(local_uri, 'wb'))
    # pickle_byte_obj = pickle.dumps(model)
    s3 = boto3.client("s3")
    s3.upload_file(local_uri, bucket_name, object_key)
    

def load_pickle_obj_from_s3(bucket_name, object_key):
    logging.info('calling load_obj')
    local_uri = f'{temp_folder}/{object_key}'
    objfile = Path(local_uri)
    if objfile.is_file():
        logging.info(f'using local file:{local_uri}')
        return pickle.load(open(local_uri, 'rb'))
    else:
        s3_uri = f's3://{bucket_name}/{object_key}'
        logging.info(f'reading s3 file:{s3_uri}')
        data = pd.read_pickle(s3_uri)
        logging.info(f'saving s3 file:{s3_uri} locally at: {local_uri}')
        pickle.dump(data, open(local_uri, 'wb'))
        return data
    # s3_uri = f'/tmp/{object_key}'
    # s3 = boto3.client('s3')
    # s3.download_file(bucket_name, object_key, s3_uri)
    # return pickle.load(open(s3_uri, 'rb'))
    #return pickle.loads(s3.Bucket(bucket_name).Object(object_key).get()['Body'].read())

def save_file_to_s3(filename, bucket_name, object_key):
    logging.info('calling save_obj')
    # save the model to disk
    # pickle_byte_obj = pickle.dumps(model)
    s3 = boto3.client("s3")
    s3.upload_file(filename, bucket_name, object_key, ExtraArgs={'ContentType': 'text/html', "ContentEncoding" : "utf-8"})
