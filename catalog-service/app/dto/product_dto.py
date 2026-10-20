from pydantic import BaseModel

from app.models.vehicle_type import VehicleType


class ProductDto(BaseModel):
    """Ответ API: продукт без служебных полей."""

    id: int
    name: str
    description: str
    vehicle_type: VehicleType


class ProductCreateDto(BaseModel):
    """Тело запроса на создание продукта."""

    name: str
    description: str
    vehicle_type: VehicleType
