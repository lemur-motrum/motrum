FROM python:3.12-slim

RUN pip install --upgrade pip

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2 

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /home/sites/
WORKDIR /home/sites/
ADD requirements.txt /home/sites/
RUN pip install -r requirements.txt
