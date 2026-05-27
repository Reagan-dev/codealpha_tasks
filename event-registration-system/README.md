# Event Registration System API

A Django REST Framework API for publishing events, registering attendees, issuing tickets, and managing waitlists.

Python 3.12 | Django 5 | DRF | JWT | Email | SQLite/PostgreSQL | Render

## Features

- User registration with MEMBER and ORGANIZER roles
- Organizers can create, update, and delete events
- Members can register for events, view registrations, and cancel
- Automatic waitlist management: cancellation promotes next waitlisted attendee to CONFIRMED
- Unique ticket numbers in TKT-YYYYMMDD-XXXXXX format
- Email notifications: registration confirmation, cancellation, waitlist promotion (console output in dev, SMTP in production)
- Event filtering: by category, status, upcoming only, search
- Swagger UI at /swagger/ and ReDoc at /redoc/

## Tech Stack

| Layer | Technology |
| --- | --- |
| Framework | Django 5, Django REST Framework |
| Auth | JWT with Simple JWT |
| API Docs | drf-yasg Swagger UI and ReDoc |
| Database | SQLite locally, PostgreSQL on Render |
| Deployment | Render, Gunicorn, WhiteNoise |
| Email | Django Email / Gmail SMTP |

## Project Structure

```bash
accounts/
├── models.py
├── permissions.py
├── serializers.py
├── urls.py
├── utils.py
└── views.py
events/
├── management/
│   └── commands/
│       └── seed_demo_data.py
├── models.py
├── permissions.py
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
git clone https://github.com/<your-username>/CodeAlpha_EventRegistration.git
cd CodeAlpha_EventRegistration
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
python manage.py seed_demo_data
```

7. Start the server:

```bash
python manage.py runserver
```

### Seed Data

| Role | Email | Password | Notes |
| --- | --- | --- | --- |
| ORGANIZER | organizer1@example.com | TestPass123! | Sarah Mwangi — 4 events |
| ORGANIZER | organizer2@example.com | TestPass123! | James Ochieng — 4 events |
| MEMBER | alice@example.com | TestPass123! | 5 registrations |
| MEMBER | bob@example.com | TestPass123! | 4 registrations |
| MEMBER | carol@example.com | TestPass123! | 4 registrations |
| MEMBER | dan@example.com | TestPass123! | WAITLISTED on Tech Summit |

### Environment Variables

| Variable | Description | Example |
| --- | --- | --- |
| SECRET_KEY | Django signing key | django-insecure-change-me |
| DEBUG | Enables development behavior | True |
| DATABASE_URL | Database connection URL | sqlite:///db.sqlite3 |
| ALLOWED_HOSTS | Comma-separated allowed hosts | localhost,127.0.0.1 |
| EMAIL_HOST_USER | SMTP username | your-email@gmail.com |
| EMAIL_HOST_PASSWORD | SMTP app password | app-password |

## API Endpoints

| Method | Endpoint | Role | Description |
| --- | --- | --- | --- |
| POST | /api/auth/register/ | AllowAny | Register a member or organizer |
| POST | /api/auth/token/ | AllowAny | Obtain JWT tokens |
| POST | /api/auth/token/refresh/ | AllowAny | Refresh JWT access token |
| GET | /api/auth/profile/ | Authenticated | Retrieve current profile |
| PATCH | /api/auth/profile/ | Authenticated | Update current profile |
|  |  |  |  |
| GET | /api/categories/ | AllowAny | List categories |
| GET | /api/events/ | AllowAny | List events with filters |
| POST | /api/events/ | ORGANIZER | Create an event |
| GET | /api/events/<pk>/ | AllowAny | Retrieve event detail |
| PATCH | /api/events/<pk>/manage/ | Event organizer | Update owned event |
| DELETE | /api/events/<pk>/manage/ | Event organizer | Delete owned event |
|  |  |  |  |
| GET | /api/registrations/ | Authenticated | List current user's registrations |
| POST | /api/registrations/ | Authenticated | Register for an event |
| POST | /api/registrations/<pk>/cancel/ | Registration owner | Cancel registration |

### Key Business Logic

- Full event registration creates a WAITLISTED registration instead of rejecting the member.
- Cancelling a confirmed registration promotes the next WAITLISTED attendee to CONFIRMED.
- `?upcoming=true` filters out past events and returns only future events.

## Authentication

This API uses JWT. Obtain a token pair via POST /api/auth/token/. Include the access token as a Bearer token in the Authorization header for protected endpoints.

```bash
Authorization: Bearer <access_token>
```

## Email Notifications

| Trigger | Recipient | Subject |
| --- | --- | --- |
| Registration confirmed | Member | Registration Confirmed — <event title> |
| Cancellation confirmed | Member | Registration Cancelled — <event title> |
| Waitlist promoted to confirmed | Member | Registration Confirmed — <event title> |

In development (DEBUG=True) emails print to the console. Set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in `.env` for Gmail SMTP.

## Running Tests

```bash
python manage.py test
```

- EventListTest: covers event filtering, search, and upcoming events.
- EventCreateUpdateTest: validates organizer-only event management.
- RegistrationCreateTest: covers confirmed registrations, duplicates, and waitlisting.
- RegistrationCancelTest: verifies cancellation and waitlist promotion.
- PermissionTest: checks role and ownership access rules.

## Deployment (Render.com)

1. Push the repository to GitHub.
2. Create a Render Web Service from the GitHub repo.
3. Set the build command to `bash build.sh`.
4. Set the start command from `Procfile`.
5. Add a Render PostgreSQL database and copy its `DATABASE_URL`.
6. Set all `.env` variables in Render's environment settings panel.
7. Deploy and verify `/swagger/` and `/redoc/`.

## Credits

Built for CodeAlpha Backend Development Internship — May 2026
