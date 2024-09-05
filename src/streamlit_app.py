import model_functions
import web_content 
import streamlit as st
import s3_functions as s3f
import openai_assistant_chat
import stripe_payment as sp
import questionnaire_pratyay_sargah as qps
import feedback_functions as ff
import pdf_functions as pdf
import auth_functions as af
import score_functions as sf
import journal_functions as jf
import plot_functions as pf
import dynamodb_functions as db
import state_mgmt_functions as smf
import re
import ast

@st.cache_data
def cache_model(model_choice, bucket_name, features_data_file, pickled_model_data_file):
    data_dictionary_file = 'karma_coordinates_feature_dictionary.csv'
    data_dictionary_df = s3f.cache_csv_from_s3(bucket_name, data_dictionary_file)
    data_dictionary_df = data_dictionary_df.iloc[1:9, 0:4] # first row is headers, get first 8 rows and first three columns only
    data_dictionary_array = data_dictionary_df.to_numpy()

    df = s3f.cache_csv_from_s3(bucket_name, features_data_file)
    df, X, y, label_encoder = model_functions.read_features(df)
    categorical_cols, numeric_cols, preprocessor = model_functions.encode_features(X)
    model, X_train, X_test, y_train, y_test = model_functions.define_model(X, y, model_choice, preprocessor)
    model = s3f.cache_pickle_obj_from_s3(bucket_name, pickled_model_data_file)
    return data_dictionary_array, df, X.columns, categorical_cols, model, label_encoder


def _update_assessment(features_df, score_range, percent_completed, category_scores, user_answers, plh):
    query = f'''Analyse impact of journal entry={st.session_state.user_answers['journal_entry']}'''
    ai_query = f'''Given the questionnaire={features_df.to_csv()} 
                    and the answers={user_answers}, 
                    which answers get changed due to the new journal entry={st.session_state.user_answers['journal_entry']}?
                    Give impacted questions and new answers (only from valid options of answers) as a dictionary.'''
    openai_assistant_chat.prompt_specific(query=query, ai_query=ai_query, plh=plh)   
                  
    analysis = openai_assistant_chat.get_assistant_answer_from_cache(query)

    rx = r'(\{[^{}]+\})'
    if analysis:
        matches = re.findall(rx, analysis)
        if matches and len(matches) > 0:                
                        # print(matches[0])
            updated_dict = ast.literal_eval(matches[0])
            user_answers.update(updated_dict)
                        # for i in matches[0].keys():
                        #         if i in user_answers:
                        #             user_answers[i]=matches[0][i]
                        # user_answers = user_answers | matches[0]
            qps.update_assessment(score_range, percent_completed, category_scores, user_answers)            
            return user_answers, analysis
        
    return user_answers, False

def page_config(static_files_folder):
    try:
        st.set_page_config(
            page_title='Karma Coordinates',
            page_icon=f'{static_files_folder}/favicon.ico',
            layout='wide'
        )    
    except:
        pass

def run_app():
    static_files_folder = '.static'
    page_config(static_files_folder)
    smf.init()
    af.identity_msg()
    initial_assessment = True
    latest_user_answers = {}
    if st.session_state.auth:
        # fetch latest record if any
        response = db.query(st.session_state.user_answers['email'], 'latest')
        if response and len(response) > 0:
            if 'journal_entry' in st.session_state.user_answers:
                st.session_state.user_answers['journal_entry'] = ''
            # second parameter takes precedence
            st.session_state.user_answers = {**response[0], **st.session_state.user_answers}
            initial_assessment = False

    web_content.intro(static_files_folder)
    openai_assistant_chat.prompt()
    web_content.brief(static_files_folder)

    st.subheader('Make a journal entry')
    jf.journal_entry()

    st.subheader('Calculate my Karma Coordinates')
    show_assessment_questionnaire = not (not initial_assessment and st.session_state.user_answers['journal_entry'])

    placehoder = st.empty()
    features_df, score_range, percent_completed, category_scores, user_answers, score_ai_analysis_query = qps.assessment(placehoder=placehoder, show_assessment_questionnaire=show_assessment_questionnaire)

    if not show_assessment_questionnaire:
        plh = st.empty()
        user_answers, analysis = _update_assessment(features_df, score_range, percent_completed, category_scores, user_answers, plh)
        score_ai_analysis_query = user_answers['score_ai_analysis_query']
    
    if st.session_state.auth:
        st.subheader('My progress')
        pf.clickable_progress_chart()
        
    pf.bell_curve()        

    if 'karma_coordinates' in st.session_state:
        st.subheader('AI analysis')
        plh = st.container(border=True)
        query=None
        analysis=False
        with plh:
            clicked = st.button('Show and explain my score')
            if clicked:
                query = f'''Explain {score_ai_analysis_query}'''
                print(f'clicked query is: {query}')
                openai_assistant_chat.prompt_specific(query=query, ai_query=query, plh=plh)     
                analysis = openai_assistant_chat.get_assistant_answer_from_cache(query)

        pdf.download_pdf(user_answers, st.session_state.karma_coordinates, analysis)

    st.subheader('Your feedback')
    with st.container(border=True):
        web_content.request_feedback_note()
        ff.user_feedback(user_answers, percent_completed)

    web_content.sankhya_references(static_files_folder)
    sp.subscribe()


def main():
    # static_files_folder = '.static'
    # page_config(static_files_folder)
    run_app()

if __name__ == '__main__': 
    main()

