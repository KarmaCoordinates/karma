# to-be architecture
ALB listening on port 443, terminating SSL traffic.
Use Amazon ACM to generate your certificate and attach this to your HTTPS listener.
ALB Target Group sending traffic unencrypted to port 80 on the instance.
Security group for instances only allows port 80 access from your ALB.


#create certbot certs
# https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal
certonly --webroot --webroot-path=/var/www/html --email sdixit@ohioedge.com --agree-tos --no-eff-email --staging -d karmacoordinates.org  -d www.karmacoordinates.org


# route 8051 to 80
#ngix config
sudo vi /etc/nginx/sites-enabled/streamlit
## add to streamlit file
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
