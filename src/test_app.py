import streamlit as st
import questionnaire_pratyay_sargah as qps
import s3_functions as s3f
import pandas as pd
import unicodedata
import secrets_app as sa
import configs as cfg
import smtplib

def test1(token):
    print(f'{token}')

def main():
    content = test1('123abcd')

if __name__ == '__main__': main()
