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

# To upload updated data files to s3
# use __runner.py utility
# for e.g. to upload prompt changes, call prompt_engine.save_prompt_in_s3()
# remember to delete the current .pkl file from the aws karma/.tmp as wll so it fetches the new file


