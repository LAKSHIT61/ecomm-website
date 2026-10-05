from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Product
from ..schemas.product import ProductOut

router = APIRouter(prefix="/api/products", tags=["products"])


def serialize(product: Product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "price": product.price,
        "oldPrice": product.old_price,
        "tag": product.tag,
        "rating": product.rating,
        "reviews": product.reviews,
        "image": product.image,
        "description": product.description,
        "stock": product.stock,
    }


@router.get("", response_model=list[ProductOut])
def list_products(
    category: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(Product).where(Product.is_active.is_(True))
    if category and category.lower() != "all":
        query = query.where(Product.category == category.lower())
    if search:
        term = f"%{search.strip()}%"
        query = query.where(or_(Product.name.ilike(term), Product.description.ilike(term)))
    products = db.scalars(query.order_by(Product.id)).all()
    return [serialize(product) for product in products]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize(product)
