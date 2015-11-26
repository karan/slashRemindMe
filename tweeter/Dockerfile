FROM python:3.4-slim

RUN apt-get update
RUN apt-get install -y sqlite3 libsqlite3-dev

COPY . /streamer/
WORKDIR /streamer

RUN pip install -r requirements.txt
