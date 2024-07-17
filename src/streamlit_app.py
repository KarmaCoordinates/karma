import functions
import web_content 
import streamlit as st

@st.cache_data
def cached_read_features_file(resources_folder):
    return functions.read_features_file(resources_folder)

@st.cache_data
def cached_encode_features(X):
    return functions.encode_features(X)

@st.cache_data
def cached_define_model(X, y, model_choice, _preprocessor):
    return functions.define_model(X, y, model_choice, _preprocessor)

def cached_model_eval(model, X_test, y_test):
    return functions.model_eval(model, X_test, y_test)

def run_app():

    resources_folder = 'resources'
    web_content.write_content(resources_folder)

    model_choice = 'RandomForest'
    df, X, y, label_encoder = cached_read_features_file(resources_folder)
    categorical_cols, numeric_cols, preprocessor = cached_encode_features(X)

    model, X_train, X_test, y_train, y_test = cached_define_model(X, y, model_choice, preprocessor)
    # print(f'X_train:{X_train}, X_test:{X_test}, y_train:{y_train}, y_test:{y_test}')

    model = functions.load_pickle_data(resources_folder, 'kc_model_finalized.sav')

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

