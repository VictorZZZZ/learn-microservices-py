from auth_contracts.privilege_name import PrivilegeName
from auth_contracts.role_name import RoleName
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session
from app.dto.product_dto import ProductCreateDto, ProductDto
from app.mappers.product_mapper import to_product, to_product_dto
from app.repositories.product_repository import ProductRepository
from app.security.dependencies import require_privilege, require_role
from app.security.principal import AuthenticatedUser

router = APIRouter(prefix="/v1", tags=["products"])


@router.get("/products", response_model=list[ProductDto])
async def get_products(
    session: AsyncSession = Depends(get_session),
    user: AuthenticatedUser = Depends(require_privilege(PrivilegeName.READ)),
) -> list[ProductDto]:
    repository = ProductRepository(session)
    products = await repository.find_all()
    return [to_product_dto(product) for product in products]


@router.post(
    "/products",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductDto,
)
async def create_product(
    payload: ProductCreateDto,
    session: AsyncSession = Depends(get_session),
    user: AuthenticatedUser = Depends(require_role(RoleName.ADMIN)),
) -> ProductDto:
    repository = ProductRepository(session)
    product = to_product(payload)
    saved = await repository.save(product)
    return to_product_dto(saved)
