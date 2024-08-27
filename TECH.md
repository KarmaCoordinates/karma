# to-be architecture
ALB listening on port 443, terminating SSL traffic.
Use Amazon ACM to generate your certificate and attach this to your HTTPS listener.
ALB Target Group sending traffic unencrypted to port 80 on the instance.
Security group for instances only allows port 80 access from your ALB.

# server
Canonical, Ubuntu, 24.04 LTS, amd64 noble image build on 2024-07-01
ami-0862be96e41dcbf74

# setup
git clone https://github.com/KarmaCoordinates/karma.git

sudo apt install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

# keys
kc-keys-sd.pem

#create certbot certs
sudo apt install snapd
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal

sudo certbot --nginx -d karmacoordinates.org -d www.karmacoordinates.org
email: sdixit@ohioedge.com

# route 8051 to 80 
# ref: https://eladnava.com/binding-nodejs-port-80-using-nginx/
#ngix config
sudo apt-get install nginx

sudo vi /etc/nginx/sites-available/karmacoordinates.org
## add to karmacoordinates.org file
server {
    listen 80;
    if ($host = www.karmacoordinates.org) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    if ($host = karmacoordinates.org) {
        return 301 https://$host$request_uri;
    } # managed by Certbot
}

server {
    listen 443 ssl;
    server_name www.karmacoordinates.org;
    ssl_certificate /etc/letsencrypt/live/karmacoordinates.org/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/karmacoordinates.org/privkey.pem; # managed by Certbot
    #other ssl options
    return 301 https://karmacoordinates.org$request_uri;


}

server {
    listen 443 ssl;
    server_name karmacoordinates.org;
    #your root, index, etc. stuff
    location / {
        proxy_pass http://127.0.0.1:8501/;
     proxy_set_header X-Real-IP $remote_addr;
     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
     proxy_set_header X-Forwarded-Proto https;
     proxy_set_header X-Forwarded-Port 443;
     proxy_set_header Host $host;

     # The following 5 lines you have to add for Streamlit to work with HTTPS
     proxy_http_version 1.1;
     proxy_set_header Upgrade $http_upgrade;
     proxy_set_header Connection "upgrade";
     proxy_buffering off;
     proxy_read_timeout 86400;
    }
    ssl_certificate /etc/letsencrypt/live/karmacoordinates.org/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/karmacoordinates.org/privkey.pem; # managed by Certbot
    #other ssl options
}

sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/karmacoordinates.org /etc/nginx/sites-enabled/karmacoordinates.org

sudo systemctl start nginx
sudo systemctl enable nginx

sudo nginx -t && sudo nginx -s reload
sudo service restart nginx


# s3 bucket - setup kc-dev access keys, security and us-east-2 default region
-- sudo apt install awscli
sudo snap install aws-cli --classic
aws configure
AWS Access Key ID [None]: kc-dev-key_id
AWS Secret Access Key [None]: kc-dev-access_key
Default region name [None]: us-east-2

# memory profiling
conda install memory_profiler
ps -ax | grep streamlit
mprof run --attach {pid}

mprof plot -o output.png

# create env file to be loaded for kc-app.service via EnvironmentFile=
## ref: https://serverfault.com/questions/413397/how-to-set-environment-variable-in-systemd-service?answertab=modifieddesc#tab-top
vi ~/.config/systemd/user/kc-env.conf
AWS_ACCESS_KEY_ID=access_key_id
AWS_SECRET_ACCESS_KEY=access_key
AWS_DEFAULT_REGION=us-east-2

# create service file under user config
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/kc-app.service

# ubuntu service kc-app.service
[Unit]  
Description=a service for the kc app  
After=network.target  
  
[Service]  
Type=simple  
WorkingDirectory=/home/ubuntu/karma
EnvironmentFile=/home/ubuntu/.config/systemd/user/kc-env.conf
ExecStart=/home/ubuntu/karma/.venv/bin/python3 -m streamlit run src/streamlit_app.py  
Restart=on-failure  
RestartSec=2  
  
[Install]  
WantedBy=default.target  


# Note - make sure using .venv/bin/python3

# confirm if working as a USER service
systemctl --user daemon-reload
systemctl --user start kc-app.service
systemctl --user status kc-app.service
-- systemctl --user enable --now kc-app.service

# if all good then set it up as a SYSTEM service
sudo cp ~/.config/systemd/user/kc-app.service /usr/lib/systemd/system

sudo systemctl daemon-reload
sudo systemctl start kc-app
sudo systemctl enable kc-app
sudo systemctl status kc-app

# logs w/o --user
journalctl --since "1 day ago" -u kc-app.service
journalctl --user -xeu kc-app.service


