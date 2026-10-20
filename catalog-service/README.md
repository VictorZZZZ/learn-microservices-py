# Microservice 1

Первый микросервис приложения. REST API на FastAPI.

## API

| Метод | Путь            | Описание                                     |
|-------|-----------------|----------------------------------------------|
| GET   | `/v1/products`  | Список продуктов из базы данных              |
| POST  | `/v1/product`   | Создать продукт, возвращает созданный (201)  |

Пример ответа `GET /v1/products`:

```json
[
  {
    "id": 1,
    "name": "Audi A4",
    "description": "Business-class sedan with quattro AWD",
    "vehicle_type": "sedan"
  }
]
```

## Структура проекта

```
microservice_1/
├── alembic/
│   ├── versions/            — миграции
│   └── env.py               — привязка Alembic к настройкам приложения
├── alembic.ini              — конфиг Alembic
├── app/
│   ├── main.py              — точка входа, создание FastAPI-приложения
│   ├── config.py            — настройки из переменных окружения (.env)
│   ├── db/
│   │   ├── base.py          — declarative Base для ORM-моделей
│   │   ├── models.py        — сущность Product (SQLAlchemy ORM)
│   │   ├── session.py       — async engine и фабрика сессий
│   │   └── dependencies.py  — get_session: сессия на HTTP-запрос
│   ├── dto/
│   │   └── product_dto.py   — DTO продукта для ответов API (без created_at)
│   ├── mappers/
│   │   └── product_mapper.py — преобразование Product -> ProductDto
│   ├── models/
│   │   └── vehicle_type.py  — enum VehicleType
│   ├── repositories/
│   │   └── product_repository.py — доступ к таблице product
│   └── routers/
│       └── products_controller.py — роутер /v1/products
├── tests/
│   └── test_product_mapper.py — тесты маппера
├── .env.example             — шаблон переменных окружения
├── requirements.txt         — зависимости
├── requirements-dev.txt     — зависимости для разработки (тесты)
└── README.md
```

## Запуск

Нужен Python 3.10+.

1. Перейти в папку сервиса:

   ```bash
   cd microservice_1
   ```

2. Создать и активировать виртуальное окружение:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Установить зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Запустить сервер (из папки `microservice_1`):

   ```bash
   uvicorn app.main:app --reload
   ```

Сервис поднимется на http://127.0.0.1:8000

## Проверка

- Эндпоинт: http://127.0.0.1:8000/v1/products
- Swagger UI (интерактивная документация): http://127.0.0.1:8000/docs

Или через curl:

```bash
curl http://127.0.0.1:8000/v1/products
```

## Тесты

Тесты написаны на pytest, лежат в папке `tests/`. Запуск (из папки `microservice_1`, с активированным `.venv`):

```bash
pytest
```

Установка dev-зависимостей (pytest):

```bash
pip install -r requirements-dev.txt
```

## База данных (PostgreSQL)

Подключение настраивается переменными окружения (см. `app/config.py`). Локально удобнее через файл `.env`:

```bash
cp .env.example .env   # и заполнить свои значения
```

| Переменная          | Описание                    | По умолчанию |
|---------------------|-----------------------------|--------------|
| `DATABASE_HOST`     | хост Postgres               | —            |
| `DATABASE_PORT`     | порт                        | `5432`       |
| `DATABASE_USER`     | пользователь                | —            |
| `DATABASE_PASSWORD` | пароль                      | —            |
| `DATABASE_NAME`     | имя базы                    | —            |

`.env` можно не создавать — переменные можно задать любым другим способом
(экспорт в терминале, Run Configuration в PyCharm, env в k8s-манифесте).
Реальные переменные окружения имеют приоритет над `.env`.

## Миграции (Alembic)

Миграции запускаются отдельной командой, а не вместе с приложением:

```bash
alembic upgrade head      # применить все миграции
alembic current           # какая версия применена сейчас
alembic history           # список миграций
alembic downgrade base    # откатить все миграции
```

Создание новой миграции:

```bash
alembic revision -m "описание изменения"
```
