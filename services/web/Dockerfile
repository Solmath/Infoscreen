# pull official base image
FROM python:3.12.8-slim-bookworm

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt
RUN pip install waitress

# copy project
COPY . /usr/src/app/

# lint
RUN pip install flake8
RUN flake8 --ignore=E501,F401
