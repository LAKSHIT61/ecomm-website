from datetime import datetime
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CartItem, Order, OrderItem, Product, User
from ..schemas.order import CheckoutRequest, OrderOut
from .auth import get_current_user

router = APIRouter(prefix="/api/orders", tags=["orders"])


def serialize_order(db: Session, order: Order) -> OrderOut:
    rows = db.scalars(select(OrderItem).where(OrderItem.order_id == order.id).order_by(OrderItem.id)).all()
    items = []
    for row in rows:
        product = db.get(Product, row.product_id)
        items.append({
            "product_id": row.product_id,
            "product_name": product.name if product else "Product",
            "image": product.image if product else "",
            "quantity": row.quantity,
            "unit_price": row.unit_price,
            "line_total": row.unit_price * row.quantity,
        })
    return OrderOut(
        id=order.id, order_number=order.order_number, total=order.total, status=order.status,
        payment_method=order.payment_method, payment_status=order.payment_status,
        customer_name=order.customer_name, phone=order.phone, address=order.address,
        city=order.city, pincode=order.pincode, created_at=order.created_at, items=items,
    )


def make_order_number(db: Session) -> str:
    while True:
        number = f"CC{datetime.utcnow():%y%m%d}{secrets.randbelow(9000)+1000}"
        if not db.scalar(select(Order).where(Order.order_number == number)):
            return number


@router.get("", response_model=list[OrderOut])
def list_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.scalars(select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc())).all()
    return [serialize_order(db, order) for order in orders]


@router.get("/{order_number}", response_model=OrderOut)
def get_order(order_number: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.scalar(select(Order).where(Order.order_number == order_number, Order.user_id == current_user.id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return serialize_order(db, order)


@router.post("", response_model=OrderOut, status_code=201)
def create_order(payload: CheckoutRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_rows = db.scalars(select(CartItem).where(CartItem.user_id == current_user.id).order_by(CartItem.id)).all()
    if not cart_rows:
        raise HTTPException(status_code=400, detail="Your cart is empty")

    products = []
    total = 0.0
    for row in cart_rows:
        product = db.get(Product, row.product_id)
        if not product or not product.is_active:
            raise HTTPException(status_code=409, detail="One of the products in your cart is no longer available")
        if row.quantity > product.stock:
            raise HTTPException(status_code=409, detail=f"Not enough stock for {product.name}")
        products.append((row, product))
        total += product.price * row.quantity

    order = Order(
        user_id=current_user.id,
        order_number=make_order_number(db),
        total=total,
        status="Processing",
        customer_name=payload.full_name.strip(),
        phone=payload.phone.strip(),
        address=payload.address.strip(),
        city=payload.city.strip(),
        pincode=payload.pincode.strip(),
        payment_method=payload.payment_method,
        payment_status="Pending" if payload.payment_method == "online" else "Cash on Delivery",
    )
    db.add(order)
    db.flush()

    for row, product in products:
        db.add(OrderItem(order_id=order.id, product_id=product.id, quantity=row.quantity, unit_price=product.price))
        product.stock -= row.quantity
        db.delete(row)

    db.commit()
    db.refresh(order)
    return serialize_order(db, order)
