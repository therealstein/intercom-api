FROM python:3.8-slim

LABEL maintainer "sstein"

RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential libpq-dev gcc

RUN mkdir files

ADD requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python","-u","./app/main-sync.py" ]


