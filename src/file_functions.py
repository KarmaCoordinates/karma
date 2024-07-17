import pickle
import boto3
import pandas as pd


def save_data_using_pickle(model, bucket_name, object_key):
    # save the model to disk
    s3_uri = f'/tmp/{object_key}'
    pickle.dump(model, open(s3_uri, 'wb'))
    # pickle_byte_obj = pickle.dumps(model)
    s3 = boto3.client("s3")
    s3.upload_file(s3_uri, bucket_name, object_key)
    

def load_pickle_data(bucket_name, object_key):
    data = pd.read_pickle(f's3://{bucket_name}/{object_key}')
    return data
    # s3_uri = f'/tmp/{object_key}'
    # s3 = boto3.client('s3')
    # s3.download_file(bucket_name, object_key, s3_uri)
    # return pickle.load(open(s3_uri, 'rb'))
    #return pickle.loads(s3.Bucket(bucket_name).Object(object_key).get()['Body'].read())


