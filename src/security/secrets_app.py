import pandas as pd
from functools import lru_cache
from storage import s3_functions as s3f

secrets_data_file = 'kc_secrets.txt'
bucket_name = 'karmacoordinates'
object_key = 'kc_secrets.sav'

def save_to_s3():
    s3f.save_csv_to_s3(csv_filename=secrets_data_file, csv_seperator="=", bucket_name=bucket_name, object_key=object_key)
    # df = pd.read_csv(f'{s3f.temp_folder}/{secrets_data_file}', sep='=', header=None)
    # s3f.save_pickle_obj_to_s3(df, bucket_name, object_key)

@lru_cache(maxsize=None)  # Unlimited cache size
def cache_from_s3(bucket_name, object_key):
    return s3f.cache_pickle_obj_from_s3(bucket_name, object_key)

def get_value(key):
    cached_df = cache_from_s3(bucket_name, object_key)
    value = cached_df.loc[cached_df[0] == key].to_numpy()[0][1]
    return value
