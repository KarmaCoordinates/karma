from sklearn.preprocessing import scale
import numpy as np
import pandas as pd
import itertools


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


# Define the values for the features
amount_of_knowledge = [[12, 1], [16, 4], [18, 6], [20, 10], [22, 14]]
amount_of_knowledge_df = pd.DataFrame(
    amount_of_knowledge, columns=["knowledge", "knowledge_weight"]
)
amount_of_knowledge_df["knowledge_scaled_weight"] = scale(
    amount_of_knowledge_df["knowledge_weight"].astype(str)
)

# amount_of_knowledge_df['knowledge'] = amount_of_knowledge_df['knowledge'].astype(str)


disciplines = [
    ["medical", 1.5],
    ["engineering/technology", 1.3],
    ["arts/entertainment", 1.2],
    ["business/finance/accounting", 1.1],
    ["legal", 1],
]
disciplines_df = pd.DataFrame(disciplines, columns=["discipline", "discipline_weight"])
disciplines_df["discipline_scaled_weight"] = scale(disciplines_df["discipline_weight"])

diets = [["veg", 2], ["mostly veg", 1.5], ["mostly non veg", 1]]
diets_df = pd.DataFrame(diets, columns=["diet", "diet_weight"])
diets_df["diet_scaled_weight"] = scale(diets_df["diet_weight"])

workouts = [["daily", 3], ["often", 2], ["rarely", 1]]
workouts_df = pd.DataFrame(workouts, columns=["workout", "workout_weight"])
workouts_df["workout_scaled_weight"] = scale(workouts_df["workout_weight"])

drinks = [["daily", 3], ["often", 3], ["rarely", 1.5], ["never", 1]]
drinks_df = pd.DataFrame(drinks, columns=["drink", "drink_weight"])
drinks_df["drink_scaled_weight"] = scale(drinks_df["drink_weight"])

spiritualities = [["daily", 4], ["often", 2.5], ["rarely", 1.5], ["never", 1]]
spiritualities_df = pd.DataFrame(
    spiritualities, columns=["spirituality", "spirituality_weight"]
)
spiritualities_df["spirituality_scaled_weight"] = scale(
    spiritualities_df["spirituality_weight"]
)

positive_emotions = [["daily", 2], ["often", 1.5], ["rarely", 1.2], ["never", 1]]
positive_emotions_df = pd.DataFrame(
    positive_emotions, columns=["positive_emotion", "positive_emotion_weight"]
)
positive_emotions_df["positive_emotion_scaled_weight"] = scale(
    positive_emotions_df["positive_emotion_weight"]
)

negative_emotions = [["daily", 2], ["often", 1.5], ["rarely", 1.2], ["never", 1]]
negative_emotions_df = pd.DataFrame(
    negative_emotions, columns=["negative_emotion", "negative_emotion_weight"]
)
negative_emotions_df["negative_emotion_scaled_weight"] = scale(
    negative_emotions_df["negative_emotion_weight"]
)

fasting = [
    ["weekly", 9],
    ["monthly", 3],
    ["quarterly", 1.5],
    ["yearly", 1.1],
    ["never", 1],
]
fasting_df = pd.DataFrame(fasting, columns=["fasting", "fasting_weight"])
fasting_df["fasting_scaled_weight"] = scale(fasting_df["fasting_weight"])


swear_words = [["never", 2], ["rarely", 0], ["often", -1], ["daily", -2]]
swear_words_df = pd.DataFrame(
    swear_words, columns=["swear_words", "swear_words_weight"]
)
swear_words_df["swear_words_scaled_weight"] = scale(
    swear_words_df["swear_words_weight"]
)


def calculate_level(row):
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


# Perform the Cartesian product using merge
df = pd.merge(
    negative_emotions_df,
    pd.merge(
        positive_emotions_df,
        pd.merge(
            spiritualities_df,
            pd.merge(
                drinks_df,
                pd.merge(
                    workouts_df,
                    pd.merge(
                        diets_df,
                        pd.merge(
                            amount_of_knowledge_df,
                            disciplines_df,
                            # pd.merge(
                            #     disciplines_df,
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
df["scaled_level"] = df.apply(calculate_level, axis=1)

# Transform scale to 1-13 billion year or 1-13 million human lives
df = df.loc[:, ~df.columns.str.match(".*_weight")]
minkc = 1
maxkc = 13
df["karma_coordinates"] = (df["scaled_level"] - df["scaled_level"].min()) / (
    df["scaled_level"].max() - df["scaled_level"].min()
) * (maxkc - minkc) + minkc
# df['karma_coordinates_label'] = df.apply(karma_coordinates_label, axis=1)


# 5.3 Writing Data to CSV in Chunks
chunk_size = 1440000
num_chunks = len(df) // chunk_size + 1

for i, chunk in enumerate(np.array_split(df, num_chunks)):
    chunk.to_csv(f".tmp/kc3_synthout_chunk_{i}.csv", index=False)
