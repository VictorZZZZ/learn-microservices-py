# Gateway (nginx в Docker)

Единая точка входа микросервисного приложения — **порт машины `7777`**.
nginx запускается в контейнере, на локальную машину ничего не ставится.
Здесь же живёт централизованная документация API (Redoc) — `/docs/`,
статика в папке [api-docs/](api-docs/README.md).

Ответственность gateway — роутинг по префиксу пути и раздача документации.
Никакой бизнес-логики: JWT по-прежнему проверяется в каждом сервисе,
агрегация ответов — задача отдельного сервиса оркестрации (BFF), который
стоит за этим же gateway, как и остальные.

## Маршрутизация

Срезается только префикс сервиса — остальной путь передаётся без
изменений: путь из документации сервиса отправляется через gateway
как есть, добавляется один префикс.

| Внешний путь (`http://localhost:7777`) | Сервис (на хосте) | Внутренний путь |
|---|---|---|
| `/api/**` | orchestrator (`:8000`) | `/**` |
| `/auth/**` | auth-service (`:8001`) | `/**` |
| `/catalog/**` | catalog-service (`:8002`) | `/**` |
| `/profile/**` | profile-service (`:8003`) | `/**` |
| `/docs/`, `/openapi/*.json` | документация (Redoc) | статика + live-спеки сервисов |

Примеры подстановки:

- `POST /auth/v1/auth/login` → `:8001/v1/auth/login`
- `GET /catalog/v1/products` → `:8002/v1/products`
- `GET /profile/v1/user-profile` → `:8003/v1/user-profile`

## Запуск

0. Нужен запущенный Docker Desktop. Сервисы стартуют на хосте с явными
   портами (иначе uvicorn займёт дефолтный `:8000`, зарезервированный
   под оркестратор):

   ```bash
   cd auth-service     && uvicorn app.main:app --reload --port 8001
   cd catalog-service  && uvicorn app.main:app --reload --port 8002
   cd profile-service  && uvicorn app.main:app --reload --port 8003
   ```

1. Поднять gateway через compose (рекомендуется):

   ```bash
   cd gateway
   docker compose up -d          # при первом запуске скачает nginx:alpine
   docker logs -f gateway        # access/error логи nginx
   ```

   Остановка: `docker compose down`.

   Либо одной командой без compose:

   ```bash
   docker run -d --name gateway \
     -p 7777:8080 \
     -v "$PWD/nginx.conf":/etc/nginx/nginx.conf:ro \
     -v "$PWD/api-docs/site":/usr/share/nginx/html/api-docs:ro \
     --add-host=host.docker.internal:host-gateway \
     nginx:alpine
   ```

   (`--add-host` на macOS не обязателен — Docker Desktop резолвит имя сам;
   оставлен для совместимости с Linux.)

2. Быстрая проверка:

   ```bash
   curl -i http://localhost:7777/catalog/v1/products   # роутер
   open http://localhost:7777/docs/                    # документация
   ```

## Управление

```bash
docker exec gateway nginx -t          # проверить синтаксис конфига
docker exec gateway nginx -s reload   # применить правки nginx.conf без перезапуска
docker logs -f gateway                # логи
docker compose down                   # остановить (или docker rm -f gateway)
```

Правки `nginx.conf` подхватываются `nginx -s reload` — пересоздавать
контейнер не нужно.

## Документация API (Redoc)

Одна страница со всеми API: **http://localhost:7777/docs/** — все сервисы
в одной левой панели, сгруппированы по сервисам; пути показаны сразу с
префиксом gateway. Подробности и инструкция «добавить новый сервис» — в
[api-docs/README.md](api-docs/README.md).

Коротко: Redoc рендерит **живые** `openapi.json` прямо в браузере — ничего
не собирается на этапе сборки, документация всегда соответствует текущему
коду. Спеки отдаются этим же nginx (`/openapi/*.json`), поэтому страница
и JSON в одном origin и CORS не возникает. Redoc — read-only: выполнять
запросы — curl'ом (примеры ниже) или в Swagger UI сервиса напрямую на его
порту (`http://localhost:8001/docs`).

## Примеры: end-to-end через gateway

