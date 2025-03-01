# karma
# load model into s3 
python src/model_app.py  

# update white paper html
python src/whitepaper_to_html.py

# run app
streamlit run src/streamlit_app.py