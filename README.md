<div id="header" align="center">
  <h1>Minimal Wallet API</h1>

  ![Python](https://img.shields.io/badge/-Python_3.10-000?&logo=Python)
  ![FastAPI](https://img.shields.io/badge/-FastAPI_0.115.7-000?&logo=FastAPI)
  ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-000?&logo=PostgreSQL)
  ![Docker](https://img.shields.io/badge/-Docker-000?&logo=Docker)
  ![Redis](https://img.shields.io/badge/-Redis-000?&logo=Redis)
  ![Pytest](https://img.shields.io/badge/-Pytest-000?&logo=Pytest)

</div>

# Техническое задание проекта:
Напишите приложение, которое по REST принимает запрос вида:

```
GET api/v1/wallets/{WALLET_UUID}
```
```
POST api/v1/wallets/{WALLET_UUID}/operation
{
    operationType: DEPOSIT or WITHDRAW,
    amount: 1000
}
```

# Запуск проекта:

- Клонируйте репозиторий.
- Перейдите в папку **docker**.
- Создайте файл **.env** с переменными окружения:
    ```
    DB_HOST=db
    DB_PORT=5432
    DB_NAME=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=password

    TEST_DB_HOST=test_db

    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_DB=0
    ```
- Поочередно выполните следующие команды:
    ```
    docker-compose up -d --build db test_db liquibase redis
    ```
    ```
    docker-compose up -d --build backend tests
    ```
- Для повторного запуска тестов выполните команду:
    ```
    docker-compose run --rm tests
    ```
- Документация к API будет доступна по url-адресу [localhost:8000/redoc](http://localhost:8000/redoc)
