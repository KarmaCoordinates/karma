# to-be architecture
ALB listening on port 443, terminating SSL traffic.
Use Amazon ACM to generate your certificate and attach this to your HTTPS listener.
ALB Target Group sending traffic unencrypted to port 80 on the instance.
Security group for instances only allows port 80 access from your ALB.


#create certbot certs
# https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal
certonly --webroot --webroot-path=/var/www/html --email sdixit@ohioedge.com --agree-tos --no-eff-email --staging -d karmacoordinates.org  -d www.karmacoordinates.org
