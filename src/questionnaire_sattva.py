import streamlit as st

# Function to calculate Sattva level based on user responses
def calculate_sattva_score(responses):
    return sum(responses)

# Streamlit app
st.title("Sattva Levels Assessment")

st.header("Answer the following questions:")

# Questions and options
questions = [
    "1. How often do you feel calm and peaceful in your daily life?",
    "2. When faced with a challenging situation, how do you typically respond?",
    "3. How do you handle negative emotions?",
    "4. How often do you engage in activities that promote your well-being (such as meditation, yoga, spending time in nature)?",
    "5. How do you view your relationships with others?"
]

options = [
    ["A) Rarely", "B) Sometimes", "C) Usually", "D) Always"],
    ["A) I react impulsively and with agitation.", 
     "B) I feel stressed but try to cope with it.", 
     "C) I analyze the situation and try to respond thoughtfully.", 
     "D) I remain calm and find a solution without panic."],
    ["A) I tend to suppress them or ignore them.", 
     "B) I express them immediately, often with anger or frustration.", 
     "C) I acknowledge them and try to understand their cause.", 
     "D) I process my emotions calmly and seek constructive outlets."],
    ["A) Never", "B) Occasionally", "C) Frequently", "D) Daily"],
    ["A) I struggle to connect with others.", 
     "B) I have conflicts and misunderstandings often.", 
     "C) I maintain good relationships with minor conflicts.", 
     "D) I cultivate harmonious and mutually supportive relationships."]
]

# Response storage
responses = []

# Create a selectbox for each question
for i, question in enumerate(questions):
    response = st.radio(question, options[i])
    # Map responses to scores
    if response.startswith("A"):
        responses.append(1)
    elif response.startswith("B"):
        responses.append(2)
    elif response.startswith("C"):
        responses.append(3)
    elif response.startswith("D"):
        responses.append(4)

# Calculate and display result when user clicks the button
if st.button("Submit"):
    score = calculate_sattva_score(responses)
    st.write(f"Your total Sattva score is: {score}")

    # Provide feedback based on score
    if score <= 10:
        st.write("Your Sattva levels are low. Consider focusing on calming activities and emotional regulation.")
    elif 11 <= score <= 15:
        st.write("Your Sattva levels are moderate. Keep working on your well-being.")
    elif 16 <= score <= 20:
        st.write("Your Sattva levels are high. Maintain your healthy habits.")
    else:
        st.write("Your Sattva levels are very high. You have excellent clarity and peace of mind!")

# Run the app using the command: streamlit run your_script_name.py