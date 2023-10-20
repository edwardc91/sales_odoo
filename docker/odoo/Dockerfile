FROM odoo:16.0

ARG http_proxy
ARG https_proxy

ENV HTTP_PROXY $http_proxy
ENV HTTPS_PROXY $https_proxy
ENV http_proxy $http_proxy
ENV https_proxy https_proxy

ENV HTTP_PROXY $HTTP_PROXY
ENV HTTPS_PROXY $HTTPS_PROXY
ENV http_proxy $HTTP_PROXY
ENV https_proxy $HTTPS_PROXY

USER root

RUN pip3 install --upgrade pip && \
    pip3 install paramiko

USER odoo

RUN mkdir /var/lib/odoo/backups