FROM python:3.12-slim

RUN pip install --upgrade pip

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt-get install -y git \
    && pip install psycopg2 

RUN pip install git+https://github.com/jazzband/django-smart-selects.git


# RUN pip install --git+https://github.com/jazzband/django-smart-selects.git

# RUN git clone https://github.com/jazzband/django-smart-selects.git smart_selects 
# RUN cd smart_selects
# RUN pip install -e

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /home/sites/
WORKDIR /home/sites/
ADD requirements.txt /home/sites/
RUN pip install -r requirements.txt
