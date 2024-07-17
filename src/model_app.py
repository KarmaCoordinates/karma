import functions
import web_content 
import file_functions as ff


def run_app():
    resources_folder = 'resources'

    # web_content.write_content(resources_folder)

    model_choice = 'RandomForest'
    df, X, y, label_encoder = functions.read_features_file('karmacoordinates', 'kc3_synthout_chunk_0.csv')
    categorical_cols, numeric_cols, preprocessor = functions.encode_features(X)

    # functions.show_models()

    model, X_train, X_test, y_train, y_test = functions.define_model(X, y, model_choice, preprocessor)
    print(f'X_train:{X_train}, X_test:{X_test}, y_train:{y_train}, y_test:{y_test}')

    print('Training model')
    model = functions.train_model(model, X_train, y_train)

    print('Saving model')
    kc_model_final = 'kc_model_finalized.sav'
    ff.save_data_using_pickle(model, resources_folder, kc_model_final)

    print('Model trained and saved. You can exit now!')

run_app()

