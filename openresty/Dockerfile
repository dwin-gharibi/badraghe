FROM openresty/openresty:alpine

RUN apk add --no-cache --virtual .build-deps \
        build-base \
        lua5.1-dev \
        luarocks5.1 \
    && luarocks-5.1 install lua-resty-http \
    && apk del .build-deps

COPY ./openresty/nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY ./openresty/scripts/ /etc/openresty/scripts/

EXPOSE 80

CMD ["openresty", "-g", "daemon off;"]
