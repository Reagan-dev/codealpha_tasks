# Restaurant Management System API

A Django REST Framework API for restaurant menus, reservations, orders, inventory, and daily sales reporting.

Python 3.12 | Django 5 | DRF | JWT | Signals | SQLite/PostgreSQL | Render

## Features

- Three user roles: CUSTOMER, STAFF, MANAGER with scoped access
- Full menu management (categories + items) with ingredient tracking
- Table reservations with conflict detection (overlapping time windows)
- Order placement with multi-item support and automatic total calculation
- Inventory auto-deduction on order creation via Django signals (atomic via F() expressions)
- Inventory auto-restoration on order cancellation via signals
- Low stock detection with configurable reorder levels
- Daily sales report: total revenue, order count, top 5 items, avg value
- Order status progression: RECEIVED → PREPARING → READY → SERVED
- Swagger UI at /swagger/ and ReDoc at /redoc/

## Tech Stack

| Layer | Technology |
| --- | --- |
| Framework | Django 5, Django REST Framework |
| Auth | JWT with Simple JWT |
| API Docs | drf-yasg Swagger UI and ReDoc |
| Database | SQLite locally, PostgreSQL on Render |
| Deployment | Render, Gunicorn, WhiteNoise |
| Signals | Django post_save signals |

## Project Structure

```bash
accounts/
├── models.py
├── permissions.py
├── serializers.py
├── urls.py
└── views.py
menu/
├── models.py
├── serializers.py
├── urls.py
└── views.py
reservations/
├── models.py
├── serializers.py
├── urls.py
└── views.py
orders/
├── apps.py
├── management/
│   └── commands/
│       └── seed_data.py
├── models.py
├── serializers.py
├── signals.py
├── urls.py
└── views.py
inventory/
├── models.py
├── serializers.py
├── urls.py
└── views.py
```

## Getting Started

### Prerequisites

Python 3.12+ and pip.

### Installation

1. Clone the repo and enter the project directory:

```bash
git clone https://github.com/<your-username>/CodeAlpha_RestaurantManagement.git
cd CodeAlpha_RestaurantManagement
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and fill in values.
5. Run migrations:

```bash
python manage.py migrate
```

6. Seed demo data:

```bash
python manage.py seed_data
```

7. Start the server:

```bash
python manage.py runserver
```

### Seed Data

| Role | Email | Password |
| --- | --- | --- |
| MANAGER | manager@restaurant.com | Manager@1234 |
| STAFF | staff1@restaurant.com | Staff@1234 |
| STAFF | staff2@restaurant.com | Staff@1234 |
| CUSTOMER | customer1@email.com | Customer@1234 |
| CUSTOMER | customer2@email.com | Customer@1234 |
| CUSTOMER | customer3@email.com | Customer@1234 |

### Seeded Demo State

- 3 SERVED orders today — daily sales report returns non-zero revenue
- 1 inventory item is below reorder level — visible via GET /api/inventory/?low_stock=true
- 2 reservations exist for today/tomorrow

### Environment Variables

| Variable | Description | Example |
| --- | --- | --- |
| SECRET_KEY | Django signing key | django-insecure-change-me |
| DEBUG | Enables development behavior | True |
| DATABASE_URL | Database connection URL | sqlite:///db.sqlite3 |
| ALLOWED_HOSTS | Comma-separated allowed hosts | localhost,127.0.0.1 |

## API Endpoints

### Menu

| Method | Endpoint | Role | Description |
| --- | --- | --- | --- |
| GET | /api/menu/categories/ | AllowAny | List menu categories |
| GET | /api/menu/items/ | AllowAny | List menu items |
| POST | /api/menu/items/ | STAFF or MANAGER | Create menu item |
| GET | /api/menu/items/<pk>/ | AllowAny | Retrieve menu item detail |
| PATCH | /api/menu/items/<pk>/manage/ | STAFF or MANAGER | Update menu item |
| DELETE | /api/menu/items/<pk>/manage/ | MANAGER | Delete menu item |

### Tables & Reservations

| Method | Endpoint | Role | Description |
| --- | --- | --- | --- |
| GET | /api/tables/ | AllowAny | List restaurant tables |
| GET | /api/reservations/ | Authenticated | List current user's reservations |
| POST | /api/reservations/ | Authenticated | Create reservation |
| GET | /api/reservations/<pk>/ | Owner or staff | Retrieve reservation |
| PATCH | /api/reservations/<pk>/ | Owner or staff | Update reservation |
| POST | /api/reservations/<pk>/cancel/ | Owner or staff | Cancel reservation |

### Orders

| Method | Endpoint | Role | Description |
| --- | --- | --- | --- |
| GET | /api/orders/ | STAFF or owner | List orders |
| POST | /api/orders/ | Authenticated | Place order |
| GET | /api/orders/<pk>/ | STAFF or owner | Retrieve order detail |
| PATCH | /api/orders/<pk>/status/ | STAFF | Update order status |

### Inventory & Reports

| Method | Endpoint | Role | Description |
| --- | --- | --- | --- |
| GET | /api/inventory/ | STAFF or MANAGER | List inventory |
| PATCH | /api/inventory/<pk>/restock/ | MANAGER | Restock inventory item |
| GET | /api/reports/daily-sales/ | STAFF or MANAGER | Daily sales report |

### Key Business Logic

- Signal-based inventory deduction uses F() expressions so stock changes happen atomically in the database.
- Signal-based restoration returns inventory when an order becomes CANCELLED.
- Reservation conflict detection checks overlapping time windows for the same table.
- Daily sales report accepts `?date=YYYY-MM-DD` and defaults to today.

## Authentication

This API uses JWT. Obtain a token pair via POST /api/auth/token/. Include the access token as a Bearer token in the Authorization header for protected endpoints.

```bash
Authorization: Bearer <access_token>
```

## Django Signals

The post_save signal on OrderItem deducts ingredient quantities from inventory when items are ordered. The post_save signal on Order restores ingredient quantities when an order is cancelled. `orders/apps.py` must use `OrdersConfig.ready()` so Django imports the signal handlers when the app starts.

## Running Tests

```bash
python manage.py test orders
```

- OrderCreationTest: validates order creation, totals, and item handling.
- InventorySignalTest: verifies deduction and restoration behavior.
- OrderStatusTest: validates allowed status progression.
- DailySalesReportTest: checks revenue, order count, and top item reporting.

## Deployment (Render.com)

1. Push the repository to GitHub.
2. Create a Render Web Service from the GitHub repo.
3. Set the build command to `bash build.sh`.
4. Set the start command from `Procfile`.
5. Add a Render PostgreSQL database and copy its `DATABASE_URL`.
6. Set all `.env` variables in Render's environment settings panel.
7. Ensure INSTALLED_APPS uses `orders.apps.OrdersConfig` not just `orders` — signals will not fire without this.

## Credits

Built for CodeAlpha Backend Development Internship — May 2026
