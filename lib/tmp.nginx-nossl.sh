#!/bin/sh

#define parameters which are passed in.
USERNAME=$1
DOMAIN=$2

#define the template.
cat << EOF
server {
        listen 80 default_server;
        listen [::]:80 default_server;


        server_name $DOMAIN;


#        location /grafana/ {
#                proxy_pass http://localhost:3000/;
#                proxy_set_header Host \$host;
#                proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
#        }


        location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
                root /home/$USERNAME/dj_iot;
        }
        
        location /media/ {
                root /home/$USERNAME/dj_iot;
        }

        location / {
                include proxy_params;
                proxy_pass http://unix:/run/gunicorn.sock;
        }

}
EOF
