import streamlit as st
import numpy as np
import pandas as pd
import storage.s3_functions as s3f
import assessment.scoring as sf
import __configs
import random
import storage.dynamodb_functions as db
import streamlit_functions.state_mgmt_functions as smf
import ai.openai_assistant_chat as oac
import re
import ast
import journal.journal_functions as jf

@st.cache_data
def __cache_questionnaire(bucket_name, features_data_dict_object_key, categories_data_dict_object_key):
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


def __init():    
    if 'user_answers' not in st.session_state:
        st.session_state['user_answers'] = {}

    if  'minimum_required_completion_percent' not in st.session_state:
        st.session_state['minimum_required_completion_percent'] = __configs.get_config().minimum_assessment_completion_percent

    if 'ai_analysis_requested' not in st.session_state:
        st.session_state['ai_analysis_requested'] = False
 

def __cache_user_answer(question):
    st.session_state.user_answers.update({question:st.session_state[question]})


def __calc_category_scores_user_selection(features_df, categories_df):
    category_scores={}
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

            selected_option = st.radio(feature_tpl.Question, feature_tpl.options_list, index=default_index, key=feature_tpl.Question, on_change=__cache_user_answer, args={feature_tpl.Question})

            selected_option_score = feature_tpl.options_dict.get(selected_option) 
            category_scores[category_tpl.category_name] += selected_option_score

    return category_scores


def __calc_category_scores(features_df, categories_df):
    category_scores={}
    for category_tpl in categories_df.itertuples():
        category_scores[category_tpl.category_name] = 0
        for feature_tpl in features_df.loc[features_df['Category'] == category_tpl.category_name].itertuples():
            default_index = 0
            default_selected_option = None
            if feature_tpl.Question in st.session_state.user_answers:
                default_selected_option = st.session_state.user_answers[feature_tpl.Question]
            else:
                default_selected_option = feature_tpl.options_list[default_index]

            # st.session_state.user_answers.update({feature_tpl.Question:default_selected_option})
            selected_option_score = feature_tpl.options_dict.get(default_selected_option) 

            if selected_option_score:
                category_scores[category_tpl.category_name] += selected_option_score

    return category_scores

def __get_score_analysis_query(category_scores):
    clarity_of_thinking_index = sum(category_scores.values())
    score_md = ''
    for category, score in category_scores.items():
        score_md = score_md + f'''{category}:{round(score, 1)}, '''

    score_md = f'''Your **Clarity of Thinking** score: **{clarity_of_thinking_index}** [{score_md}] '''

    return score_md

def retrieve_previous_assessment():
    if not st.session_state.previous_user_answers:
        response = db.query(st.session_state.user_answers['email'], 'latest')
        if not response is None and len(response) > 0:
            st.session_state.user_answers.update({'journal_entry' : None, 'score_ai_analysis_query':None, 'lives_to_moksha':None})
            # second parameter takes precedence
            st.session_state.user_answers = {**response[0], **st.session_state.user_answers}
            st.session_state.previous_user_answers = True

def __save_assessment(features_df_stats, category_scores, print_only=None):
    st.divider()
    plh_kc = st.empty()
    score_ai_analysis_query = __get_score_analysis_query(category_scores)     
    percent_completed = len(st.session_state.user_answers) * 100 / features_df_stats['number_of_questions']
    if percent_completed > st.session_state.minimum_required_completion_percent:
        st.session_state['karma_coordinates'] = category_scores
        lives_to_moksha = sf.calculate_karma_coordinates(category_scores, features_df_stats)

        ref = '\\allowbreak\\tiny\\text{{(Sandeep Dixit, 2024. \\textit{{Calculating Karma Coordinates}})}}'
        completed = f'\\allowbreak\\small\\text{{based on {min([round(percent_completed), 100])}\\% completion.}}'
        score = f'\\large\\text{{Number of lives to Moksha:}}\\huge{{ {lives_to_moksha} }}'
        result = f':orange-background[$${score} {completed}$$] $${ref}$$'
        plh_kc.markdown(result)

        st.session_state.user_answers.update({'score_ai_analysis_query':score_ai_analysis_query, 'lives_to_moksha':lives_to_moksha})  
        if not print_only:          
            smf.save(None, 'assessment')
    # else:
    #     st.warning(f'Atleast {round(st.session_state.minimum_required_completion_percent)}\\% of assessment needs to be completed to see Karma Coordinates.')

    return percent_completed, score_ai_analysis_query


def __user_assessment(features_df, categories_df, features_df_stats, category_scores={}, placehoder=st.empty()):
    with placehoder.container():   
        category_scores = __calc_category_scores_user_selection(features_df, categories_df)  
        return __save_assessment(category_scores=category_scores, features_df_stats=features_df_stats, )


def __ai_assessment(features_df, categories_df, features_df_stats, placehoder=st.empty()):
    with placehoder.container():   
        if jf.is_new():
            query = f'''Analyse impact of journal entry={st.session_state.user_answers['journal_entry']}'''
            ai_query = f'''Given the questionnaire={features_df.to_csv()} 
                            and the answers={st.session_state.user_answers}, 
                            which answers get changed due to the new journal entry={st.session_state.user_answers['journal_entry']}?
                            Give impacted questions and changed answers (only from valid options of answers) as a dictionary.'''
            oac.prompt_specific(query=query, ai_query=ai_query, plh=placehoder)   
                        
            analysis = oac.get_assistant_answer_from_cache(query)

            if analysis:
                __update_assessment_per_analysis(features_df, analysis)
            
        category_scores = __calc_category_scores(features_df=features_df, categories_df=categories_df)  


        # st.markdown(f'Karma Coordinates AI automatically updates your assessment by analyzing your journal entries!') 
        phl_toggle = st.empty()
        manual_update = False #phl_toggle.toggle('Manually update assessment', key='toggle_assessment')
        if manual_update:
            phl_manual_assessment = st.empty()
            return __user_assessment(features_df=features_df, categories_df=categories_df, features_df_stats=features_df_stats, placehoder=phl_manual_assessment)

        else:
            if jf.is_new():
                return __save_assessment(category_scores=category_scores, features_df_stats=features_df_stats)
            else:
                return __save_assessment(category_scores=category_scores, features_df_stats=features_df_stats, print_only=True)

def __update_assessment_per_analysis(features_df, analysis):
    rx = r'(\{[^{}]+\})'
    matches = re.findall(rx, analysis)
    if matches and len(matches) > 0:                
        updated_dict = ast.literal_eval(matches[0])
        for i in updated_dict.keys():
            matched_question = features_df.loc[features_df['Question'] == i]
            if len(matched_question) == 1:
                answer = updated_dict.get(i)
                if answer in matched_question['options_list']:
                    st.session_state.user_answers.update({i:answer})



def assessment(placehoder=st.empty(), hide_assessment_questionnaire=False):
    __init()
    features_df, categories_df, features_df_stats = __cache_questionnaire('karmacoordinates', 'karma_coordinates_features_data_dictionary.csv', 'karma_coordinates_categories_data_dictionary.csv')
    with placehoder.container(border=False):
        if hide_assessment_questionnaire:
            plh = st.empty()
            return __ai_assessment(features_df=features_df, categories_df=categories_df, features_df_stats=features_df_stats, placehoder=plh)
        else:
            plh = st.empty()
            return __user_assessment(features_df=features_df, categories_df=categories_df, features_df_stats=features_df_stats, placehoder=plh)



def main():
    pass

if __name__ == '__main__': main()
