import logging

from fastapi import FastAPI

from app.config import get_settings
from app.exception_handlers import register_exception_handlers
from app.routers import auth_controller

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

app = FastAPI(title="Auth Service")

app.include_router(auth_controller.router)
register_exception_handlers(app)
