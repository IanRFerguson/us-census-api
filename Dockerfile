FROM python:3.9
ENV PYTHONUNBUFFERED 1

###

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get -y install python3-pip

RUN apt-get -y install redis-server

RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata curl ca-certificates fontconfig locales \
    && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/* 

###

ENV APP_ROOT /var/www/CENSUS_APP

#Create the working directory
RUN mkdir -p $APP_ROOT

WORKDIR $APP_ROOT

COPY . ./
RUN pip install -r requirements.txt 

EXPOSE 5000