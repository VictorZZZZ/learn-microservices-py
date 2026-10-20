## Структура Базы данных


```mermaid

erDiagram
    USER {
        uuid id PK "uuid4, генерируется приложением"
        boolean enabled
        string username UK "уникальный логин"
        string password_hash "bcrypt-хеш, пароль в открытом виде не хранится"
    }

    ROLE {
        int id PK
        string name UK "ADMIN | MANAGER | READ_ONLY"
    }

    PRIVILEGE {
        int id PK
        string name UK "CREATE | UPDATE | DELETE | READ"
    }

    USER_ROLE {
        uuid user_id PK, FK
        int role_id PK, FK
    }

    USER_PRIVILEGE {
        uuid user_id PK, FK
        int privilege_id PK, FK
    }

    ROLE_PRIVILEGE {
        int role_id PK, FK
        int privilege_id PK, FK
    }

    REFRESH_TOKEN {
        bigint id PK
        uuid user_id FK
        string token UK "случайная строка, не JWT"
        timestamptz expires_at
        boolean revoked "true — токен отозван (ротация)"
        timestamptz created_at
    }

    USER ||--o{ USER_ROLE : "имеет роли"
    ROLE ||--o{ USER_ROLE : "назначена пользователям"
    USER ||--o{ USER_PRIVILEGE : "имеет прямые привилегии"
    PRIVILEGE ||--o{ USER_PRIVILEGE : "назначена пользователям"
    ROLE ||--o{ ROLE_PRIVILEGE : "включает привилегии"
    PRIVILEGE ||--o{ ROLE_PRIVILEGE : "входит в роли"
    USER ||--o{ REFRESH_TOKEN : "имеет refresh-токены"

```

## Замечания к схеме

- `users.id` — UUID (uuid4): генерируется приложением при создании, без
  последовательности/autoincrement (в JSON API и JWT-клейме `uid` — строкой).
- Колонка `password_hash` (вместо `password`): колонка хранит bcrypt-хеш,
  имя говорит об этом явно. Колонки `first_name`/`last_name`/`org_id` удалены
  миграцией 20261020_drop_user_names_org.
- Эффективные привилегии пользователя = объединение привилегий его ролей (ROLE_PRIVILEGE)
  и прямых привилегий (USER_PRIVILEGE). Это объединение кладётся в access-токен.
- Новому пользователю при регистрации назначается роль `READ_ONLY`.
- Таблица `refresh_token` (в ER-диаграмме — REFRESH_TOKEN) добавлена для хранения
  refresh-токенов: она позволяет делать ротацию (старый токен отзывается при выдаче нового)
  и в будущем реализовать logout.
