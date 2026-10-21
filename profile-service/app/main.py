import logging

from fastapi import FastAPI

from app.config import get_settings
from app.routers import profiles_controller

settings = get_settings()

# настройка логирования приложения; без неё INFO-сообщения
# (в т.ч. SQL от SQLAlchemy) не попадают в консоль
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

# SQL-запросы SQLAlchemy пишет в logger "sqlalchemy.engine" уровнем INFO;
# включаем его только при LOG_SQL=true (по умолчанию WARNING их глушит)
logging.getLogger("sqlalchemy.engine").setLevel(
    logging.INFO if settings.log_sql else logging.WARNING
)

app = FastAPI(title="Profile Service")

app.include_router(profiles_controller.router)
