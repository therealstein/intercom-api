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
      - VIRTUAL_HOST=chat.stein.ovh
      - IC_Database=intercom
      - IC_DBPassword=my-secret-password
    volumes:
      - ./chat:/usr/src/app
networks:
  default:
    external:
      name: nginx-proxy
```




