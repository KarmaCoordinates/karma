ALB listening on port 443, terminating SSL traffic.
Use Amazon ACM to generate your certificate and attach this to your HTTPS listener.
ALB Target Group sending traffic unencrypted to port 80 on the instance.
Security group for instances only allows port 80 access from your ALB.