FROM python:3.4

RUN apt-get update
RUN apt-get install -y sqlite3 libsqlite3-dev

COPY requirements.txt /app/streamer/
RUN pip install -r /app/streamer/requirements.txt

COPY . /app/streamer/
WORKDIR /app/streamer/
