FROM openresty/openresty:alpine

COPY ./nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY ./scripts/ /etc/openresty/scripts/

EXPOSE 80

CMD ["openresty", "-g", "daemon off;"]