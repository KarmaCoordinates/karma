import functions
import web_content 
import streamlit as st
import file_functions as ff
import openai_assistant_chat
# import llama_chat



@st.cache_data
def cache_model(model_choice, bucket_name, features_data_file, pickled_model_data_file):
    data_dictionary_file = 'data_dictionary.csv'
    data_dictionary_df = ff.cache_csv_from_s3(bucket_name, data_dictionary_file)
    data_dictionary_df = data_dictionary_df.iloc[1:9, 0:4] # first row is headers, get first 8 rows and first three columns only
    data_dictionary_array = data_dictionary_df.to_numpy()


    df = ff.cache_csv_from_s3(bucket_name, features_data_file)
    df, X, y, label_encoder = functions.read_features(df)
    categorical_cols, numeric_cols, preprocessor = functions.encode_features(X)
    model, X_train, X_test, y_train, y_test = functions.define_model(X, y, model_choice, preprocessor)
    model = ff.cache_pickle_obj_from_s3(bucket_name, pickled_model_data_file)
    return data_dictionary_array, df, X.columns, categorical_cols, model, label_encoder


def run_app():
    static_files_folder = '.static'
    web_content.set_page_config(static_files_folder)

    web_content.intro(static_files_folder)

    openai_assistant_chat.init()
    openai_assistant_chat.prompt()

    web_content.brief(static_files_folder)

    model_choice = 'RandomForest'
    bucket_name = 'karmacoordinates'
    features_data_file = 'kc3_synthout_chunk_0.csv'
    pickled_model_data_file = 'kc_model_finalized.sav'
    data_dictionary_array, df, columns, categorical_cols, model, label_encoder = cache_model(model_choice, bucket_name, features_data_file, pickled_model_data_file)

    # accuracy, conf_matrix = functions.model_eval(model, X_test, y_test)

    input_df, user_input = functions.show_user_input(data_dictionary_array, df, columns, categorical_cols)   

    prediction, prediction_label = functions.make_prediction(model, label_encoder, input_df)  
    functions.show_prediction(prediction_label)
    functions.explain_prediction(prediction_label)

    # web_content.write_paper(static_files_folder)

    pdf = functions.create_pdf(input_df, prediction)
    functions.download_pdf(pdf, user_input, prediction_label)

    web_content.request_feedback_note()
    feedback = functions.show_user_feedback(user_input)

    user_input.update(feedback)
    functions.save_user_feedback(user_input)

    web_content.sankhya_references(static_files_folder)

    functions.update_ui_status('loading', 'Complete')

    # openai_completions_chat.init()
    # openai_completions_chat.prompt()

    # llama_chat.init()
    # llama_chat.prompt(prompt)


run_app()

