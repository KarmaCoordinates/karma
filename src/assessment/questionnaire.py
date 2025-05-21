import pandas as pd
from storage import s3_functions as s3f

def cache_questionnaire(
    bucket_name, features_data_dict_object_key, categories_data_dict_object_key
):
    features_df = s3f.cache_csv_from_s3(
        bucket_name=bucket_name, object_key=features_data_dict_object_key
    )
    key_value_columns = [
        "Option_1",
        "Value_1",
        "Option_2",
        "Value_2",
        "Option_3",
        "Value_3",
        "Option_4",
        "Value_4",
    ]
    features_df["options_dict"] = [
        {k: v for k, v in zip(row[::2], row[1::2]) if pd.notna(k) and pd.notna(v)}
        for row in features_df[key_value_columns].values
    ]
    key_columns = ["Option_1", "Option_2", "Option_3", "Option_4"]
    features_df["options_list"] = [
        list(filter(pd.notna, item)) for item in zip(*features_df[key_columns].values.T)
    ]
    categories_df = s3f.cache_csv_from_s3(
        bucket_name=bucket_name, object_key=categories_data_dict_object_key
    )

    value_columns = features_df[["Value_1", "Value_2", "Value_3", "Value_4"]]
    minimum_score = value_columns.min(axis=1).sum()
    maximum_score = value_columns.max(axis=1).sum()

    return (
        features_df,
        categories_df,
        {
            "minimum_score": minimum_score,
            "maximum_score": maximum_score,
            "number_of_questions": len(features_df),
        },
    )
