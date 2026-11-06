# Архитектура

Приложение «Автолавка» построено из нескольких сервисов на Python (FastAPI,
PostgreSQL, SQLAlchemy, Alembic).

## Сервисы

| Сервис            | Назначение                                              |
|-------------------|---------------------------------------------------------|
| Auth Service      | Регистрация пользователей и выдача JWT-токенов          |
| Profile Service   | Профили пользователей и организаций                     |
| Catalog Service   | Каталог товаров                                         |
| Gateway           | Единая точка входа и API-документация                   |
| Recognize Service | OCR текста с техпаспортов автомобилей                   |

## Базы данных

Каждый сервис работает со своей базой PostgreSQL и своими миграциями Alembic:

- Auth Service — пользователи, роли, привилегии
  (`auth-service/docs/db_structure.md`).
- Profile Service — профили пользователей и организаций
  (`profile-service/docs/db_structure.md`).
- Catalog Service — таблица `product`
  (`catalog-service/docs/warehose_er.md`).
