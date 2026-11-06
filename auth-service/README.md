# Auth Service

Микросервис аутентификации: регистрация пользователей и выдача JWT-токенов.
REST API на FastAPI, PostgreSQL, SQLAlchemy (async), Alembic.

## Как это устроено

- **Пароль** хранится только как bcrypt-хеш (аналог `BCryptPasswordEncoder`
  из Spring Security). Соль генерируется на каждый пароль и хранится внутри хеша.
- **id пользователя — UUID (uuid4)**, генерируется приложением при создании
  (аналог `UUID.randomUUID()` в JPA). В JSON API и в JWT-клейме `uid` — строкой.
- **Access-токен** — JWT, подписан по **HS256** общим секретом (`JWT_SECRET`).
  Внутри — `sub` (username), `uid`, `roles`, `privileges` (эффективные
  привилегии = привилегии ролей + прямые привилегии пользователя). Другим
  микросервисам не нужно ходить в auth-сервис за правами — всё уже в токене.
  Живёт 15 минут (настраивается).
- **Refresh-токен** — непрозрачная случайная строка, хранится в таблице
  `refresh_tokens`. При каждом `/refresh` — **ротация**: старый токен отзывается,
  выдаётся новая пара. Живёт 30 дней (настраивается).
- **Токены выдаются только пользователю с `enabled = true`** (проверяется и при
  login, и при refresh).
- Новому пользователю при регистрации назначается роль **READ_ONLY**
  (привилегия READ). Изменить роли можно SQL (см. ниже) — эндпоинтов управления
  ролями пока нет.

## API

| Метод | Путь                | Описание                                             |
|-------|---------------------|------------------------------------------------------|
| POST  | `/v1/auth/register` | Регистрация: создаёт пользователя и выдаёт токены (201) |
| POST  | `/v1/auth/login`    | Логин: выдаёт пару токенов                           |
| POST  | `/v1/auth/refresh`  | Ротация: новая пара токенов, старый refresh отзывается |

### Ошибки

Формат: `{"code": "...", "message": "..."}` (аналог ProblemDetail).
Обработчики доменных ошибок — в `app/exception_handlers.py`
(аналог `@RestControllerAdvice`).

| HTTP | code                   | Когда                                    |
|------|------------------------|------------------------------------------|
| 409  | `USERNAME_TAKEN`       | username уже занят                       |
| 401  | `INVALID_CREDENTIALS`  | неверный логин или пароль                |
| 403  | `ACCOUNT_DISABLED`     | `enabled = false`                        |
| 401  | `INVALID_REFRESH_TOKEN`| refresh не найден / истёк / отозван      |

### Примеры

`POST /v1/auth/register`:

```json
{
  "username": "jdoe",
  "password": "s3cret-password"
}
```

Ответ (201):

