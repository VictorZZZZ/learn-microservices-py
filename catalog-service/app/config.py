from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # .env — только удобство для локальной разработки; в k8s значения приходят
    # переменными окружения из ConfigMap/Secret и имеют приоритет над файлом
    model_config = SettingsConfigDict(env_file=".env")

    database_host: str
    database_port: int = 5432  # дефолт; переопределяется env-переменной DATABASE_PORT
    database_user: str
    database_password: str
    database_name: str
    log_sql: bool = False  # LOG_SQL=true — печатать SQL-запросы в лог

    # --- JWT (проверка access-токенов, которые выдаёт auth-сервис) ---
    # HS256 — симметричная подпись, поэтому секрет обязан совпадать с JWT_SECRET
    # auth-сервиса; короткий ключ ослабляет подпись — нужно >= 32 байт (RFC 7518)
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
