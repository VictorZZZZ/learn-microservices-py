# Profile Service

Микросервис профилей пользователей и организаций. REST API на FastAPI.

Профильные данные (имя, должность, контакты, организация) вынесены сюда из
auth-сервиса: auth отвечает за учётку (логин/пароль/роли), этот сервис — за
«кто человек» и где работает. Связь между базами — общий ключ `user.id` =
`users.id` из auth-сервиса (database per service, FK между базами нет).

## API

| Метод | Путь              | Описание                                                    |
|-------|-------------------|-------------------------------------------------------------|
| GET   | `/v1/user-profile`| Профиль текущего пользователя (id берётся из JWT, claim `uid`) |
| GET   | `/v1/org-profile` | Организация текущего пользователя                           |

Оба эндпоинта возвращают данные того, кто сделал запрос: чей профиль — решает
JWT, а не путь или параметр. Это личные данные, поэтому достаточно пройти
аутентификацию (`Authorization: Bearer <access-токен>`); привилегия READ, как
в catalog-сервисе, не нужна.

`404` означает, что аккаунт есть в auth-сервисе, но профиль здесь ещё не
заведён (для `/v1/org-profile` — также что пользователь не привязан к
организации).

Пример ответа `GET /v1/user-profile`:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "jdoe",
  "first_name": "Иван",
  "last_name": "Иванов",
  "position": "Инженер",
  "avatar_url": null,
  "phone": "+375291234567",
  "telegram_id": "ivanov",
  "organization_id": 7
}
```

Пример ответа `GET /v1/org-profile`:

```json
{
  "id": 7,
  "name": "ООО Ромашка",
  "unp": "123456789",
  "city": "Минск",
  "address": "ул. Ленина, 1",
  "postal_code": "220000",
  "phone": "+375172000000",
  "website": "https://romashka.by"
}
```

## Структура проекта

```
profile-service/
├── alembic/
│   ├── versions/            — миграции
│   └── env.py               — привязка Alembic к настройкам приложения
├── alembic.ini              — конфиг Alembic
├── app/
│   ├── main.py              — точка входа, создание FastAPI-приложения
│   ├── config.py            — настройки из переменных окружения (.env)
│   ├── db/
│   │   ├── base.py          — declarative Base для ORM-моделей
│   │   ├── models.py        — сущности UserProfile и OrganizationProfile (SQLAlchemy ORM)
│   │   ├── session.py       — async engine и фабрика сессий
│   │   └── dependencies.py  — get_session: сессия на HTTP-запрос
│   ├── dto/
│   │   └── profile_dto.py   — UserProfileDto и OrganizationProfileDto (без created_at/updated_at/is_test)
│   ├── mappers/
│   │   └── profile_mapper.py — сущность -> DTO
│   ├── repositories/
│   │   ├── user_profile_repository.py         — доступ к таблице user_profile
│   │   └── organization_profile_repository.py — доступ к таблице organization_profile
│   ├── routers/
│   │   └── profiles_controller.py      — роутеры /v1/user-profile и /v1/org-profile
│   └── security/
│       ├── dependencies.py  — get_current_user / require_privilege / require_role
│       ├── principal.py     — AuthenticatedUser (кто сделал запрос)
│       └── token_verifier.py — проверка access-токенов auth-сервиса
├── tests/
│   ├── test_profile_mapper.py   — тесты маппера
│   └── test_profiles_security.py — тесты эндпоинтов (без БД, сессия подменяется)
├── .env.example             — шаблон переменных окружения
├── requirements.txt         — зависимости
├── requirements-dev.txt     — зависимости для разработки (тесты)
└── README.md
```

## Запуск

Нужен Python 3.10+.

1. Перейти в папку сервиса:

   ```bash
   cd profile-service
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

4. Запустить сервер (из папки `profile-service`):

   ```bash
   uvicorn app.main:app --reload --port 8002
   ```

   Порт 8002, чтобы не пересекаться с auth (8000) и catalog (8001),
   запущенными одновременно.

Сервис поднимется на http://127.0.0.1:8002

## Проверка

- Эндпоинты: http://127.0.0.1:8002/v1/user-profile, http://127.0.0.1:8002/v1/org-profile
- Swagger UI (интерактивная документация): http://127.0.0.1:8002/docs

Или через curl (токен — из `POST /v1/auth/login` auth-сервиса):

```bash
curl -H "Authorization: Bearer <access-токен>" http://127.0.0.1:8002/v1/user-profile
```

## Тесты

Тесты написаны на pytest, лежат в папке `tests/`. База данных не нужна:
сессия подменяется фейком, JWT проверяется по-настоящему. Запуск (из папки
`profile-service`, с активированным `.venv`):

```bash
pytest
```

Установка dev-зависимостей (pytest):

```bash
pip install -r requirements-dev.txt
```

## База данных (PostgreSQL)

У сервиса своя база — `learn-py-profiles` (database per service), как
`learn-py-auth` у auth-сервиса и `learn-py-products` у catalog-сервиса.
Создать её нужно один раз:

```bash
createdb learn-py-profiles
```

Подключение настраивается переменными окружения (см. `app/config.py`).
Локально удобнее через файл `.env`:

```bash
cp .env.example .env   # и заполнить свои значения
```

| Переменная          | Описание                    | По умолчанию      |
|---------------------|-----------------------------|-------------------|
| `DATABASE_HOST`     | хост Postgres               | —                 |
| `DATABASE_PORT`     | порт                        | `5432`            |
| `DATABASE_USER`     | пользователь                | —                 |
| `DATABASE_PASSWORD` | пароль                      | —                 |
| `DATABASE_NAME`     | имя базы                    | —                 |
| `JWT_SECRET`        | секрет для проверки токенов | —                 |
| `LOG_SQL`           | печатать SQL в лог          | `false`           |

`JWT_SECRET` должен совпадать с секретом auth-сервиса: подпись HS256
симметричная — проверить токен может только владелец того же секрета, что
его подписал.

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
