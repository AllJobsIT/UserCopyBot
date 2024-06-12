# UserCopyBot

## Требования

- Docker
- Docker-compose

## Инструкция по запуску

- Положить в директорию проекта ваш session файл(если имеется, иначе создастся новый)
- Файл .env.default переименовать в .env и заполнить. В **API_URL** необходимо указать url апишки
  CMS([host/api/graphq/])(При наличии session файла в SESSION_NAME указать его название без расширения)
- Выполнить команду:

```shell
docker-compose up -d
```

- Наслаждаться результатом
