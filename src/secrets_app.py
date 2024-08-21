import model_functions
import s3_functions as ff
import pandas as pd

secrets_data_file = 'kc_secrets.txt'
bucket_name = 'karmacoordinates'
object_key = 'kc_secrets.sav'

def save_to_s3():
    df = pd.read_csv(f'{ff.temp_folder}/{secrets_data_file}', sep='=', header=None)
    ff.save_pickle_obj_to_s3(df, bucket_name, object_key)

def cache_from_s3(key):
    cached_df = ff.cache_pickle_obj_from_s3(bucket_name, object_key)
    value = cached_df.loc[cached_df[0] == key].to_numpy()[0][1]
    return value
# save_to_s3()
