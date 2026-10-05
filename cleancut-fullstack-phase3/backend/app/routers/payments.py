from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
import base64
import hashlib
import hmac
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from ..config import settings
from ..database import get_db
from ..models import CartItem, Order, OrderItem, Product, User
from .auth import get_current_user
from .orders import serialize_order, make_order_number

router = APIRouter(prefix="/api/payments", tags=["payments"])


def razorpay_request(path: str, payload: dict) -> dict:
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise HTTPException(status_code=503, detail="Online payments are not configured yet. Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to backend/.env")
    token = base64.b64encode(f"{settings.razorpay_key_id}:{settings.razorpay_key_secret}".encode()).decode()
    body = json.dumps(payload).encode()
    request = Request(f"https://api.razorpay.com/v1/{path}", data=body, method="POST", headers={
        "Authorization": f"Basic {token}", "Content-Type": "application/json"
    })
    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode())
    except (HTTPError, URLError, TimeoutError) as exc:
        raise HTTPException(status_code=502, detail="Could not communicate with Razorpay") from exc


def verify_signature(order_id: str, payment_id: str, signature: str) -> bool:
    message = f"{order_id}|{payment_id}".encode()
    expected = hmac.new(settings.razorpay_key_secret.encode(), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


class PaymentOrderRequest(BaseModel):
    full_name: str
    phone: str
    address: str
    city: str
    pincode: str


class PaymentVerifyRequest(BaseModel):
    internal_order_number: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/razorpay/order")
def create_razorpay_order(payload: PaymentOrderRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_rows = db.scalars(select(CartItem).where(CartItem.user_id == current_user.id).order_by(CartItem.id)).all()
    if not cart_rows:
        raise HTTPException(status_code=400, detail="Your cart is empty")
    products=[]; total=0.0
    for row in cart_rows:
        product=db.get(Product,row.product_id)
        if not product or not product.is_active: raise HTTPException(status_code=409, detail="A product in your cart is unavailable")
        if row.quantity > product.stock: raise HTTPException(status_code=409, detail=f"Not enough stock for {product.name}")
        products.append((row,product)); total += float(product.price)*row.quantity
    amount_paise=int(round(total*100))
    remote = razorpay_request("orders", {"amount":amount_paise,"currency":"INR","receipt":make_order_number(db),"notes":{"user_id":str(current_user.id)}})
    order=Order(user_id=current_user.id,order_number=make_order_number(db),total=total,status="Awaiting Payment",customer_name=payload.full_name.strip(),phone=payload.phone.strip(),address=payload.address.strip(),city=payload.city.strip(),pincode=payload.pincode.strip(),payment_method="online",payment_status="Pending",razorpay_order_id=remote["id"])
    db.add(order); db.flush()
    for row,product in products:
        db.add(OrderItem(order_id=order.id,product_id=product.id,quantity=row.quantity,unit_price=product.price))
    db.commit(); db.refresh(order)
    return {"key_id":settings.razorpay_key_id,"razorpay_order_id":remote["id"],"amount":amount_paise,"currency":"INR","order_number":order.order_number}


@router.post("/razorpay/verify")
def verify_razorpay_payment(payload: PaymentVerifyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order=db.scalar(select(Order).where(Order.order_number==payload.internal_order_number,Order.user_id==current_user.id))
    if not order or order.payment_method!="online": raise HTTPException(status_code=404, detail="Payment order not found")
    if order.payment_status=="Paid": return serialize_order(db,order)
    if order.razorpay_order_id != payload.razorpay_order_id: raise HTTPException(status_code=400,detail="Payment order mismatch")
    if not verify_signature(payload.razorpay_order_id, payload.razorpay_payment_id, payload.razorpay_signature):
        raise HTTPException(status_code=400,detail="Payment verification failed")
    items=db.scalars(select(OrderItem).where(OrderItem.order_id==order.id)).all()
    for item in items:
        product=db.get(Product,item.product_id)
        if not product or not product.is_active or product.stock < item.quantity:
            raise HTTPException(status_code=409,detail="Stock changed while payment was being completed. Contact support before placing another order.")
    for item in items:
        product=db.get(Product,item.product_id); product.stock -= item.quantity
    cart_rows=db.scalars(select(CartItem).where(CartItem.user_id==current_user.id)).all()
    for row in cart_rows: db.delete(row)
    order.status="Processing"; order.payment_status="Paid"; order.razorpay_payment_id=payload.razorpay_payment_id; order.razorpay_signature=payload.razorpay_signature
    db.commit(); db.refresh(order)
    return serialize_order(db,order)
