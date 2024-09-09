import streamlit as st
import numpy as np
import pandas as pd
import s3_functions as s3f
import score_functions as sf
import _configs
import random
import dynamodb_functions as db
import state_mgmt_functions as smf
import openai_assistant_chat as oac
import re
import ast
import journal_functions as jf

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
     
    return features_df, categories_df, {'minimum_score':minimum_score, 'maximum_score':maximum_score, 'number_of_questions':len(features_df)}


def _init():    
    if 'user_answers' not in st.session_state:
        st.session_state['user_answers'] = {}

    if  'minimum_required_completion_percent' not in st.session_state:
        st.session_state['minimum_required_completion_percent'] = _configs.get_config().minimum_assessment_completion_percent

    if 'ai_analysis_requested' not in st.session_state:
        st.session_state['ai_analysis_requested'] = False
 

def _cache_user_answer(user_answer):
    st.session_state.user_answers[user_answer] = st.session_state[user_answer]


# Function to process each category of questions
def _calc_scores_user_selection(features_df, categories_df,category_scores={}, ):
    for category_tpl in categories_df.itertuples():
        category_scores[category_tpl.category_name] = 0
        st.markdown(f'{category_tpl.category_name} Assessment - {category_tpl.category_description}')

        for feature_tpl in features_df.loc[features_df['Category'] == category_tpl.category_name].itertuples():
            default_index = 0
            default_selected_option = None
            if feature_tpl.Question in st.session_state.user_answers:
                if st.session_state.user_answers[feature_tpl.Question] in feature_tpl.options_list:
                    default_index = feature_tpl.options_list.index(st.session_state.user_answers[feature_tpl.Question])
                    default_selected_option = st.session_state.user_answers[feature_tpl.Question]
            else:
                default_selected_option = feature_tpl.options_list[default_index]

            selected_option = st.radio(feature_tpl.Question, feature_tpl.options_list, index=default_index, key=feature_tpl.Question, on_change=_cache_user_answer, args={feature_tpl.Question})

            selected_option_score = feature_tpl.options_dict.get(selected_option) 
            category_scores[category_tpl.category_name] += selected_option_score

    return category_scores


def _calc_category_scores(features_df, categories_df,category_scores={}):
    for category_tpl in categories_df.itertuples():
        category_scores[category_tpl.category_name] = 0
        for feature_tpl in features_df.loc[features_df['Category'] == category_tpl.category_name].itertuples():
            default_index = 0
            default_selected_option = None
            if feature_tpl.Question in st.session_state.user_answers:
                default_selected_option = st.session_state.user_answers[feature_tpl.Question]
            else:
                default_selected_option = feature_tpl.options_list[default_index]

            selected_option_score = feature_tpl.options_dict.get(default_selected_option) 

            if selected_option_score:
                category_scores[category_tpl.category_name] += selected_option_score

    return category_scores

def _get_score_analysis_query(category_scores):
    clarity_of_thinking_index = sum(category_scores.values())
    score_md = ''
    for category, score in category_scores.items():
        score_md = score_md + f'''{category}:{round(score, 1)}, '''

    score_md = f'''Your **Clarity of Thinking** score: **{clarity_of_thinking_index}** [{score_md}] '''

    return score_md

def retrieve_previous_assessment():
    if not st.session_state.previous_user_answers:
        response = db.query(st.session_state.user_answers['email'], 'latest')
        # print(f'response {response}')
        if not response is None and len(response) > 0:
            st.session_state.user_answers.update({'journal_entry' : None})
            # second parameter takes precedence
            st.session_state.user_answers = {**response[0], **st.session_state.user_answers}
            st.session_state.previous_user_answers = True

def update_assessment(features_df_stats, category_scores):
    st.divider()
    plh_kc = st.empty()
    score_ai_analysis_query = _get_score_analysis_query(category_scores)        
    percent_completed = len(st.session_state.user_answers) * 100 / features_df_stats['number_of_questions']
    if percent_completed > st.session_state.minimum_required_completion_percent:
        st.session_state['karma_coordinates'] = category_scores
        lives_to_moksha = sf.calculate_karma_coordinates(category_scores, features_df_stats)
        plh_kc.markdown(f':orange-background[$$\\large\\space Number\\space of \\space lives \\space to \\space Moksha:$$ $$\\huge {lives_to_moksha} $$] $$\\small based\\space on\\space {round(percent_completed)}\\% \\space assessment.$$')
        # plh_kc.markdown(f'Sandeep\\space Dixit,\\space 2024.\\space \\it Calculating\\space Karma\\space Coordinates')
        st.session_state.user_answers.update({'score_ai_analysis_query':score_ai_analysis_query, 'lives_to_moksha':lives_to_moksha})           
        smf.save(None, 'assessment')
    else:
        st.warning(f'Atleast {round(st.session_state.minimum_required_completion_percent)}\\% of assessment needs to be completed to see Karma Coordinates.')

    return percent_completed, score_ai_analysis_query


def _user_assessment(features_df, categories_df, features_df_stats, category_scores={}, placehoder=st.empty()):
    with placehoder.container():   
        category_scores = _calc_scores_user_selection(features_df, categories_df)  
        return update_assessment(category_scores=category_scores, features_df_stats=features_df_stats, )


def _ai_assessment(features_df, categories_df, features_df_stats, placehoder=st.empty()):
    with placehoder.container():   
        if jf.is_new():
            # print(f'calling ai analysis')
            query = f'''Analyse impact of journal entry={st.session_state.user_answers['journal_entry']}'''
            ai_query = f'''Given the questionnaire={features_df.to_csv()} 
                            and the answers={st.session_state.user_answers}, 
                            which answers get changed due to the new journal entry={st.session_state.user_answers['journal_entry']}?
                            Give impacted questions and new answers (only from valid options of answers) as a dictionary.'''
            oac.prompt_specific(query=query, ai_query=ai_query, plh=placehoder)   
                        
            analysis = oac.get_assistant_answer_from_cache(query)

            rx = r'(\{[^{}]+\})'
            if analysis:
                matches = re.findall(rx, analysis)
                if matches and len(matches) > 0:                
                                # print(matches[0])
                    updated_dict = ast.literal_eval(matches[0])
                    st.session_state.user_answers.update(updated_dict)
                                # for i in matches[0].keys():
                                #         if i in user_answers:
                                #             user_answers[i]=matches[0][i]
                                # user_answers = user_answers | matches[0]
                    # percent_completed = len(st.session_state.user_answers) * 100 / features_df_stats['number_of_questions']
                    # update_assessment(features_df_stats, percent_completed, category_scores, st.session_state.user_answers)            
                    # return user_answers, analysis
            
                st.markdown(analysis)

        category_scores = _calc_category_scores(features_df=features_df, categories_df=categories_df)  
        st.markdown(f'Using previous assessment and current journal entry to perform differential AI analysis!')        

        return update_assessment(category_scores=category_scores, features_df_stats=features_df_stats)


def assessment(placehoder=st.empty(), hide_assessment_questionnaire=False):
    _init()
    features_df, categories_df, features_df_stats = _cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
    with placehoder.container(border=True):
        if hide_assessment_questionnaire:
            plh = st.empty()
            return _ai_assessment(features_df=features_df, categories_df=categories_df, features_df_stats=features_df_stats, placehoder=plh)
        else:
            plh = st.empty()
            return _user_assessment(features_df=features_df, categories_df=categories_df, features_df_stats=features_df_stats, placehoder=plh)



def main():
    pass

if __name__ == '__main__': main()
