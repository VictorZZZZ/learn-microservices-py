from conftest import make_access_token

PRODUCT_URL = "/v1/products"
NEW_PRODUCT = {"name": "Коврики", "description": "В салон", "vehicle_type": "sedan"}


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# --- GET /products: нужна привилегия READ ---


def test_get_products_without_token_is_401(client):
    response = client.get(PRODUCT_URL)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_get_products_with_garbage_token_is_401(client):
    # ascii: httpx не пропускает не-ascii символы в значениях заголовков
    response = client.get(PRODUCT_URL, headers=bearer("not-a-jwt-token"))

    assert response.status_code == 401


def test_get_products_with_expired_token_is_401(client):
    token = make_access_token(roles=["READ_ONLY"], privileges=["READ"], ttl_minutes=-1)

    response = client.get(PRODUCT_URL, headers=bearer(token))

    assert response.status_code == 401


def test_get_products_with_token_signed_by_other_secret_is_401(client):
    token = make_access_token(
        roles=["READ_ONLY"], privileges=["READ"], secret="9876543210abcdef9876543210abcdef"
    )

    response = client.get(PRODUCT_URL, headers=bearer(token))

    assert response.status_code == 401


def test_get_products_with_read_privilege_is_200(client):
    token = make_access_token(roles=["READ_ONLY"], privileges=["READ"])

    response = client.get(PRODUCT_URL, headers=bearer(token))

    assert response.status_code == 200
    assert response.json() == []


def test_get_products_without_read_privilege_is_403(client):
    token = make_access_token(roles=[], privileges=["UPDATE"])

    response = client.get(PRODUCT_URL, headers=bearer(token))

    assert response.status_code == 403


# --- POST /products: нужна роль ADMIN ---


def test_create_product_without_token_is_401(client):
    response = client.post(PRODUCT_URL, json=NEW_PRODUCT)

    assert response.status_code == 401


def test_create_product_by_admin_is_201(client):
    token = make_access_token(roles=["ADMIN"], privileges=["READ", "CREATE"])

    response = client.post(PRODUCT_URL, json=NEW_PRODUCT, headers=bearer(token))

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == NEW_PRODUCT["name"]
    assert body["vehicle_type"] == NEW_PRODUCT["vehicle_type"]


def test_create_product_by_non_admin_is_403(client):
    # MANAGER с привилегией CREATE всё равно не пройдёт: метод закрыт ролью,
    # а не привилегией
    token = make_access_token(roles=["MANAGER"], privileges=["READ", "CREATE"])

    response = client.post(PRODUCT_URL, json=NEW_PRODUCT, headers=bearer(token))

    assert response.status_code == 403
