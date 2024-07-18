import functions
import web_content 
import streamlit as st
import file_functions as ff


@st.cache_data
def cache_model(bucket_name, features_data_file):
    model_choice = 'RandomForest'
 
    df, X, y, label_encoder = functions.read_features_file(bucket_name, features_data_file)
    categorical_cols, numeric_cols, preprocessor = functions.encode_features(X)
    model, X_train, X_test, y_train, y_test = functions.define_model(X, y, model_choice, preprocessor)
    return df, X, y, label_encoder, categorical_cols, model, X_test, y_test

@st.cache_data
def cached_model_eval(_model, X_test, y_test):
    return functions.model_eval(_model, X_test, y_test)

@st.cache_data
def cached_load_pickle_data(bucket_name, object_key):
    model = ff.load_obj(bucket_name, object_key)
    return model

def run_app():
    bucket_name = 'karmacoordinates'
    features_data_file = 'kc3_synthout_chunk_0.csv'
    pickled_model_data_file = 'kc_model_finalized.sav'

    resources_folder = 'resources'
    web_content.write_content(resources_folder)

    model_choice = 'RandomForest'
    df, X, y, label_encoder, categorical_cols, model, X_test, y_test = cache_model(bucket_name, features_data_file)

    model = cached_load_pickle_data(bucket_name, pickled_model_data_file)

    accuracy, conf_matrix = cached_model_eval(model, X_test, y_test)

    input_df, user_input = functions.show_user_input(df, X, categorical_cols)      
    prediction, prediction_label = functions.make_prediction(model, label_encoder, input_df)  
    functions.show_prediction(prediction_label)
    functions.explain_prediction(prediction_label)

    pdf = functions.create_pdf(input_df, prediction)
    functions.download_pdf(pdf, user_input, prediction_label)

    web_content.request_feedback_note()
    functions.show_user_feedback()

run_app()

