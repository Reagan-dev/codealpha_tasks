# URL Shortener API

A Django REST Framework API for creating compact, trackable short links with optional custom aliases, expiry dates, and QR codes.

Python 3.12 | Django 5 | DRF | JWT | SQLite/PostgreSQL | Render

## Features

- Shorten any valid URL to a 6-character code
- Custom alias support (alphanumeric + hyphens)
- Link expiry via expires_in_days parameter
- Click count tracking (atomic, race-condition safe via F() expressions)
- QR code generation (PNG download)
- JWT-authenticated link management (list, detail, delete own links)
- Swagger UI at /swagger/ and ReDoc at /redoc/

## Tech Stack

| Layer | Technology |
| --- | --- |
| Framework | Django 5, Django REST Framework |
| Auth | JWT with Simple JWT |
| API Docs | drf-yasg Swagger UI and ReDoc |
| Database | SQLite locally, PostgreSQL on Render |
| Deployment | Render, Gunicorn, WhiteNoise |
| QR Codes | qrcode / Pillow |

## Project Structure

```bash
shortener/
├── admin.py
├── apps.py
├── models.py
├── serializers.py
├── tests.py
├── urls.py
├── utils.py
└── views.py
```

## Getting Started

### Prerequisites

Python 3.12+ and pip.

### Installation

1. Clone the repo and enter the project directory:

```bash
git clone https://github.com/<your-username>/CodeAlpha_URLShortener.git
cd CodeAlpha_URLShortener
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

6. Create a superuser (optional):

```bash
python manage.py createsuperuser
```

7. Start the server:

```bash
python manage.py runserver
```

### Environment Variables

| Variable | Description | Example |
| --- | --- | --- |
| SECRET_KEY | Django signing key | django-insecure-change-me |
| DEBUG | Enables development behavior | True |
| DATABASE_URL | Database connection URL | sqlite:///db.sqlite3 |
| ALLOWED_HOSTS | Comma-separated allowed hosts | localhost,127.0.0.1 |

## API Endpoints

| Method | Endpoint | Auth Required | Description |
| --- | --- | --- | --- |
| POST | /api/auth/token/ | No | Obtain JWT access and refresh tokens |
| POST | /api/auth/token/refresh/ | No | Refresh an access token |
| POST | /api/shorten/ | No | Create a short URL |
| GET | /s/<short_code>/ | No | Redirect to the original URL and count click |
| GET | /api/links/ | Yes | List authenticated user's links |
| GET | /api/links/<short_code>/ | Yes | Retrieve one owned link |
| DELETE | /api/links/<short_code>/ | Yes | Delete one owned link |
| GET | /api/links/<short_code>/qr/ | No | Download QR code PNG |

### Quick Example

```bash
curl -X POST http://127.0.0.1:8000/api/shorten/ \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://www.djangoproject.com/"}'
```

```bash
curl -L http://127.0.0.1:8000/s/abc123/
```

```bash
curl http://127.0.0.1:8000/api/links/abc123/qr/ --output qr.png
```

## Authentication

This API uses JWT. Obtain a token pair via POST /api/auth/token/. Include the access token as a Bearer token in the Authorization header for protected endpoints.

```bash
Authorization: Bearer <access_token>
```

## Running Tests

```bash
python manage.py test shortener
```

- ShortenURLTest: validates URL shortening, aliases, and expiry rules.
- RedirectTest: verifies redirects and atomic click counting.
- LinkManagementTest: checks authenticated listing, detail, and delete access.
- QRCodeTest: verifies PNG QR code generation.

## Deployment (Render.com)

1. Push the repository to GitHub.
2. Create a Render Web Service from the GitHub repo.
3. Set the build command to `bash build.sh`.
4. Set the start command from `Procfile`.
5. Add a Render PostgreSQL database and copy its `DATABASE_URL`.
6. Set all `.env` variables in Render's environment settings panel.
7. Deploy and open `/swagger/` to verify the API.

## Credits

Built for CodeAlpha Backend Development Internship — May 2026
