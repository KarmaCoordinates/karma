# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe
import streamlit as st
from streamlit.components.v1 import html

def subscribe():
    st.subheader('Donate to support this open source community initiative')
    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown('[Subscribe](https://buy.stripe.com/14keWy5LffpzeKkaEE) for unlimited AI (ChatGPT) queries into Indian epics and spiritual content such as Sankhya, Yoga, Vedas, Upanishad, Ramayan, Mahabharat, etc. AI indexing and querying is costly. Your support will go a long way in bringing ancient Indian epics and philosophy doctrines to everyone.')
    with col2:
        st.image('.static/qr_14keWy5LffpzeKkaEE.png', width=100)


def main():
    pass

if __name__ == '__main__': main()
