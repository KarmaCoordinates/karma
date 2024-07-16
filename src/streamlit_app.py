import functions
import web_content 


def run_app():

    resources_folder = 'resources'


    web_content.write_content(resources_folder)

    model_choice = 'RandomForest'
    df, X, y, label_encoder = functions.load_data(resources_folder)
    categorical_cols, numeric_cols, preprocessor = functions.encode_features(X)

    model, X_train, X_test, y_train, y_test = functions.define_model(X, y, model_choice, preprocessor)
    # print(f'X_train:{X_train}, X_test:{X_test}, y_train:{y_train}, y_test:{y_test}')

    model = functions.load_model(resources_folder)

    accuracy, conf_matrix = functions.model_eval(model, X_test, y_test)

    input_df, user_input = functions.show_user_input(df, X, categorical_cols)      
    prediction, prediction_label = functions.make_prediction(model, label_encoder, input_df)  
    functions.show_prediction(prediction_label)
    functions.explain_prediction(prediction_label)

    pdf = functions.create_pdf(input_df, prediction)
    functions.download_pdf(pdf, user_input, prediction_label)

    web_content.request_feedback_note()
    functions.show_user_feedback()

run_app()

