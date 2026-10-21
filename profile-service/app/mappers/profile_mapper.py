from app.db.models import OrganizationProfile, UserProfile
from app.dto.profile_dto import OrganizationProfileDto, UserProfileDto


def to_user_profile_dto(profile: UserProfile) -> UserProfileDto:
    return UserProfileDto(
        id=profile.id,
        username=profile.username,
        first_name=profile.first_name,
        last_name=profile.last_name,
        position=profile.position,
        avatar_url=profile.avatar_url,
        phone=profile.phone,
        telegram_id=profile.telegram_id,
        organization_id=profile.organization_id,
    )


def to_organization_profile_dto(organization: OrganizationProfile) -> OrganizationProfileDto:
    return OrganizationProfileDto(
        id=organization.id,
        name=organization.name,
        unp=organization.unp,
        city=organization.city,
        address=organization.address,
        postal_code=organization.postal_code,
        phone=organization.phone,
        website=organization.website,
    )
