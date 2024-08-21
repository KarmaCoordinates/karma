from sklearn.preprocessing import scale
import numpy as np
import pandas as pd
import itertools
import s3_functions as s3f
from ast import literal_eval

# weightage translates to how much it contributes to clarity of thinking

bucket_name = 'karmacoordinates'
data_dictionary_file = 'karma_coordinates_feature_dictionary.csv'
data_dictionary_df = s3f.cache_csv_from_s3(bucket_name, data_dictionary_file)
data_dictionary_df.columns = data_dictionary_df.iloc[0] # set first row as column names
data_dictionary_df = data_dictionary_df.iloc[1:11, 0:4] # first row is headers, get first 8 rows and first three columns only
data_dictionary_df['value_weight'] = data_dictionary_df['value_weight'].apply(literal_eval) # read all strings as literal (array, etc)

def get_feature_df(feature_name):
    df = data_dictionary_df.loc[data_dictionary_df['name'] == feature_name, 'value_weight'].values[0]
    df = pd.DataFrame(df, columns=[feature_name, f'{feature_name}_weight'])
    df[f'{feature_name}_scaled_weight'] = scale(df[f'{feature_name}_weight'])
    return df

def karma_coordinates_label(row):
    remaining_human_lives = round(row["karma_coordinates"])
    if row["karma_coordinates"] > 11:
        return f"{remaining_human_lives}/13 Nearing Moksha. Satva=Dominant, Tamas=Low"
    if row["karma_coordinates"] > 9:
        return f"{remaining_human_lives}/13 Highly Awakened. Satva=High, Tamas=Moderate"
    if row["karma_coordinates"] > 5:
        return f"{remaining_human_lives}/13 Moderately Awakened. Satva=Moderate, Tamas=High"
    return (
        f"{remaining_human_lives}/13 Awakening has started. Satva=Low, Tamas=Dominant"
    )

def calculate_level_of_clarity(row):
    return (
        row.knowledge_scaled_weight
        + row.discipline_scaled_weight
        + row.diet_scaled_weight
        + row.workout_scaled_weight
        - row.drink_scaled_weight
        + row.spirituality_scaled_weight
        - row.positive_emotion_scaled_weight
        - row.negative_emotion_scaled_weight
        # + row.fasting_scaled_weight
        # + row.swear_words_scaled_weight
    )

# load features
knowledge_df = get_feature_df('knowledge')
discipline_df = get_feature_df('discipline')
diet_df = get_feature_df('diet')
workout_df = get_feature_df('workout')
drink_df = get_feature_df('drink')
spirituality_df = get_feature_df('spirituality')
positive_emotion_df = get_feature_df('positive_emotion')
negative_emotion_df = get_feature_df('negative_emotion')
fasting_df = get_feature_df('fasting')
swear_words_df = get_feature_df('swear_words')


# Perform the Cartesian product using merge
df = pd.merge(
    negative_emotion_df,
    pd.merge(
        positive_emotion_df,
        pd.merge(
            spirituality_df,
            pd.merge(
                drink_df,
                pd.merge(
                    workout_df,
                    pd.merge(
                        diet_df,
                        pd.merge(
                            knowledge_df,
                            discipline_df,
                            # pd.merge(
                            #     discipline_df,
                            #     pd.merge(fasting_df, swear_words_df, how="cross"),
                            #     how="cross",
                            # ),
                            how="cross",
                        ),
                        how="cross",
                    ),
                    how="cross",
                ),
                how="cross",
            ),
            how="cross",
        ),
        how="cross",
    ),
    how="cross",
)

# Scale the calculated level
df["scaled_level"] = df.apply(calculate_level_of_clarity, axis=1)

# Transform scale to 1-13 billion year or 1-13 million human lives
df = df.loc[:, ~df.columns.str.match(".*_weight")]
minkc = 1
maxkc = 13
df["karma_coordinates"] = (df["scaled_level"] - df["scaled_level"].min()) / (
    df["scaled_level"].max() - df["scaled_level"].min()
) * (maxkc - minkc) + minkc
# df['karma_coordinates_label'] = df.apply(karma_coordinates_label, axis=1)

# exit()

# 5.3 Writing Data to CSV in Chunks
chunk_size = 1440000
num_chunks = len(df) // chunk_size + 1

for i, chunk in enumerate(np.array_split(df, num_chunks)):
    chunk.to_csv(f".tmp/kc3_synthout_chunk_{i}.csv", index=False)
