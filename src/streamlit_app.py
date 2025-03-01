import ai.model_functions as model_functions
import web_content 
import streamlit as st
import storage.s3_functions as s3f
import ai.openai_assistant_chat as openai_assistant_chat
import payment.stripe_payment as sp
import assessment.questionnaire_pratyay_sargah as qps
import feedback.feedback_functions as ff
import analytics.pdf_functions as pdf
import security.auth_functions as af
import assessment.score_functions as sf
import journal.journal_functions as jf
import analytics.plot_functions as pf
import storage.dynamodb_functions as db
import streamlit_functions.state_mgmt_functions as smf
import quiz as qz

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
    hide_assessment_questionnaire = False
    if st.session_state.auth:
        qps.retrieve_previous_assessment()
        if st.session_state.previous_user_answers:
            hide_assessment_questionnaire = True
        # print(f'''jf.is_new(): {jf.is_new()}, st.session_state.previous_user_answers: {st.session_state.previous_user_answers}''')
        web_content.auth_overview(static_files_folder)
        openai_assistant_chat.prompt()
        st.subheader('Make a journal entry')
        new_journal_entry=jf.journal_entry()
    else:
        web_content.overview(static_files_folder)
        openai_assistant_chat.prompt()
        web_content.background(static_files_folder)
        qz.take_quiz()


    st.subheader('Calculate my Karma Coordinates')    
    placehoder = st.empty()
    percent_completed, score_ai_analysis_query = qps.assessment(placehoder=placehoder, hide_assessment_questionnaire=hide_assessment_questionnaire)
    
    if st.session_state.auth:
        st.subheader('My progress')
        pf.clickable_progress_chart()

    # st.subheader('How does your score compare?')
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
                openai_assistant_chat.prompt_specific(query=query, ai_query=query, plh=plh)     
                analysis = openai_assistant_chat.get_assistant_answer_from_cache(query)

        pdf.download_assessment_pdf(st.session_state.user_answers, st.session_state.karma_coordinates, analysis)

        if st.session_state.auth:
            st.subheader('Download Journal as PDF')    
            pdf.download_journal()

    if st.session_state.auth:
        st.subheader('Your feedback')
        with st.container(border=True):
            web_content.request_feedback_note()
            ff.user_feedback(st.session_state.user_answers, percent_completed)

    web_content.sankhya_references(static_files_folder)
    sp.subscribe()


def main():
    # static_files_folder = '.static'
    # page_config(static_files_folder)
    run_app()

if __name__ == '__main__': 
    main()