```json
{
  "user": {
    "id": "3f2a9c1e-6b7d-4e8f-9a01-2c3b4d5e6f70",
    "username": "jdoe",
    "enabled": true,
    "roles": ["READ_ONLY"]
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "w7Yc2... (86 символов)",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

`POST /v1/auth/login` — тот же формат `tokens`:

```json
{ "username": "jdoe", "password": "s3cret-password" }
```

`POST /v1/auth/refresh`:

```json
{ "refresh_token": "w7Yc2..." }
```

Payload access-токена (можно посмотреть на jwt.io):

```json
{
  "sub": "jdoe",
  "uid": "3f2a9c1e-6b7d-4e8f-9a01-2c3b4d5e6f70",
  "roles": ["READ_ONLY"],
  "privileges": ["READ"],
  "iat": 1760851200,
  "exp": 1760852100
}
```

## Структура проекта

```
auth-service/
├── alembic/
│   ├── versions/                       — миграции
│   │   ├── 20261019_create_auth_tables.py      — таблицы (users, roles, ...)
│   │   ├── 20261019_seed_roles.py              — сиды ролей/привилегий
│   │   ├── 20261019_names_nullable.py          — first/last_name стали nullable
│   │   └── 20261020_drop_user_names_org.py     — first/last_name и org_id удалены
│   └── env.py                          — привязка Alembic к настройкам
├── alembic.ini
├── app/
│   ├── main.py                         — создание FastAPI-приложения
│   ├── config.py                       — настройки из переменных окружения (.env)
│   ├── exceptions.py                   — доменные ошибки (аналог BusinessException)
│   ├── exception_handlers.py           — ошибки -> HTTP (аналог @RestControllerAdvice)
│   ├── db/
│   │   ├── base.py                     — declarative Base
│   │   ├── models.py                   — ORM: User, Role, Privilege, RefreshToken
│   │   ├── session.py                  — async engine и фабрика сессий
│   │   └── dependencies.py             — get_session: сессия на HTTP-запрос
│   ├── models/                         — enum'ы справочников
│   │   ├── role_name.py                — RoleName: ADMIN, MANAGER, READ_ONLY
│   │   └── privilege_name.py           — PrivilegeName: CREATE, UPDATE, DELETE, READ
│   ├── dto/
│   │   └── auth_dto.py                 — запросы/ответы API
│   ├── mappers/
│   │   └── user_mapper.py              — RegisterRequest -> User, User -> UserDto
│   ├── repositories/
│   │   ├── user_repository.py          — доступ к users/roles
│   │   └── refresh_token_repository.py — доступ к refresh_tokens
│   ├── services/
│   │   ├── password_service.py         — bcrypt hash/verify
│   │   ├── token_service.py            — создание/проверка JWT
│   │   └── auth_service.py             — сценарии register/login/refresh
│   └── routers/
│       └── auth_controller.py          — роутер /v1/auth/*
├── tests/                              — unit-тесты без БД
├── docs/db_structure.md                — ER-диаграмма
├── .env.example
├── requirements.txt / requirements-dev.txt
└── README.md
```

## Запуск

Нужен Python 3.10+.

```bash
cd auth-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env   # заполнить значения, включая JWT_SECRET
alembic upgrade head   # применить миграции (таблицы + сиды)
uvicorn app.main:app --reload
```

Если старая версия миграций (с `users.id BIGINT`) уже была применена к вашей БД —
пересоздайте схему с нуля (данных в users пока нет, сиды вернутся сами):

```bash
alembic downgrade base && alembic upgrade head
```

Требуется PostgreSQL 13+ (миграция использует `gen_random_uuid()`).

Сервис поднимется на http://127.0.0.1:8000, Swagger UI — http://127.0.0.1:8000/docs

## Переменные окружения

| Переменная                  | Описание                          | По умолчанию |
|-----------------------------|-----------------------------------|--------------|
| `DATABASE_HOST`             | хост Postgres                     | —            |
| `DATABASE_PORT`             | порт                              | `5432`       |
| `DATABASE_USER`             | пользователь                      | —            |
| `DATABASE_PASSWORD`         | пароль                            | —            |
| `DATABASE_NAME`             | имя базы                          | —            |
| `JWT_SECRET`                | секрет подписи HS256 (>= 32 симв.)| —            |
| `ACCESS_TOKEN_TTL_MINUTES`  | время жизни access-токена, мин.   | `15`         |
| `REFRESH_TOKEN_TTL_DAYS`    | время жизни refresh-токена, дней  | `30`         |
| `LOG_SQL`                   | `true` — печатать SQL в лог       | `false`      |

Генерация секрета:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Сид-данные (миграция 20261019_seed_roles)

| Роль       | Привилегии                    |
|------------|-------------------------------|
| ADMIN      | CREATE, UPDATE, DELETE, READ  |
| MANAGER    | CREATE, UPDATE, READ          |
| READ_ONLY  | READ                          |

Выдать пользователю роль (пока вручную):

```sql
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE u.username = 'jdoe' AND r.name = 'ADMIN';
```

Отключить пользователя (все последующие login/refresh вернут 403):

```sql
UPDATE users SET enabled = false WHERE username = 'jdoe';
```

## Проверка вручную (curl)

```bash
# 1. Регистрация — сразу получаем пару токенов
curl -s -X POST http://127.0.0.1:8000/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"jdoe","password":"s3cret-password"}'

# 2. Логин
curl -s -X POST http://127.0.0.1:8000/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"jdoe","password":"s3cret-password"}'

# 3. Refresh (подставить refresh_token из шага 2)
curl -s -X POST http://127.0.0.1:8000/v1/auth/refresh \
  -H 'Content-Type: application/json' \
  -d '{"refresh_token":"<refresh_token>"}'

# Повторный refresh тем же токеном вернёт 401 INVALID_REFRESH_TOKEN — ротация
```

## Тесты

Unit-тесты без БД (bcrypt, JWT, мапперы):

```bash
pytest
```

## Структура БД

ER-диаграмма — в [docs/db_structure.md](docs/db_structure.md).
Таблицы: `users`, `roles`, `privileges`, `user_roles`, `user_privileges`,
`role_privileges`, `refresh_tokens`.
