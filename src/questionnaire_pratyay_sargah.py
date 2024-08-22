import streamlit as st
import numpy as np
import pandas as pd
import s3_functions as s3f

# categories_descriptions = {
#     'Viparyayah (विपर्यय)' : '''This term refers to wrong perception or misunderstanding. It denotes a state of error or ignorance where one misapprehends reality, often due to an inversion of the true understanding. In a more detailed context within Samkhya, it can relate to the various forms of ignorance that distort one's understanding of the self and the world''',
#     'Aśakti (अशक्ति)' : '''Ashakti translates to incapacity or inability. It signifies a state where one is unable to perform actions effectively due to various impairments, particularly regarding the sensory organs or cognitive functions. This incapacity can manifest in different forms, contributing to individuals' difficulties in discerning truths or fulfilling their potential''',
#     'Tuṣṭi (तुष्टि)' : '''Tushti means contentment or satisfaction. It refers to a state of being pleased or content with one's circumstances or understanding. In Samkhya philosophy, it can signify a mental state that arises when the mind is at peace with reality, achieving a sense of well-being''',
#     'Siddhi (सिद्धि)' : '''Siddhi denotes perfection or accomplishment. It implies the attainment of goals, mastery over certain skills, or realization of one's potential. In spiritual contexts, it can refer to the acquisition of supernatural powers or significant spiritual achievements. Siddhi is often discussed in relation to personal growth and the realization of one's true nature''',
#     'Lifestyle' : '''The typical way of life -  interests, opinions, behaviours, and behavioural orientations - of an individual'''
#  }


@st.cache_data
def _cache_questionnaire(bucket_name, features_data_dict_object_key, categories_data_dict_object_key):
    features_df = s3f.cache_csv_from_s3(bucket_name=bucket_name, object_key=features_data_dict_object_key)
    categories_df = s3f.cache_csv_from_s3(bucket_name=bucket_name, object_key=categories_data_dict_object_key)
    # df.columns = df.iloc[0] # first row is column names
    # df = df[1:] 
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
    # total_scores[category] = 0

    features_df, categories_df = _cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
    for category_tuple in categories_df.itertuples():
        total_scores[category_tuple.category_name] = 0
        st.markdown(f'{category_tuple.category_name} Assessment - {category_tuple.category_description}')
        for feature_tuple in features_df.loc[features_df['Category'] == category_tuple.category_name].itertuples():
            option_names = [x for x in [feature_tuple.Option_1, feature_tuple.Option_2, feature_tuple.Option_3, feature_tuple.Option_4] if str(x) != 'nan']
            options_value = [x for x in [feature_tuple.Value_1, feature_tuple.Value_2, feature_tuple.Value_3, feature_tuple.Value_4] if str(x) != 'nan']
            selected_option = st.radio(feature_tuple.Question, option_names, key=feature_tuple.Question, on_change=cache_user_input, args={feature_tuple.Question})
            selected_option_score = options_value[option_names.index(selected_option)] 
            total_scores[category_tuple.category_name] += selected_option_score  

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



# _init()
# process_questions()
# show_score()        

