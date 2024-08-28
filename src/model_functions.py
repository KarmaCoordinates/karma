import pandas as pd
import numpy as np
import sklearn 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import accuracy_score, confusion_matrix
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import s3_functions as s3f
import state_mgmt_functions as sf
import score_functions as scf


prediction_init = False

# Load the data
def read_features(df):
    df = df.drop(columns=['scaled_level'])
    df['knowledge'] = df['knowledge'].astype(str)

    # Encode the target variable
    label_encoder = LabelEncoder()
    df['karma_coordinates'] = label_encoder.fit_transform(round(df['karma_coordinates']))

    # Split the data into features and target
    X = df.drop(columns=['karma_coordinates'])
    y = df['karma_coordinates']

    return df, X, y, label_encoder

def column_hints():
    df = pd.DataFrame(np.array([['How often you feel sad, depressed, etc.', 'How often you feel happy, excited, etc.', 
                                 'Do you read philosophical literature and/or practice spiritutality',
                                 'How often you drink, smoke, etc.', 'How often you work out.', 'Do you eat healthy.', 
                                 'Number of years of education or equivalent experience', 'What is your professional line of work']]), 
                      columns=['negative_emotion', 'positive_emotion', 'spirituality', 'drink', 'workout', 'diet', 'knowledge', 'discipline'])
    return df


# Overall Statistics
def show_stats(df):
    st.subheader('Overall Statistics')
    st.write(df.describe(include='all'))


# Encode categorical features
def encode_features(X):
    categorical_cols = X.select_dtypes(include=['object']).columns
    numeric_cols = X.select_dtypes(include=['number']).columns

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', SimpleImputer(strategy='mean'), numeric_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
        ])
    return categorical_cols, numeric_cols, preprocessor


# Exploratory Data Analysis (EDA)$
def show_eda(df, columns, categorical_cols):
    st.subheader('Exploratory Data Analysis')
    for col in columns:
        fig, ax = plt.subplots()
        if col in categorical_cols:
            sns.countplot(x=df[col], ax=ax)
            st.pyplot(fig)
            st.write(f'The plot above shows the distribution of the {col} feature. It represents the count of each category present in the dataset.')
        else:
            sns.histplot(df[col], kde=True, ax=ax)
            st.pyplot(fig)
            st.write(f'The plot above shows the distribution of the {col} feature. It represents the frequency of different values within this numerical feature. The line indicates the density of the values.')


def show_models():
    # User selects the model
    st.subheader('Modeling')
    model_choice = st.selectbox('Select Model', ('RandomForest', 'LogisticRegression'), key='models')


def define_model(X, y, model_choice, _preprocessor):
        # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    # Create a model pipeline based on user choice
    if model_choice == 'RandomForest':
        model = make_pipeline(_preprocessor, RandomForestClassifier(random_state=42))
    elif model_choice == 'LogisticRegression':
        model = make_pipeline(_preprocessor, LogisticRegression(random_state=42))


    return model, X_train, X_test, y_train, y_test

def train_model(model, X_train, y_train):
    # Train the model
    model = model.fit(X_train, y_train)
    return model


# Model evaluation
def model_eval(model, X_test, y_test):
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)
    return accuracy, conf_matrix

# Display model performance
def model_perf(accuracy, conf_matrix):
    st.subheader('Model Performance')
    st.write(f'Accuracy: {accuracy:.2f}')
    st.write('Accuracy represents the proportion of correct predictions made by the model out of all predictions. It is a measure of how well the model is performing.')

    st.subheader('Confusion Matrix')
    fig, ax = plt.subplots()
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', ax=ax)
    st.pyplot(fig)
    st.write('The confusion matrix shows the number of correct and incorrect predictions made by the model. Each row represents the actual class, while each column represents the predicted class. The diagonal values indicate correct predictions.')

# Create input fields for user
def show_user_input(data_dictionary_array, df, columns, categorical_cols):
    st.subheader('Calculate my Karma Coordinates')
    user_input = {}
    for row in data_dictionary_array:
        feature_name = row[0]
        display_name = row[1]
        hint = row[2]
        #hint =  column_hints()[col].iloc[0]
        if feature_name in categorical_cols:
            key1 = f'kk_inputs_{feature_name}'
            user_input[feature_name] = st.selectbox(f'{display_name}', df[feature_name].unique(), help=f'Answer the question: {hint}', key=key1, on_change=sf.update_ui_status, args=(key1, True))
        else:
            user_input[feature_name] = st.number_input(f'{display_name}', float(df[feature_name].min()), float(df[feature_name].max()), float(df[feature_name].mean()), help=f'Answer the question: {hint}', key=key1, on_change=sf.update_ui_status, args=(key1, True))

    # Convert user input dict to DataFrame
    input_df = pd.DataFrame(user_input, index=[0])

    return input_df, user_input



def explain_prediction(prediction_label):
    df = pd.DataFrame([['Extra-ordinary', 'Extra-ordinary', 'Extra-ordinary', 'Extra-ordinary', 'Extra-ordinary', 'Extra-ordinary'], 
                       ['Well-developed', 'Well-developed', 'Well-developed', 'Well-developed', 'Well-developed', 'Well-developed']], 
                       columns=('Reasoning', 'Vocabulary', 'Dedicated Effort', '3 Knowledge to overcome sorrows', 'Acquisition of good people', 'Giving'))
    #st.write(df)

    if prediction_label > 11:
        return '''
        Satva=Dominant, Tamas=Very-Low  
        *You have developed exceptional reasoning mind. 
        You have developed exceptional skills to use words wisely and also understanding the meaning of what others say to you.
        You have developed exceptional discipline to work on tasks at hand.
        You have acquired company of good people. You give. 
        You are a balanced person who doesn't get perturbed often.* 
        '''
    elif prediction_label > 9:
        return '''High Awakening! Satva=High, Tamas=Low  
        '''
    elif prediction_label > 7:
        return '''Moderate Awakening! Satva=Moderate, Tamas=Moderate  
        '''
    elif prediction_label > 5:
        return '''Low Awakening! Satva=Low, Tamas=High  
        '''
    else:
        return '''Wake up! Satva=Very-Low, Tamas=Dominant  
        '''


# Display prediction
def show_prediction(prediction_label):
    lives_remaining = scf.calculate_karma_coordinates(prediction_label[0])
    st.subheader('AI prediction')
    # all not rating clicks are assumed to be selectbox on_clicks
    global prediction_init
    if prediction_init or sf.is_loading('kk_inputs_'):
        if not prediction_init: prediction_init = True
        prediction = f'''>## Your Karma Coordinates: :green[**{lives_remaining}**] lives to Moksha.'''
        st.markdown(prediction)

# Make prediction
def make_prediction(model, label_encoder, input_df):
    prediction = model.predict(input_df)
    prediction_label = label_encoder.inverse_transform(prediction)
    return prediction, prediction_label


def horoscope_calculation():
    st.subheader('Include your zodiac sign and horoscope in calculations')

def improving_karma_coordinates():
    st.subheader('Improve Karma Coordinates')

def main():
    pass

if __name__ == '__main__': main()
