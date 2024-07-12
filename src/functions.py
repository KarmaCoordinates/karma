import math
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
from fpdf import FPDF
import base64


# Load the data
@st.cache_data
def load_data(resources_folder):
    df = pd.read_csv(f'{resources_folder}/kc3_synthout_chunk_0.csv')
    df = df.drop(columns=['scaled_level'])
    df['knowledge'] = df['knowledge'].astype(str)

    # Encode the target variable
    label_encoder = LabelEncoder()
    df['karma_coordinates'] = label_encoder.fit_transform(round(df['karma_coordinates']))

    # Split the data into features and target
    X = df.drop(columns=['karma_coordinates'])
    y = df['karma_coordinates']

    return df, X, y, label_encoder

@st.cache_data
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
@st.cache_data
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
def show_eda(df, X, categorical_cols):
    st.subheader('Exploratory Data Analysis')
    for col in X.columns:
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


@st.cache_data
def train_model(X, y, model_choice, _preprocessor):
        # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create a model pipeline based on user choice
    if model_choice == 'RandomForest':
        model = make_pipeline(_preprocessor, RandomForestClassifier(random_state=42))
    elif model_choice == 'LogisticRegression':
        model = make_pipeline(_preprocessor, LogisticRegression(random_state=42))

    # Train the model
    model.fit(X_train, y_train)

    return model, X_test, y_test


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
def show_user_input(df, X, categorical_cols):
    st.subheader('Calculate my Karma Coordinates')
    user_input = {}
    for col in X.columns:
        #hint =  column_hints()[col].iloc[0]
        if col in categorical_cols:
            user_input[col] = st.selectbox(f'{col}', df[col].unique(), help=f'Select {col}', key=f'kk_inputs_{col}')
        else:
            user_input[col] = st.number_input(f'{col}', float(df[col].min()), float(df[col].max()), float(df[col].mean()), help=f'Input the value for {col}')

    # Convert user input to DataFrame
    input_df = pd.DataFrame(user_input, index=[0])

    return input_df, user_input

# Make prediction
def make_prediction(model, label_encoder, input_df):
    prediction = model.predict(input_df)
    prediction_label = label_encoder.inverse_transform(prediction)
    return prediction, prediction_label

def calculate_karma_coordinates(prediction_label):
    # 5 billion years, prediction_lables are from 5-13 (in billion years)
    current_distance = 5 
    # total number of default human life existences
    possible_human_existences = 13000000000 / 100 
    dominant_satva_efficiency = 1000000
    high_satva_efficiency = 100000
    moderate_satva_efficiency = 10000
    low_satva_efficiency = 1000
    default_satva_efficiency = 100
    # Dominant satva means 1 year of life = 1000000, High satva means 1 year of life = 100000, Moderage satva means 1 year of life = 10000 years, Low satva means 1 year of life = 10 years of progress
    if prediction_label > 11:
        satva_multiplier = dominant_satva_efficiency
    elif prediction_label > 9:
        satva_multiplier = high_satva_efficiency
    elif prediction_label > 7:
        satva_multiplier = moderate_satva_efficiency
    elif prediction_label > 5:
        satva_multiplier = low_satva_efficiency
    else:
        satva_multiplier = default_satva_efficiency

    slope = (prediction_label / current_distance) * (satva_multiplier * prediction_label)
    remaining_lives = (possible_human_existences / slope)
    return f'{math.trunc(remaining_lives):,}'
    #return remaining_lives

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
    lives_remaining = calculate_karma_coordinates(prediction_label[0])
    st.subheader('AI prediction')
    st.markdown(f'# Your Karma Coordinates: **{lives_remaining}** lives to Moksha.')

# User feedback
def show_user_feedback():
    st.subheader('Feedback')
    satva_choice = st.selectbox('Satva', ('Dominant', 'High', 'Moderate', 'Low'), key='satva_feedback')
    tamas_choice = st.selectbox('Tamas', ('Low', 'Moderate', 'High', 'Dominant'), key='tamas_feedback')

def horoscope_calculation():
    st.subheader('Include your zodiac sign and horoscope in calculations')

def improving_karma_coordinates():
    st.subheader('Improve Karma Coordinates')

# Option to download the result as PDF
def create_pdf(input_data, prediction):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Karma Coordinates Prediction Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.cell(200, 10, txt="Input Features:", ln=True)
    for key, value in input_data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
    
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Predicted Karma Coordinates Label: {prediction}", ln=True)
    
    return pdf

def download_pdf(pdf, user_input, prediction_label):
    st.subheader('Download Prediction as PDF')
    if st.button('Generate PDF Report'):
        pdf = create_pdf(user_input, prediction_label[0])
        pdf_output = pdf.output(dest='S').encode('latin1')
        b64 = base64.b64encode(pdf_output).decode('latin1')
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="prediction_report.pdf">Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)

