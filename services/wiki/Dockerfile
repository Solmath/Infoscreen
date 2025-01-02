# pull official base image
FROM python:3.12.8-slim-bookworm

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /usr/src/app/

# install dependencies
RUN pip install --upgrade pip

RUN pip install --pre moin
RUN pip install -r requirements.txt
    
# RUN pip install flake8 

# # lint
# RUN flake8 --ignore=E501,F401 

# Create moin instance
# Todo: What if instance already exists?
RUN moin create-instance --path INSTANCE-DIRECTORY
COPY ./wikiconfig.py /usr/src/app/INSTANCE-DIRECTORY
RUN cd /usr/src/app/INSTANCE-DIRECTORY \
    moin index-create \
    moin welcome \
    moin load-help -n help-en \
    moin load-help -n help-common
