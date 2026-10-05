from pydantic import BaseModel, Field


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1, le=99)


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=99)


class CartProductOut(BaseModel):
    id: int
    name: str
    price: float
    image: str
    stock: int


class CartItemOut(BaseModel):
    product: CartProductOut
    quantity: int
    line_total: float


class CartOut(BaseModel):
    items: list[CartItemOut]
    total: float
    item_count: int
