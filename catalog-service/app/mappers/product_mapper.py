from app.db.models import Product
from app.dto.product_dto import ProductCreateDto, ProductDto


def to_product(dto: ProductCreateDto) -> Product:
    return Product(
        name=dto.name,
        description=dto.description,
        vehicle_type=dto.vehicle_type,
    )


def to_product_dto(product: Product) -> ProductDto:
    return ProductDto(
        id=product.id,
        name=product.name,
        description=product.description,
        vehicle_type=product.vehicle_type,
    )
