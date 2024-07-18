import functions
import file_functions as ff


def run_app():
    bucket_name = 'karmacoordinates'
    features_data_file = 'kc3_synthout_chunk_0.csv'
    model_data_file = 'kc_model_finalized.sav'

    # web_content.write_content(resources_folder)

    model_choice = 'RandomForest'
    df, X, y, label_encoder = functions.read_features_file(bucket_name, features_data_file)
    categorical_cols, numeric_cols, preprocessor = functions.encode_features(X)

    # functions.show_models()

    model, X_train, X_test, y_train, y_test = functions.define_model(X, y, model_choice, preprocessor)

    print('Training model')
    model = functions.train_model(model, X_train, y_train)

    print('Saving model')
    ff.save_obj(model, bucket_name, model_data_file)

    print('Model trained and saved. You can exit now!')

run_app()

