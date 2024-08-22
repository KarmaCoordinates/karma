import model_functions
import web_content 
import streamlit as st
import s3_functions as s3f
import openai_assistant_chat
import stripe_payment as sp
import questionnaire_pratyay_sargah as qps
import feedback_functions as ff
import pdf_functions as pf
import status_functions as sf

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

def run_app():
    static_files_folder = '.static'
    web_content.page_config(static_files_folder)

    web_content.intro(static_files_folder)

    # openai_assistant_chat.init()
    openai_assistant_chat.prompt()

    web_content.brief(static_files_folder)

    # model_choice = 'RandomForest'
    # bucket_name = 'karmacoordinates'
    # features_data_file = 'kc3_synthout_chunk_0.csv'
    # pickled_model_data_file = 'kc_model_finalized.sav'
    # data_dictionary_array, df, columns, categorical_cols, model, label_encoder = cache_model(model_choice, bucket_name, features_data_file, pickled_model_data_file)

    # accuracy, conf_matrix = functions.model_eval(model, X_test, y_test)


    st.subheader('Calculate my Karma Coordinates')
    with st.container(border=True):
        input_df, user_input, prediction, prediction_label = qps.process_questions()
        st.divider()
        st.subheader('AI analysis')
        plh = st.container()
        # clicked = st.button('Show and explain my score', on_click=openai_assistant_chat.prompt_specific, args=(qps.get_score(), plh))
        clicked = st.button('Show and explain my score')
        if clicked:
            # plh.markdown('clicked and here')
            openai_assistant_chat.prompt_specific(qps.get_score(), plh)    
            st.session_state['analysis_done'] = True

        # score_md = qps.show_score()
        # openai_assistant_chat.prompt_specific(str(score_md))


    # with st.container(border=True):
    #     input_df, user_input = model_functions.show_user_input(data_dictionary_array, df, columns, categorical_cols)   

    # prediction, prediction_label = model_functions.make_prediction(model, label_encoder, input_df)  
    # model_functions.show_prediction(prediction_label)
    # model_functions.explain_prediction(prediction_label)

        if 'analysis_done' in st.session_state and st.session_state.analysis_done:
            pdf = pf.create_pdf(user_input, qps.get_score())
            pf.download_pdf(pdf)

            web_content.request_feedback_note()
            feedback = ff.show_user_feedback(user_input)
            # print(f'before {user_input}')
            user_input.update(feedback)
            # print(f'after {user_input}')
            ff.save_user_feedback(user_input)

    web_content.sankhya_references(static_files_folder)

    sp.subscribe()
    
    sf.update_ui_status('loading', 'Complete')


run_app()

