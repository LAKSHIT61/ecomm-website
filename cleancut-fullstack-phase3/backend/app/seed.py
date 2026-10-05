from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Product

PRODUCTS = [
    dict(id=1, name="Gentle Face Cleanser", slug="gentle-face-cleanser", category="skincare", price=499, old_price=699, tag="Bestseller", rating=4.8, reviews="1.2K", image="assets/images/cleanser.jpg", description="A gentle everyday cleanser designed to leave skin feeling fresh, clean and comfortable.", stock=120),
    dict(id=2, name="Glow Serum", slug="glow-serum", category="skincare", price=899, old_price=1299, tag="Bestseller", rating=4.9, reviews="2.1K", image="assets/images/serum.jpg", description="A lightweight glow serum designed for a hydrated, luminous-looking complexion.", stock=85),
    dict(id=3, name="Daily Moisturizer", slug="daily-moisturizer", category="beauty", price=699, old_price=999, tag="New", rating=4.7, reviews="980", image="assets/images/moisturizer.jpg", description="An everyday moisturizer designed to keep skin feeling soft and hydrated.", stock=95),
    dict(id=4, name="Facial Roller Set", slug="facial-roller-set", category="tools", price=599, old_price=899, tag="Trending", rating=4.6, reviews="843", image="assets/images/roller.jpg", description="A simple facial massage set for an elevated self-care routine.", stock=60),
    dict(id=5, name="Sun Defense SPF 50", slug="sun-defense-spf-50", category="skincare", price=699, old_price=999, tag="Popular", rating=4.8, reviews="1.4K", image="assets/images/sunscreen.jpg", description="Daily sun protection for a comfortable, easy-to-layer routine.", stock=140),
    dict(id=6, name="Hydrating Lip Mask", slug="hydrating-lip-mask", category="beauty", price=399, old_price=599, tag="Bestseller", rating=4.7, reviews="920", image="assets/images/lip-mask.jpg", description="A nourishing lip mask designed for soft, hydrated-looking lips.", stock=110),
]


def seed_products(db: Session):
    existing = db.scalars(select(Product)).first()
    if existing:
        return
    db.add_all(Product(**item) for item in PRODUCTS)
    db.commit()
