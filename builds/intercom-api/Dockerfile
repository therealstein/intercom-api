FROM python:3.8-slim

LABEL maintainer "sstein"

RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential

RUN mkdir files

ADD requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

