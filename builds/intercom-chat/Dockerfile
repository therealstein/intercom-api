FROM node:10.20-jessie
# Create app directory
WORKDIR /usr/src/app

RUN apt-get update \
  && apt-get install -y mysql-client libmysqlclient-dev

EXPOSE 3000
CMD npm install && node index
