# Test-task-for-EPG-Service

## Инструкция по запуску проекта

### С помощью Docker-Compose

Я рекомендую такой способ запуска, так как он запустит на вашем устройстве сразу контейнеры с приложением, базой данных и веб-сервером.
1. Для того чтобы запустить проект через Docker-compose, на вашем устройстве должен стоять сам Docker, его можно скачать по этой ссылке: [Docker](https://www.docker.com/). После того как Docker будет установлен, он попросит вас перезапустить систему.
2. Клонировать или сказать архив с проектом в любое удобное для вас место.
3. Внутри главной папки создать файл `.env` со следующим содержанием:
```plaintext
PG_NAME=epguser
PG_PASSWORD=epgpassword
PG_HOST=db
PG_PORT=5432
PG_DB_NAME=epgdb

SENDER_EMAIL=<указать ваши данные>
SENDER_PASSWORD=<указать ваши данные>
SMTP_SERVER=<указать ваши данные>
SMTP_PORT=<указать ваши данные>
```
4. Далее необходимо создать пару ключей для работы авторизации пользователей. Для этого переходим по этому пути `src/certs` и создаем там пару ключей с помощью следующей команды: `ssh-keygen -t rsa -b 2048 -m PEM -f jwtRS256`.
5. Теперь проект полностью готов к сборке. Переходим в главную папку `Test-task-for-EPG-Service` и вводим там следующую команду, которая позволит собрать проект и сразу его запустить: `docker-compose up --build`.
6. После того как проект будет собран вы сможете перейти по ссылке `http://localhost:80/api/docs`, чтобы увидеть документацию проекта.

## Как деплоить проект.

Для того чтобы задеплоить проект на реальный сервер, вам достаточно поменять под себя конфигурацию файла `nginx.conf`.

## Что можно поменять в проекте.

Поскольку это тестовый проект, я не стал его слишком сильно усложнять, но вообще, тут можно много что поменять. 

1. Я бы старался делать архитектуру ApiGateway и выносить авторизацию в отдельный микросервис, через который будут проходить все запрос пользователей.
2. Я бы также вынес в отдельный сервис логику оценивания пользователей друг другом, с отдельной базой данных для этого. 