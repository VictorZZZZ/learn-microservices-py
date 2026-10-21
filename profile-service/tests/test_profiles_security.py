from uuid import UUID

from conftest import make_access_token, set_session_rows

from app.db.models import OrganizationProfile, UserProfile

USER_PROFILE_URL = "/v1/user-profile"
ORG_PROFILE_URL = "/v1/org-profile"
USER_ID = UUID("123e4567-e89b-12d3-a456-426614174000")

PROFILE = UserProfile(
    id=USER_ID,
    username="jdoe",
    first_name="Иван",
    last_name="Иванов",
    organization_id=7,
)
ORGANIZATION_PROFILE = OrganizationProfile(id=7, name="ООО Ромашка", unp="123456789")


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# --- GET /user-profile: достаточно аутентификации ---


def test_user_profile_without_token_is_401(client):
    response = client.get(USER_PROFILE_URL)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_user_profile_with_garbage_token_is_401(client):
    # ascii: httpx не пропускает не-ascii символы в значениях заголовков
    response = client.get(USER_PROFILE_URL, headers=bearer("not-a-jwt-token"))

    assert response.status_code == 401


def test_user_profile_with_expired_token_is_401(client):
    token = make_access_token(roles=["READ_ONLY"], privileges=["READ"], ttl_minutes=-1)

    response = client.get(USER_PROFILE_URL, headers=bearer(token))

    assert response.status_code == 401


def test_user_profile_with_token_signed_by_other_secret_is_401(client):
    token = make_access_token(
        roles=["READ_ONLY"], privileges=["READ"], secret="9876543210abcdef9876543210abcdef"
    )

    response = client.get(USER_PROFILE_URL, headers=bearer(token))

    assert response.status_code == 401


def test_user_profile_of_authenticated_user_without_privileges_is_200(client):
    # собственный профиль — персональные данные: доступны без привилегий READ,
    # любому, кто прошёл аутентификацию (в отличие от /v1/products)
    token = make_access_token(roles=[], privileges=[])
    set_session_rows([PROFILE])

    response = client.get(USER_PROFILE_URL, headers=bearer(token))

    assert response.status_code == 200


def test_user_profile_returns_profile_of_current_user(client):
    token = make_access_token(roles=["READ_ONLY"], privileges=["READ"])
    set_session_rows([PROFILE])

    response = client.get(USER_PROFILE_URL, headers=bearer(token))

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(USER_ID)
    assert body["username"] == "jdoe"
    assert body["first_name"] == "Иван"
    assert body["last_name"] == "Иванов"
    assert body["organization_id"] == 7


def test_user_profile_when_never_created_is_404(client):
    # аккаунт есть в auth-сервисе, но профиль здесь ещё не заводили
    token = make_access_token(roles=["READ_ONLY"], privileges=["READ"])

    response = client.get(USER_PROFILE_URL, headers=bearer(token))

    assert response.status_code == 404


# --- GET /org-profile: организация текущего пользователя ---


def test_org_profile_without_token_is_401(client):
    response = client.get(ORG_PROFILE_URL)

    assert response.status_code == 401


def test_org_profile_without_profile_is_404(client):
    token = make_access_token(roles=["READ_ONLY"], privileges=["READ"])

    response = client.get(ORG_PROFILE_URL, headers=bearer(token))

    assert response.status_code == 404


def test_org_profile_when_user_has_no_organization_is_404(client):
    token = make_access_token(roles=["READ_ONLY"], privileges=["READ"])
    set_session_rows([UserProfile(id=USER_ID)])

    response = client.get(ORG_PROFILE_URL, headers=bearer(token))

    assert response.status_code == 404


def test_org_profile_returns_organization_of_current_user(client):
    token = make_access_token(roles=["READ_ONLY"], privileges=["READ"])
    # первый execute — профиль пользователя, второй — организация
    set_session_rows([PROFILE], [ORGANIZATION_PROFILE])

    response = client.get(ORG_PROFILE_URL, headers=bearer(token))

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 7
    assert body["name"] == "ООО Ромашка"
    assert body["unp"] == "123456789"
