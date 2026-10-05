from datetime import datetime
from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    slug: str = Field(min_length=2, max_length=180)
    category: str = Field(min_length=2, max_length=60)
    price: float = Field(gt=0)
    old_price: float | None = Field(default=None, gt=0)
    tag: str | None = Field(default=None, max_length=60)
    rating: float = Field(default=0, ge=0, le=5)
    reviews: str = Field(default="0", max_length=30)
    image: str = Field(min_length=1, max_length=500)
    description: str = ""
    stock: int = Field(default=0, ge=0)
    is_active: bool = True

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    slug: str | None = Field(default=None, min_length=2, max_length=180)
    category: str | None = Field(default=None, min_length=2, max_length=60)
    price: float | None = Field(default=None, gt=0)
    old_price: float | None = Field(default=None, gt=0)
    tag: str | None = Field(default=None, max_length=60)
    rating: float | None = Field(default=None, ge=0, le=5)
    reviews: str | None = Field(default=None, max_length=30)
    image: str | None = Field(default=None, max_length=500)
    description: str | None = None
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

class AdminOrderUpdate(BaseModel):
    status: str | None = Field(default=None, max_length=40)
    payment_status: str | None = Field(default=None, max_length=40)

class AdminUserOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    address: str | None
    is_admin: bool
    created_at: datetime
    model_config = {"from_attributes": True}
