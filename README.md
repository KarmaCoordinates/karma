# karma
# load model into s3 
python src/model_app.py  

# update white paper html
python src/whitepaper_to_html.py

# run streamlit app
streamlit run src/streamlit_app.py

# run fastapi app
## development
fastapi dev src/fastapi_app.py 
## production
fastapi run src/fastapi_app.py 

