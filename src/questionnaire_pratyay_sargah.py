import streamlit as st
import numpy as np
import pandas as pd
import s3_functions as s3f
import score_functions as sf
import configs

@st.cache_data
def _cache_questionnaire(bucket_name, features_data_dict_object_key, categories_data_dict_object_key):
    features_df = s3f.cache_csv_from_s3(bucket_name=bucket_name, object_key=features_data_dict_object_key)
    key_value_columns = ['Option_1', 'Value_1', 'Option_2', 'Value_2', 'Option_3', 'Value_3', 'Option_4', 'Value_4']
    features_df['options_dict'] = [{ k: v for k, v in zip(row[::2], row[1::2]) if pd.notna(k) and pd.notna(v) } for row in features_df[key_value_columns].values]
    key_columns = ['Option_1', 'Option_2', 'Option_3', 'Option_4']
    features_df['options_list'] = [list(filter(pd.notna, item)) for item in zip(*features_df[key_columns].values.T)]
    categories_df = s3f.cache_csv_from_s3(bucket_name=bucket_name, object_key=categories_data_dict_object_key)

    value_columns = features_df[['Value_1', 'Value_2', 'Value_3', 'Value_4']]
    minimum_score = value_columns.min(axis=1).sum()
    maximum_score = value_columns.max(axis=1).sum()
    # total_min = min_values.sum()
    # total_max = max_values.sum()
     
    return features_df, categories_df, {'minimum_score':minimum_score, 'maximum_score':maximum_score, 'number_of_questions':len(features_df)}


def _init():    
    if 'user_answers' not in st.session_state:
        st.session_state['user_answers'] = {}

    if  'minimum_required_completion_percent' not in st.session_state:
        st.session_state['minimum_required_completion_percent'] = configs.get_config().minimum_assessment_completion_percent

    if 'ai_analysis_requested' not in st.session_state:
        st.session_state['ai_analysis_requested'] = False
 

def _cache_user_answer(user_answer):
    st.session_state.user_answers[user_answer] = st.session_state[user_answer]


# Function to process each category of questions
def _calc_scores():
    category_scores = {}
    score_range = {}
    score = 0
    features_df, categories_df, _score_range = _cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
    score_range = _score_range
    for category_tpl in categories_df.itertuples():
        category_scores[category_tpl.category_name] = 0
        st.markdown(f'{category_tpl.category_name} Assessment - {category_tpl.category_description}')
        for feature_tpl in features_df.loc[features_df['Category'] == category_tpl.category_name].itertuples():
            selected_option = st.radio(feature_tpl.Question, feature_tpl.options_list, key=feature_tpl.Question, on_change=_cache_user_answer, args={feature_tpl.Question})
            selected_option_score = feature_tpl.options_dict.get(selected_option) 
            category_scores[category_tpl.category_name] += selected_option_score  

    return category_scores, score_range

def _process_questions():
    category_scores, score_range = _calc_scores()
    input_df = pd.DataFrame(st.session_state.user_answers, index=[0])
    return input_df, st.session_state.user_answers, category_scores, sum(category_scores.values()), _get_score_analysis_query(category_scores), score_range

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

def _get_score_analysis_query(category_scores):
    clarity_of_thinking_index = sum(category_scores.values())
    score_md = ''
    for category, score in category_scores.items():
        score_md = score_md + f'''{category}:{score}, '''

    # Display clarity of thinking index
    score_md = f'''Your **Clarity of Thinking** score: **{clarity_of_thinking_index}** [{score_md}] '''

    return score_md

def assessment():
    _init()
    with st.container(border=True):
        input_df, user_answers, category_scores, total_score, score_ai_analysis_query, score_range = _process_questions()
        st.divider()
        plh_kc = st.empty()
        # st.subheader('AI analysis')
        plh = st.container()
        # clicked = st.button('Show and explain my score', on_click=openai_assistant_chat.prompt_specific, args=(qps.get_score(), plh))
        # clicked = st.button('Show and explain my score')
        # if clicked:
        percent_completed = len(st.session_state.user_answers) * 100 / score_range['number_of_questions']
        if percent_completed > st.session_state.minimum_required_completion_percent:
            # st.session_state['ai_analysis_requested'] = True
            st.session_state['karma_coordinates'] = category_scores
            live_to_moksha = sf.calculate_karma_coordinates(category_scores, score_range)
            plh_kc.markdown(f':orange-background[$$\\large\\space Number\\space of \\space lives \\space to \\space Moksha:$$ $$\\huge {live_to_moksha} $$] $$\\small (Based\\space on\\space {round(percent_completed)}\\% \\space assessment.)$$')
            # openai_assistant_chat.prompt_specific(score_ai_analysis_query, plh)                
            # st.session_state.minimum_required_completion_percent = min(round(st.session_state.minimum_required_completion_percent * 1.2), 100)
        else:
            # if st.session_state['ai_analysis_requested']: 
                #ai_analysis was requested before, now increment the limit
                # st.session_state.minimum_required_completion_percent = min(round(st.session_state.minimum_required_completion_percent * 1.2), 100)
                # st.session_state['ai_analysis_requested'] = False
            st.warning(f'Atleast {round(st.session_state.minimum_required_completion_percent)}\\% of assessment needs to be completed to see Karma Coordinates.')
    return user_answers, score_ai_analysis_query, percent_completed

def main():
    pass

if __name__ == '__main__': main()
