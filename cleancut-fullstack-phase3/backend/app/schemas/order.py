from datetime import datetime
from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=7, max_length=40)
    address: str = Field(min_length=5, max_length=500)
    city: str = Field(min_length=2, max_length=100)
    pincode: str = Field(min_length=4, max_length=12)
    payment_method: str = Field(default="cod", pattern="^(cod|online)$")


class OrderItemOut(BaseModel):
    product_id: int
    product_name: str
    image: str
    quantity: int
    unit_price: float
    line_total: float


class OrderOut(BaseModel):
    id: int
    order_number: str
    total: float
    status: str
    payment_method: str
    payment_status: str
    customer_name: str
    phone: str
    address: str
    city: str
    pincode: str
    created_at: datetime
    items: list[OrderItemOut]
