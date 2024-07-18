import pickle
import boto3
import pandas as pd
from pathlib import Path



def save_obj(obj, bucket_name, object_key):
    # save the model to disk
    local_uri = f'/tmp/{object_key}'
    pickle.dump(obj, open(local_uri, 'wb'))
    # pickle_byte_obj = pickle.dumps(model)
    s3 = boto3.client("s3")
    s3.upload_file(local_uri, bucket_name, object_key)
    

def load_obj(bucket_name, object_key):
    local_uri = f'/tmp/{object_key}'
    objfile = Path(local_uri)
    if objfile.is_file():
        print(f'using local file:{local_uri}')
        return pickle.load(open(local_uri, 'rb'))
    else:
        s3_uri = f's3://{bucket_name}/{object_key}'
        print(f'reading s3 file:{s3_uri}')
        data = pd.read_pickle(s3_uri)
        print(f'saving s3 file:{s3_uri} locally at: {local_uri}')
        pickle.dump(data, open(local_uri, 'wb'))
        return data
    # s3_uri = f'/tmp/{object_key}'
    # s3 = boto3.client('s3')
    # s3.download_file(bucket_name, object_key, s3_uri)
    # return pickle.load(open(s3_uri, 'rb'))
    #return pickle.loads(s3.Bucket(bucket_name).Object(object_key).get()['Body'].read())


