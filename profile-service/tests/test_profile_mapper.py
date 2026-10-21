from uuid import uuid4

from app.db.models import OrganizationProfile, UserProfile
from app.mappers.profile_mapper import to_organization_profile_dto, to_user_profile_dto


def test_to_user_profile_dto():
    user_id = uuid4()
    profile = UserProfile(
        id=user_id,
        username="jdoe",
        first_name="Иван",
        last_name="Иванов",
        position="Инженер",
        avatar_url="https://example.com/avatar.png",
        phone="+375291234567",
        telegram_id="ivanov",
        organization_id=7,
    )

    dto = to_user_profile_dto(profile)

    assert dto.id == user_id
    assert dto.username == "jdoe"
    assert dto.first_name == "Иван"
    assert dto.last_name == "Иванов"
    assert dto.position == "Инженер"
    assert dto.avatar_url == "https://example.com/avatar.png"
    assert dto.phone == "+375291234567"
    assert dto.telegram_id == "ivanov"
    assert dto.organization_id == 7

    dumped = dto.model_dump()
    assert "created_at" not in dumped
    assert "updated_at" not in dumped
    assert "is_test" not in dumped


def test_to_organization_profile_dto():
    organization = OrganizationProfile(
        id=7,
        name="ООО Ромашка",
        unp="123456789",
        city="Минск",
        address="ул. Ленина, 1",
        postal_code="220000",
        phone="+375172000000",
        website="https://romashka.by",
    )

    dto = to_organization_profile_dto(organization)

    assert dto.id == 7
    assert dto.name == "ООО Ромашка"
    assert dto.unp == "123456789"
    assert dto.city == "Минск"
    assert dto.address == "ул. Ленина, 1"
    assert dto.postal_code == "220000"
    assert dto.phone == "+375172000000"
    assert dto.website == "https://romashka.by"

    dumped = dto.model_dump()
    assert "created_at" not in dumped
    assert "updated_at" not in dumped
    assert "is_test" not in dumped
