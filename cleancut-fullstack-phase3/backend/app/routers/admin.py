from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Order, OrderItem, Product, User
from ..schemas.admin import ProductCreate, ProductUpdate, AdminOrderUpdate, AdminUserOut
from ..schemas.product import ProductOut
from .auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"] )

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def serialize_product(p: Product) -> dict:
    return {"id":p.id,"name":p.name,"slug":p.slug,"category":p.category,"price":p.price,"oldPrice":p.old_price,"tag":p.tag,"rating":p.rating,"reviews":p.reviews,"image":p.image,"description":p.description,"stock":p.stock,"is_active":p.is_active}

@router.get("/dashboard")
def dashboard(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    total_orders = db.scalar(select(func.count(Order.id))) or 0
    total_customers = db.scalar(select(func.count(User.id)).where(User.is_admin.is_(False))) or 0
    total_products = db.scalar(select(func.count(Product.id)).where(Product.is_active.is_(True))) or 0
    revenue = db.scalar(select(func.coalesce(func.sum(Order.total), 0)).where(Order.payment_status.in_(["Paid", "Cash on Delivery"]))) or 0
    pending = db.scalar(select(func.count(Order.id)).where(Order.status.in_(["Processing", "Pending"]))) or 0
    low_stock = db.scalar(select(func.count(Product.id)).where(Product.is_active.is_(True), Product.stock <= 10)) or 0
    since = datetime.utcnow() - timedelta(days=30)
    recent_revenue = db.scalar(select(func.coalesce(func.sum(Order.total), 0)).where(Order.created_at >= since, Order.payment_status.in_(["Paid", "Cash on Delivery"]))) or 0
    return {"total_orders":total_orders,"total_customers":total_customers,"total_products":total_products,"revenue":float(revenue),"pending_orders":pending,"low_stock_products":low_stock,"last_30_days_revenue":float(recent_revenue)}

@router.get("/products")
def products(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return [serialize_product(p) for p in db.scalars(select(Product).order_by(Product.id.desc())).all()]

@router.post("/products", status_code=201)
def create_product(payload: ProductCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    if db.scalar(select(Product).where(Product.slug == payload.slug)):
        raise HTTPException(status_code=409, detail="A product with this slug already exists")
    product=Product(**payload.model_dump()); db.add(product); db.commit(); db.refresh(product); return serialize_product(product)

@router.patch("/products/{product_id}")
def update_product(product_id:int, payload:ProductUpdate, _:User=Depends(require_admin), db:Session=Depends(get_db)):
    product=db.get(Product,product_id)
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    data=payload.model_dump(exclude_unset=True)
    if "slug" in data:
        duplicate=db.scalar(select(Product).where(Product.slug==data["slug"], Product.id!=product_id))
        if duplicate: raise HTTPException(status_code=409, detail="A product with this slug already exists")
    for k,v in data.items(): setattr(product,k,v)
    db.commit(); db.refresh(product); return serialize_product(product)

@router.delete("/products/{product_id}")
def archive_product(product_id:int, _:User=Depends(require_admin), db:Session=Depends(get_db)):
    product=db.get(Product,product_id)
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    product.is_active=False; db.commit(); return {"message":"Product archived"}

@router.get("/orders")
def orders(_:User=Depends(require_admin), db:Session=Depends(get_db), status:str|None=Query(default=None)):
    q=select(Order).order_by(Order.created_at.desc())
    if status: q=q.where(Order.status==status)
    rows=db.scalars(q).all()
    return [{"id":o.id,"order_number":o.order_number,"customer_name":o.customer_name,"user_id":o.user_id,"total":o.total,"status":o.status,"payment_method":o.payment_method,"payment_status":o.payment_status,"city":o.city,"created_at":o.created_at,"items":db.scalar(select(func.sum(OrderItem.quantity)).where(OrderItem.order_id==o.id)) or 0} for o in rows]

@router.patch("/orders/{order_id}")
def update_order(order_id:int,payload:AdminOrderUpdate, _:User=Depends(require_admin),db:Session=Depends(get_db)):
    order=db.get(Order,order_id)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    data=payload.model_dump(exclude_unset=True)
    for k,v in data.items(): setattr(order,k,v)
    db.commit(); db.refresh(order); return {"message":"Order updated","order_id":order.id,"status":order.status,"payment_status":order.payment_status}

@router.get("/customers", response_model=list[AdminUserOut])
def customers(_:User=Depends(require_admin), db:Session=Depends(get_db)):
    return db.scalars(select(User).order_by(User.created_at.desc())).all()
