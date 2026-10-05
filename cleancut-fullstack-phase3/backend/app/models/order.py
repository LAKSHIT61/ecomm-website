from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from ..database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    order_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Processing")
    customer_name: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    phone: Mapped[str] = mapped_column(String(40), default="", nullable=False)
    address: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    city: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    pincode: Mapped[str] = mapped_column(String(12), default="", nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), default="cod", nullable=False)
    payment_status: Mapped[str] = mapped_column(String(40), default="Pending", nullable=False)
    razorpay_order_id: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True, index=True)
    razorpay_payment_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    razorpay_signature: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
