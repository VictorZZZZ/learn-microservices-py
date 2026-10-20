from app.db.models import Product
from app.dto.product_dto import ProductCreateDto
from app.mappers.product_mapper import to_product, to_product_dto
from app.models.vehicle_type import VehicleType


def test_to_product_dto():
    product = Product(
        id=100,
        name="audi",
        description="some descr",
        vehicle_type=VehicleType.SEDAN,
    )

    dto = to_product_dto(product)

    assert dto.id == 100
    assert dto.name == "audi"
    assert dto.description == "some descr"
    assert dto.vehicle_type == VehicleType.SEDAN
    assert "created_at" not in dto.model_dump()


def test_to_product():
    dto = ProductCreateDto(
        name="audi",
        description="some descr",
        vehicle_type=VehicleType.HATCHBACK,
    )

    product = to_product(dto)

    assert product.id is None          # id присвоит база при сохранении
    assert product.name == "audi"
    assert product.description == "some descr"
    assert product.vehicle_type == VehicleType.HATCHBACK
    assert product.created_at is None  # created_at заполнит server_default
