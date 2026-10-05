from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CartItem, Product, User
from ..schemas.cart import CartItemAdd, CartItemUpdate, CartOut
from .auth import get_current_user

router = APIRouter(prefix="/api/cart", tags=["cart"])


def serialize_cart(db: Session, user: User) -> CartOut:
    rows = db.scalars(select(CartItem).where(CartItem.user_id == user.id).order_by(CartItem.id)).all()
    items = []
    total = 0.0
    count = 0
    for row in rows:
        product = db.get(Product, row.product_id)
        if not product or not product.is_active:
            continue
        line = float(product.price) * row.quantity
        total += line
        count += row.quantity
        items.append({
            "product": {"id": product.id, "name": product.name, "price": product.price, "image": product.image, "stock": product.stock},
            "quantity": row.quantity,
            "line_total": line,
        })
    return CartOut(items=items, total=total, item_count=count)


@router.get("", response_model=CartOut)
def get_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return serialize_cart(db, current_user)


@router.post("/items", response_model=CartOut)
def add_item(payload: CartItemAdd, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.get(Product, payload.product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < payload.quantity:
        raise HTTPException(status_code=409, detail=f"Only {product.stock} item(s) are available")
    row = db.scalar(select(CartItem).where(CartItem.user_id == current_user.id, CartItem.product_id == product.id))
    if row:
        if row.quantity + payload.quantity > product.stock:
            raise HTTPException(status_code=409, detail=f"Only {product.stock} item(s) are available")
        row.quantity += payload.quantity
    else:
        db.add(CartItem(user_id=current_user.id, product_id=product.id, quantity=payload.quantity))
    db.commit()
    return serialize_cart(db, current_user)


@router.patch("/items/{product_id}", response_model=CartOut)
def update_item(product_id: int, payload: CartItemUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(CartItem).where(CartItem.user_id == current_user.id, CartItem.product_id == product_id))
    if not row:
        raise HTTPException(status_code=404, detail="Cart item not found")
    product = db.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    if payload.quantity > product.stock:
        raise HTTPException(status_code=409, detail=f"Only {product.stock} item(s) are available")
    row.quantity = payload.quantity
    db.commit()
    return serialize_cart(db, current_user)


@router.delete("/items/{product_id}", response_model=CartOut)
def remove_item(product_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(CartItem).where(CartItem.user_id == current_user.id, CartItem.product_id == product_id))
    if row:
        db.delete(row)
        db.commit()
    return serialize_cart(db, current_user)


@router.delete("", response_model=CartOut)
def clear_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(CartItem).where(CartItem.user_id == current_user.id)).all()
    for row in rows:
        db.delete(row)
    db.commit()
    return serialize_cart(db, current_user)
