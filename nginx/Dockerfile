FROM nginx:1.29.1-alpine

RUN apk add --no-cache tini

RUN rm /etc/nginx/conf.d/default.conf
COPY default.conf /etc/nginx/conf.d/

RUN mkdir -p /var/www/certbot /var/log/nginx

# Se precisar copiar certificados localmente, copie para /etc/letsencrypt (geralmente você usa volume)
# COPY ./nginx/ssl /etc/letsencrypt

# Ajustar permissões na pasta correta
RUN chmod -R 700 /etc/letsencrypt && \
    chown -R root:root /etc/letsencrypt

ENTRYPOINT [ "/sbin/tini", "--" , "/docker-entrypoint.sh" ]
CMD [ "nginx", "-g", "daemon off;" ]
