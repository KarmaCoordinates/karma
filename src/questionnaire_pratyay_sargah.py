import streamlit as st
import numpy as np
import pandas as pd
import s3_functions as s3f

@st.cache_data
def _cache_questionnaire(bucket_name, features_data_dict_object_key, categories_data_dict_object_key):
    features_df = s3f.cache_csv_from_s3(bucket_name=bucket_name, object_key=features_data_dict_object_key)
    features_df['options_dict'] = features_df.apply(lambda row: {**{row['Option_1'] : row['Value_1']}, **{row['Option_2'] : row['Value_2']}, **{row['Option_3'] : row['Value_3']}, **{row['Option_4'] : row['Value_4']}}, axis=1)
    key_columns = ['Option_1', 'Option_2', 'Option_3', 'Option_4']
    features_df['options_list'] = [list(filter(pd.notna, item)) for item in zip(*features_df[key_columns].values.T)]
    categories_df = s3f.cache_csv_from_s3(bucket_name=bucket_name, object_key=categories_data_dict_object_key)
    return features_df, categories_df


def _init():
    if 'user_input' not in st.session_state:
        st.session_state['user_input'] = {}

def cache_user_input(user_selection):
    st.session_state.user_input[user_selection] = st.session_state[user_selection]

total_scores = {}

# Function to process each category of questions
def _calc_scores():
    score = 0
    features_df, categories_df = _cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
    for category_tpl in categories_df.itertuples():
        total_scores[category_tpl.category_name] = 0
        st.markdown(f'{category_tpl.category_name} Assessment - {category_tpl.category_description}')
        for feature_tpl in features_df.loc[features_df['Category'] == category_tpl.category_name].itertuples():
            selected_option = st.radio(feature_tpl.Question, feature_tpl.options_list, key=feature_tpl.Question, on_change=cache_user_input, args={feature_tpl.Question})
            selected_option_score = feature_tpl.options_dict.get(selected_option) 
            total_scores[category_tpl.category_name] += selected_option_score  

def process_questions():
    _init()
    _calc_scores()
    input_df = pd.DataFrame(st.session_state.user_input, index=[0])
    return input_df, st.session_state.user_input, sum(total_scores.values()), sum(total_scores.values())

# def show_score():
#     # Display total scores and calculate total clarity of thinking index
#     st.subheader("Total Scores Summary:")
#     clarity_of_thinking_index = sum(total_scores.values())
#     score_md = ''
#     for category, score in total_scores.items():
#         score_md = score_md + f'{category} Score: {score}'
#         st.write(f"{category} Score: {score}")

#     # Display clarity of thinking index
#     st.write(f"Your Clarity of Thinking Index: {clarity_of_thinking_index}")
#     score_md = score_md + f"Your Clarity of Thinking Index: {clarity_of_thinking_index}"

#     return score_md

    # Providing interpretation of the scores
    # if clarity_of_thinking_index < 0:
    #     st.write("You might want to work on your clarity of thinking.")
    # elif clarity_of_thinking_index == 0:
    #     st.write("You are at a neutral level. Consider focusing on personal growth.")
    # else:
    #     st.write("You have a good level of clarity of thinking and insight!")

def get_score():
    clarity_of_thinking_index = sum(total_scores.values())
    score_md = ''
    for category, score in total_scores.items():
        score_md = score_md + f'''{category}:{score}, '''

    # Display clarity of thinking index
    score_md = f'''Your **Clarity of Thinking** score: **{clarity_of_thinking_index}** [{score_md}] '''

    return score_md


