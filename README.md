# karma
#ngix config
sudo vi /etc/nginx/sites-enabled/streamlit
server {
    listen 80;
    server_name karmacoordinates.org;
    location / {
        proxy_pass http://3.16.169.174:8501/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

sudo rm /etc/nginx/sites-enabled/default

sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/streamlit

sudo systemctl start nginx
sudo systemctl enable nginx


# run from ec2
nohup streamlit run src/streamlit_app.py &