```bash
# 1. Логин (в ответе access_token)
curl -s -X POST http://localhost:7777/auth/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username": "your-user", "password": "your-password"}'

# 2. Защищённый запрос profile-сервиса с токеном из шага 1
TOKEN=...
curl -s http://localhost:7777/profile/v1/user-profile \
  -H "Authorization: Bearer $TOKEN"

# 3. Каталог
curl -s http://localhost:7777/catalog/v1/products

# 4. Агрегированные ответы оркестратора (когда сервис появится)
curl -s http://localhost:7777/api/...
```

## Траблшутинг

- **502 Bad Gateway** — nginx работает, но целевой сервис на хосте не
  поднят или слушает не тот порт. Проверить: `lsof -i :8001` и т.д.
- **Порт 7777 занят**: `lsof -i :7777`.
- **Linux-хост**: запускайте uvicorn с `--host 0.0.0.0` и не убирайте
  `--add-host=host.docker.internal:host-gateway` (в compose уже есть).
- **Swagger** отдельного сервиса работает только напрямую на его порту
  (`http://localhost:8001/docs`): страница документации FastAPI
  запрашивает `/openapi.json` по абсолютному пути, поэтому за
  под-префиксом gateway она не работает. Для чтения документации всех
  сервисов сразу используйте `/docs/`.
- **`/api/**` отдаёт 502**, пока оркестратор не поднят — это ожидаемо.

## Когда лучше Traefik или Kong вместо nginx

Все три — законные варианты точки входа; выбор определяется тем, что
требуется от gateway.

**nginx** — статический reverse proxy. Маршруты описываются в конфиге
вручную, любое изменение — правка файла и reload. Идеален, когда
топология меняется редко (наш случай: фиксированный набор из четырёх
сервисов), а нужен быстрый и предсказуемый роутер. Это же индустриальный
дефолт — в проде перед Java-стеками nginx стоит чаще специализированных
шлюзов.

**Traefik** — reverse proxy с динамической конфигурацией. Главный козырь
— автодискавери: в docker-compose/Kubernetes Traefik сам находит
контейнеры по label'ам (`traefik.http.routers.auth.rule=...`) и
перестраивает маршруты на лету, без reload. Новый сервис подключается
собственными label'ами — конфиг gateway не трогается вообще. Из коробки
— Let's Encrypt и live-дашборд. Брать, когда всё приложение живёт в
Docker/K8s и состав сервисов часто меняется. Сейчас, пока сервисы
крутятся на хосте через uvicorn, Traefik пришлось бы настраивать
статическим файлом — и его главное преимущество теряется.

**Kong** — полноценный API-gateway, а не просто прокси (под капотом тот
же nginx + OpenResty/Lua). Даёт admin API и экосистему плагинов: rate
limiting, API-ключи для внешних потребителей, CORS, трансформация
запросов/ответов, проверка JWT на edge, метрики использования API. По
духу это ближайший к коммерческим API-менеджментам (Apigee) вариант; в
Java-мире примерно так выглядела бы связка Spring Cloud Gateway +
кастомные фильтры, но с админкой и готовыми плагинами. Цена — заметно
тяжелее в освоении и эксплуатации: свои сущности
(services/routes/consumers/plugins), БД или DB-less-режим. Брать, когда
появляются gateway-политики: лимиты, квоты, ключи сторонним клиентам,
аутентификация на edge. Для чистого роутинга — избыточен.

|         | nginx                     | Traefik                        | Kong                          |
|---------|---------------------------|--------------------------------|-------------------------------|
| Конфиг  | ручной, статический       | автоматический (label'ы, DNS)  | через admin API               |
| Козырь  | простота, предсказуемость | автодискавери в Docker/K8s     | плагины и API-политики        |
| Брать когда | топология фиксирована, нужна только маршрутизация | сервисы часто добавляются/убираются в контейнерах | нужны rate limiting, API-ключи, auth на edge |

Разумная эволюция для этого проекта: **nginx** сейчас → **Traefik**,
когда всё переедет в docker-compose и захочется автодискавери →
**Kong** — только если появятся настоящие gateway-политики (заодно тогда
можно осознанно централизовать проверку JWT на edge вместо
defense-in-depth в каждом сервисе, как сейчас).

## Что дальше

Когда сервисы переедут в контейнеры, в `nginx.conf` достаточно заменить
`host.docker.internal:800x` в блоках `upstream` на имена compose-сервисов
(`http://auth-service:8001` и т.д.) — Docker DNS резолвит их внутри
общей сети compose.
