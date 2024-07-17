import functions
import web_content 


def run_app():
    resources_folder = 'resources'


    web_content.write_content(resources_folder)

    model_choice = 'RandomForest'
    df, X, y, label_encoder = functions.read_features_file('karmacoordinates', 'kc3_synthout_chunk_0.csv')
    categorical_cols, numeric_cols, preprocessor = functions.encode_features(X)


    functions.show_stats(df)
    functions.show_eda(df, X, categorical_cols)
    functions.show_models()

    model, X_test, y_test = functions.train_model(X, y, model_choice, preprocessor)
    accuracy, conf_matrix = functions.model_eval(model, X_test, y_test)

    functions.model_perf(accuracy, conf_matrix)

    input_df, user_input = functions.show_user_input(df, X, categorical_cols)      
    prediction, prediction_label = functions.make_prediction(model, label_encoder, input_df)  
    functions.show_prediction(prediction_label)

    pdf = functions.create_pdf(input_df, prediction)
    functions.download_pdf(pdf, user_input, prediction_label)


run_app(False)

