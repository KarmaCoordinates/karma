import functions
import web_content 
import streamlit as st
import file_functions as ff

@st.cache_data
def cache_model(model_choice, bucket_name, features_data_file, pickled_model_data_file):
    data_dictionary_file = 'data_dictionary.csv'
    data_dictionary_df = ff.load_csv(bucket_name, data_dictionary_file)
    data_dictionary_df = data_dictionary_df.iloc[1:9, 0:3] # first row is headers, get first 8 rows and first three columns only
    data_dictionary_array = data_dictionary_df.to_numpy()


    df = ff.load_csv(bucket_name, features_data_file)
    df, X, y, label_encoder = functions.read_features(df)
    categorical_cols, numeric_cols, preprocessor = functions.encode_features(X)
    model, X_train, X_test, y_train, y_test = functions.define_model(X, y, model_choice, preprocessor)
    model = ff.load_obj(bucket_name, pickled_model_data_file)
    return data_dictionary_array, df, X.columns, categorical_cols, model, label_encoder


def run_app():
    bucket_name = 'karmacoordinates'
    features_data_file = 'kc3_synthout_chunk_0.csv'
    pickled_model_data_file = 'kc_model_finalized.sav'



    static_files_folder = '.static'
    web_content.write_content(static_files_folder)

    model_choice = 'RandomForest'

    data_dictionary_array, df, columns, categorical_cols, model, label_encoder = cache_model(model_choice, bucket_name, features_data_file, pickled_model_data_file)

    # accuracy, conf_matrix = functions.model_eval(model, X_test, y_test)

    input_df, user_input = functions.show_user_input(data_dictionary_array, df, columns, categorical_cols)   

    prediction, prediction_label = functions.make_prediction(model, label_encoder, input_df)  
    functions.show_prediction(prediction_label)
    functions.explain_prediction(prediction_label)

    pdf = functions.create_pdf(input_df, prediction)
    functions.download_pdf(pdf, user_input, prediction_label)

    # web_content.request_feedback_note()
    # functions.show_user_feedback()

    web_content.write_sankhya_references()

run_app()

