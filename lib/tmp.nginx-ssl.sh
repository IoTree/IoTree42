#!/bin/sh

#define parameters which are passed in.
USERNAME=$1
DOMAIN=$2

#define the template.
cat << EOF
map \$http_upgrade \$connection_upgrade {
  default upgrade;
  ''      close;
}

server {
  listen 80;
  server_name $DOMAIN;
  return 301 https://\$host\$request_uri;
}

# SSL configuration
server {
  listen 443 ssl;
  server_name $DOMAIN;
  ssl_certificate      /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
  ssl_certificate_key  /etc/letsencrypt/live/$DOMAIN/privkey.pem;

  # Improve HTTPS performance with session resumption
  ssl_session_cache shared:SSL:10m;
  ssl_session_timeout 5m;

  # Enable server-side protection against BEAST attacks
  ssl_prefer_server_ciphers on;
  ssl_ciphers ECDH+AESGCM:ECDH+AES256:ECDH+AES128:DH+3DES:!ADH:!AECDH:!MD5;

  # Disable SSLv3
  ssl_protocols TLSv1 TLSv1.1 TLSv1.2;

  # Diffie-Hellman parameter for DHE ciphersuites
  # ssl_dhparam /etc/ssl/certs/dhparam.pem;

  # Enable HSTS (https://developer.mozilla.org/en-US/docs/Security/HTTP_Strict_Transport_Security)
  add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";

  # Enable OCSP stapling (http://blog.mozilla.org/security/2013/07/29/ocsp-stapling-in-firefox)
  ssl_stapling on;
  ssl_stapling_verify on;
  ssl_trusted_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
  resolver 8.8.8.8 8.8.4.4 valid=300s;
  resolver_timeout 5s;

#  location /grafana/ {
#    proxy_pass http://localhost:3000/;
#    proxy_set_header Host \$host;
#    proxy_redirect http:// https://;
#    proxy_http_version 1.1;
#    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
#    proxy_set_header Upgrade \$http_upgrade;
#    proxy_set_header Connection \$connection_upgrade;
#    }

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
        proxy_connect_timeout       600;
        proxy_send_timeout          600;
        proxy_read_timeout          600;
        send_timeout                600;
    }
}

EOF
