# CleanCut Full-Stack — Phase 4

Premium beauty e-commerce frontend + FastAPI backend + SQLAlchemy database.

## Included

- Premium CleanCut storefront UI
- FastAPI backend
- SQLite for local development
- PostgreSQL-ready configuration
- Product catalogue API
- Secure signup/login with scrypt password hashing + JWT
- User profile API
- Persistent authenticated shopping cart
- Guest cart that syncs into the account after login/signup
- Database-backed checkout
- Cash-on-delivery order creation
- Stock validation and automatic stock decrement when an order is created
- Customer order history and order details
- API documentation at `/docs`

## Run locally

From the `backend` directory:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\\Scripts\\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app from the project root:

```bash
uvicorn backend.app.main:app --reload
```

Open:

- Storefront: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/health`

## Phase 4 API

### Cart

```text
GET    /api/cart
POST   /api/cart/items
PATCH  /api/cart/items/{product_id}
DELETE /api/cart/items/{product_id}
DELETE /api/cart
```

### Orders

```text
GET  /api/orders
GET  /api/orders/{order_number}
POST /api/orders
```

The checkout endpoint currently supports **Cash on Delivery**. Online payment is intentionally reserved for Phase 5 so no fake payment-success flow is exposed.

## Next phase

Phase 5 will add Razorpay payment creation + server-side payment verification and connect successful payments to the existing order system.

## Phase 5 — Razorpay payments

Online payments are now supported through Razorpay. For local testing:

1. Copy `backend/.env.example` to `backend/.env`.
2. Add your Razorpay **Key ID** and **Key Secret**.
3. Install dependencies with `pip install -r requirements.txt`.
4. Start FastAPI and open `http://127.0.0.1:8000/checkout.html`.

The secret key is only used by the backend. The browser receives the public Key ID and Razorpay Order ID. The backend verifies the Razorpay signature before marking the order as paid and reducing inventory.

COD remains available without Razorpay credentials.


## Phase 6 — Admin dashboard

Create/promote an admin account from the backend directory:

```bash
python -m app.create_admin --email admin@example.com --password "Use-a-strong-password"
```

Then sign in at `/login.html` with that account and open `/admin.html`. Admin APIs are protected by the `is_admin` flag. Never commit production credentials or JWT/Razorpay secrets.

## Deployment

See `DEPLOYMENT.md` for the Render + PostgreSQL production deployment path. The repository includes `render.yaml` for one-click Blueprint provisioning.
