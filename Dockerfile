FROM ubuntu:latest

EXPOSE 8000
WORKDIR /app

ENV LANG=C.UTF-8

# installing deps

RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive" apt-get install -y supervisor python3 python3-pip ipset iptables sudo nginx ruby ruby-dev
RUN gem install sass

COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY langate2000-supervisor.conf /etc/supervisor/supervisord.conf

# nginx setup

COPY langate2000-nginx.conf /etc/nginx/sites-enabled/default

# Django setup

ADD theming /app/theming
ADD langate2000-netcontrol /app/langate2000-netcontrol

WORKDIR /app/theming/

RUN sass insalan.scss langate.css

WORKDIR /app/langate/

ADD langate/entrypoint.sh .

CMD ./entrypoint.sh
