import streamlit as st
import questionnaire_pratyay_sargah as qps
import s3_functions as s3f
import pandas as pd
import unicodedata
import secrets_app as sa
import configs as cfg
import smtplib

def test1(token):

    # Create a placeholder
    placeholder = st.empty()

    # Use the placeholder to create input elements
    with placeholder.container():
        user_input = st.text_input("Enter something:")
        submit_button = st.button("Submit")

    # Logic for clearing the input
    if submit_button:
        # Perform some action with the input
        st.write(f'You entered: {user_input}')

        # Clear the placeholder
        placeholder.empty()
        # Optional: Repopulate or handle the presence of input elements again if requir

def test2():

    # Create a layout with 2 columns
    col1, col2 = st.columns(2)

    # Add elements to the first column (col1)
    with col1:
        input_text = st.text_input("Enter some text:", "")
        submit_button = st.button("Submit")

    # Add some static text to the second column (col2)
    with col2:
        st.write("This is a static text in column 2.")

    # Logic to handle what happens when the button is pressed
    if submit_button:
        # If the button is pressed, display the input in column 2
        col2.write(f"You entered: {input_text}")

        # Clear the input elements in col1
        col1.empty()
        with col1:
            st.markdown('')
        # Optionally, you can re-add elements to col1 if needed
        # with col1:
        #     st.write("Input cleared, please enter new text:")
        #     st.text_input("Enter some text:", "")    

def main():
    test2()

if __name__ == '__main__': main()
