from pydantic import BaseModel, ConfigDict


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    price: float
    oldPrice: float | None
    tag: str | None
    rating: float
    reviews: str
    image: str
    description: str
    stock: int
