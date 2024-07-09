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


# locally or web
running_locally = True

def write_content(resources_folder):
    # title
    st.title('Karma Coordinates Calculator App')

    # web content
    st.image(f'{resources_folder}/kapil-muni-image.png', caption='Kapil muni 5000 BC')

    pdf = f'<a href="{resources_folder}/samkhya-karika.pdf">pdf</a>'

    txt = f'''According to Sankhya-yoga, Prakriti (the universe) exists for providing
    experiences to Purush. Purush upon realization that “I exist” is liberated
    (Moksha). Every life-form in Prakriti is engaged in providing experiences to a
    Purush. Once  all Purush are awakened, the Prakriti’s work is complete and it
    collapses into a singularity and the next cycle is started with a big-bang. As
    per the open model with omega of 6, universe is 6 billion years old and it
    will end when it is about 13 billion years old - that is in another 7
    billion years. (https://en.wikipedia.org/wiki/Ultimate_fate_of_the_universe) 

    A life-form comes into an existence due to a microscopic particle in
    nature called as Sukshm. It is Sukshm that gets tinged with the acquired 
    tendencies (Bhavas), from life-form to life-form! Once all tendencies are 
    overcome/consumed, Moksha is achieved. A human life is the only known form 
    of Sukshm that is capable of achieving Moksha for its Purush. Sankhya-yoga 
    quantifies and explains attributes (Gunas) and tendencies (Bhavas) that can 
    take a life form closer to achieving Moksha. 

    Karma Coordinates is a fun app developed to approximate based on your Gunas and 
    Bhavas your current position in this karmic journey of many lives until Moksha. 
    A score of 11/13 means you are at about 11 billion year mark - very near 
    to achieving the awakening state.  A score of 7/13 means you are at 7 billion 
    year mark, ahead but can speed it up by certain lifestyle based changes. 

    Karma Coordinates outcome is also explained in terms of three Gunas - Satva, 
    Rajas and Tamas:  
    - Satva is the light (Prakash) property in the Prakriti. The neural network 
    in our brain - our intellect - has the highest Satva. 
    - Rajas is the energy property in the Prakriti. It moves mass. It activates. 
    Our mind and bodies are enabled by Rajas. 
    - Tamas is the mass property in the Prakriti - The flesh and bones of our body 
    has the highest Tamas.  
    '''

    st.markdown(txt)

# Load the data
@st.cache_data
def load_data(resources_folder):
    df = pd.read_csv(f'{resources_folder}/kc3_synthout_chunk_0.csv')
    df = df.drop(columns=['scaled_level', 'karma_coordinates'])

    # Encode the target variable
    label_encoder = LabelEncoder()
    df['karma_coordinates_label'] = label_encoder.fit_transform(df['karma_coordinates_label'])

    # Split the data into features and target
    X = df.drop(columns=['karma_coordinates_label'])
    y = df['karma_coordinates_label']

    return df, X, y, label_encoder


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

#print('0')


def show_models():
    # User selects the model
    st.subheader('Modeling')
    model_choice = st.selectbox('Select Model', ('RandomForest', 'LogisticRegression'))


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



#print('1')

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
        if col in categorical_cols:
            user_input[col] = st.selectbox(f'{col}', df[col].unique(), help=f'Select the value for {col}')
        else:
            user_input[col] = st.number_input(f'{col}', float(df[col].min()), float(df[col].max()), float(df[col].mean()), help=f'Input the value for {col}')

    # Convert user input to DataFrame
    input_df = pd.DataFrame(user_input, index=[0])

    return input_df, user_input

#print('2')

# Make prediction
def make_prediction(model, label_encoder, input_df):
    prediction = model.predict(input_df)
    prediction_label = label_encoder.inverse_transform(prediction)
    return prediction, prediction_label


#print('3')

# Display prediction
def show_prediction(prediction_label):
    st.subheader('AI prediction')
    st.write(f'# Your Karma Coordinates: **{prediction_label[0]}**')
    #st.write('The prediction above indicates the most likely karma coordinates label based on the input features provided.')

# User feedback
def show_user_feedback():
    st.subheader('Feedback')
    satva_choice = st.selectbox('Satva', ('Dominant', 'High', 'Moderate', 'Low'))
    tamas_choice = st.selectbox('Tamas', ('Low', 'Moderate', 'High', 'Dominant'))

    st.subheader('Include your zodiac sign and horoscope in calculations')

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


def main(show_eda, local_env):
    # hide EDA
    show_eda = False
    if local_env:
        resources_folder = 'karma/resources'
    else:
        resources_folder = 'resources'


    write_content(resources_folder)

    model_choice = 'RandomForest'
    df, X, y, label_encoder = load_data(resources_folder)
    categorical_cols, numeric_cols, preprocessor = encode_features(X)


    if show_eda: 
        show_stats(df)
        show_eda(df, X, categorical_cols)
        show_models()

    model, X_test, y_test = train_model(X, y, model_choice, preprocessor)
    accuracy, conf_matrix = model_eval(model, X_test, y_test)

    if show_eda:
        model_perf(accuracy, conf_matrix)

    input_df, user_input = show_user_input(df, X, categorical_cols)      
    prediction, prediction_label = make_prediction(model, label_encoder, input_df)  
    show_prediction(prediction_label)

    pdf = create_pdf(input_df, prediction)
    download_pdf(pdf, user_input, prediction_label)


main(False, False)
