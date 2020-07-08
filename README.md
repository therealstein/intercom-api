# intercom-api


intercom-api represents Following functions:

## Installation

add docker-compose.yml
```docker
version: '3'
services:
  intercom-db:
    container_name: intercom-db
    image: mariadb:latest
    volumes:
    - ./db:/var/lib/mysql
    restart: always
    environment:
       - MYSQL_ROOT_PASSWORD=my-secret-password
       - MYSQL_DATABASE=intercom
       - TZ=Europe/Berlin
  intercom-api:
    container_name: intercom-api
    restart: always
    build: ./builds/intercom-api/.
    environment:
      - TZ=Europe/Berlin
      - VIRTUAL_HOST=intercom.hostname.org
      - LETSENCRYPT_HOST=intercom.hostname.org
      - LETSENCRYPT_EMAIL=email@email.com
      - IC_Database=intercom
      - IC_DBPassword=my-secret-password
    volumes:
      - ./api:/app
      - ./files:/files
  intercom-chat:
    container_name: intercom-chat
    restart: always
    build: ./builds/intercom-chat/.
    environment:
      - TZ=Europe/Berlin
      - VIRTUAL_HOST=chat.hostname.org
      - IC_Database=intercom
      - IC_DBPassword=my-secret-password
    volumes:
      - ./chat:/usr/src/app
  intercom-sync:
    container_name: intercom-sync
    restart: always
    build: ./builds/intercom-sync/.
    environment:
      - TZ=Europe/Berlin
      - IC_Database=intercom
      - IC_DBPassword=my-secret-password
      - DB_HOST=dbhost
      - DB_PORT=5432
      - DB_USER=wikiuser
      - DB_PASS=wikipass
      - DB_NAME=wikidb
    volumes:
      - ./sync:/app
networks:
  default:
    external:
      name: nginx-proxy
```




