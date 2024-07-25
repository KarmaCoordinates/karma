import streamlit as st
import file_functions as ff
import functions
import web_content 

@st.cache_data
def cache_model(model_choice, bucket_name, features_data_file, pickled_model_data_file):
    df = ff.load_csv(bucket_name, features_data_file)
    df, X, y, label_encoder = functions.read_features(df)
    categorical_cols, numeric_cols, preprocessor = functions.encode_features(X)
    model, X_train, X_test, y_train, y_test = functions.define_model(X, y, model_choice, preprocessor)
    model = ff.load_pickle_obj_from_s3(bucket_name, pickled_model_data_file)

    accuracy, conf_matrix = functions.model_eval(model, X_test, y_test)

    return df, X.columns, categorical_cols, model, label_encoder, accuracy, conf_matrix

def run_app():

    bucket_name = 'karmacoordinates'
    features_data_file = 'kc3_synthout_chunk_0.csv'
    pickled_model_data_file = 'kc_model_finalized.sav'

    resources_folder = 'resources'
    web_content.brief(resources_folder)

    model_choice = 'RandomForest'
    df, columns, categorical_cols, model, label_encoder, accuracy, conf_matrix = cache_model(model_choice, bucket_name, features_data_file, pickled_model_data_file)


    functions.show_stats(df)
    functions.show_eda(df, columns, categorical_cols)
    functions.show_models()

    functions.model_perf(accuracy, conf_matrix)

    input_df, user_input = functions.show_user_input(df, columns, categorical_cols)      
    prediction, prediction_label = functions.make_prediction(model, label_encoder, input_df)  
    functions.show_prediction(prediction_label)

    pdf = functions.create_pdf(input_df, prediction)
    functions.download_pdf(pdf, user_input, prediction_label)


run_app()

