FROM python:3.12-slim

RUN pip install --upgrade pip

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /home/sites/
WORKDIR /home/sites/
ADD requirements.txt /home/sites/
RUN pip install -r requirements.txt
