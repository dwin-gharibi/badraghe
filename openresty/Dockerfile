FROM openresty/openresty:alpine

COPY openresty/nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY openresty/scripts/ /etc/openresty/scripts/

EXPOSE 80

CMD ["openresty", "-g", "daemon off;"]