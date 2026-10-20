import os
from datetime import UTC, datetime, timedelta

# 32+ байта: PyJWT ругается на более короткие HMAC-ключи (RFC 7518)
TEST_SECRET = "0123456789abcdef0123456789abcdef"

# Дефолты для Settings, чтобы тесты не зависели от наличия .env.
# Ставим ДО импорта app.*: main.py при импорте читает настройки.
# setdefault не мешает локально — реальные env-переменные имеют приоритет.
os.environ.setdefault("DATABASE_HOST", "localhost")
os.environ.setdefault("DATABASE_USER", "postgres")
os.environ.setdefault("DATABASE_PASSWORD", "postgres")
os.environ.setdefault("DATABASE_NAME", "microservice_1")
os.environ.setdefault("JWT_SECRET", TEST_SECRET)

import jwt as pyjwt  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.dependencies import get_session  # noqa: E402
from app.main import app  # noqa: E402

USER_ID = "123e4567-e89b-12d3-a456-426614174000"


def make_access_token(
    roles: list[str],
    privileges: list[str],
    *,
    secret: str = TEST_SECRET,
    ttl_minutes: int = 15,
) -> str:
    """Собирает токен тем же способом, что TokenService auth-сервиса."""
    now = datetime.now(UTC)
    payload = {
        "sub": "jdoe",
        "uid": USER_ID,
        "roles": roles,
        "privileges": privileges,
        "iat": now,
        "exp": now + timedelta(minutes=ttl_minutes),
    }
    return pyjwt.encode(payload, secret, algorithm="HS256")


class _FakeResult:
    def __init__(self, rows: list) -> None:
        self._rows = rows

    def scalars(self) -> "_FakeResult":
        return self

    def all(self) -> list:
        return self._rows


class FakeSession:
    """Двойник AsyncSession без БД: хватает для запросов ProductRepository."""

    def __init__(self) -> None:
        self._next_id = 1

    async def execute(self, stmt) -> _FakeResult:
        return _FakeResult([])

    def add(self, obj) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def refresh(self, obj) -> None:
        # имитируем то, что БД сгенерировала id при INSERT
        obj.id = self._next_id
        self._next_id += 1


async def _fake_get_session():
    yield FakeSession()


@pytest.fixture
def client() -> TestClient:
    # подменяем только сессию с БД; безопасность (Bearer) работает по-настоящему
    app.dependency_overrides[get_session] = _fake_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_session, None)
