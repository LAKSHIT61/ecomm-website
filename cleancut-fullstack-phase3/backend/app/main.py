from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from .config import settings
from .database import Base, SessionLocal, engine
from . import models  # noqa: F401
from .routers.products import router as products_router
from .routers.auth import router as auth_router
from .routers.cart import router as cart_router
from .routers.orders import router as orders_router
from .routers.payments import router as payments_router
from .routers.admin import router as admin_router
from .seed import seed_products

PROJECT_ROOT = Path(__file__).resolve().parents[2]

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(products_router)
app.include_router(auth_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(admin_router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    # Small compatibility migration for databases created during Phase 2.
    # Production deployments should use Alembic migrations once the schema grows.
    inspector = inspect(engine)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    order_columns = {column["name"] for column in inspector.get_columns("orders")}
    with engine.begin() as connection:
        if "phone" not in user_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(40)"))
        if "address" not in user_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN address VARCHAR(500)"))
        if "is_admin" not in user_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL"))
        order_migrations = {
            "customer_name": "VARCHAR(120) DEFAULT ''",
            "phone": "VARCHAR(40) DEFAULT ''",
            "address": "VARCHAR(500) DEFAULT ''",
            "city": "VARCHAR(100) DEFAULT ''",
            "pincode": "VARCHAR(12) DEFAULT ''",
            "payment_method": "VARCHAR(20) DEFAULT 'cod'",
            "payment_status": "VARCHAR(40) DEFAULT 'Pending'",
            "razorpay_order_id": "VARCHAR(80)",
            "razorpay_payment_id": "VARCHAR(80)",
            "razorpay_signature": "VARCHAR(200)",
        }
        for column, definition in order_migrations.items():
            if column not in order_columns:
                connection.execute(text(f"ALTER TABLE orders ADD COLUMN {column} {definition}"))
    with SessionLocal() as db:
        seed_products(db)


@app.get("/api/health")
def health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok", "service": settings.app_name, "database": "connected"}


@app.get("/api")
def api_root():
    return {"message": "CleanCut API is running", "docs": "/docs"}


# Serve the existing frontend from the same FastAPI app so local development
# only needs one server command.
app.mount("/assets", StaticFiles(directory=PROJECT_ROOT / "assets"), name="assets")
app.mount("/css", StaticFiles(directory=PROJECT_ROOT / "css"), name="css")
app.mount("/js", StaticFiles(directory=PROJECT_ROOT / "js"), name="js")


@app.get("/{page_name}.html", include_in_schema=False)
def frontend_page(page_name: str):
    candidate = PROJECT_ROOT / f"{page_name}.html"
    if candidate.exists():
        return FileResponse(candidate)
    return FileResponse(PROJECT_ROOT / "index.html")


@app.get("/", include_in_schema=False)
def frontend_root():
    return FileResponse(PROJECT_ROOT / "index.html")
