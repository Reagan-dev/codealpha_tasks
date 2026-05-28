# CodeAlpha Backend Development Internship

Four production-ready REST APIs built with Django, DRF, JWT, and PostgreSQL — deployed on Railway.

![Python 3.12](https://img.shields.io/badge/Python-3.12-blue) ![Django](https://img.shields.io/badge/Django-5.0-darkgreen) ![DRF](https://img.shields.io/badge/DRF-3.14-red) ![JWT](https://img.shields.io/badge/Auth-JWT-orange) ![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791) ![Railway](https://img.shields.io/badge/Hosting-Railway-0B0D0E) ![PEP 8](https://img.shields.io/badge/Style-PEP%208-brightgreen)

---

## Internship Overview

CodeAlpha Backend Development Internship (May 2026) is a hands-on program focused on building production-grade REST APIs using Django and Django REST Framework. This repository contains four complete backend projects that demonstrate real-world API design patterns, authentication, database optimization, and cloud deployment. Each project tackles distinct business domains while maintaining consistent development standards across the codebase.

---

## Projects

| Task | Project | Description | Live API | Tech Highlights |
|------|---------|-------------|----------|-----------------|
| Task 1 | URL Shortener | Generate shareable short links with QR codes, click analytics, and expiration policies. | [Live API](https://codealphatasks-production-9019.up.railway.app/swagger/) | QR code generation, click tracking, TTL expiry, URL validation |
| Task 2 | Event Registration System | Manage event registrations with automated ticket assignment, waitlist handling, and email notifications. | [Live API](https://codealphatasks-production-4c1d.up.railway.app/swagger/) | Waitlist management, automated ticket numbers, email notifications, capacity limits |
| Task 3 | Restaurant Management System | Handle orders, inventory, and revenue tracking with real-time stock management and daily sales reporting. | [Live API](https://protective-reprieve-production-1460.up.railway.app/swagger/) | Inventory signals, order pipeline tracking, daily sales reports, stock automation |
| Task 4 | Job Board Platform | Post jobs, manage applications, upload resumes, and track candidate pipeline with employer dashboard. | [Live API](https://alluring-clarity-production-2529.up.railway.app/swagger/) | Resume uploads, application status pipeline, employer filtering, candidate rankings |

> Each project has its own README with full setup instructions, endpoint documentation, and seed data guide. Click the project folder to read it.

---

## Tech Stack

| Layer | Technology | Used In |
|-------|-----------|---------|
| **Framework** | Django 5.0 + Django REST Framework 3.14 | All tasks |
| **Authentication** | JWT (SimpleJWT) | All tasks |
| **Database** | PostgreSQL (production) / SQLite (development) | All tasks |
| **API Documentation** | drf-yasg (Swagger + ReDoc) | All tasks |
| **Deployment** | Railway | All tasks |
| **Static Files** | Whitenoise | All tasks |
| **Email** | Django Email Backend / Gmail SMTP | Tasks 2, 4 |
| **File Uploads** | Django FileField / ImageField | Tasks 3, 4 |
| **Database Signals** | Django post_save signals | Task 3 |
| **QR Codes** | qrcode[pil] | Task 1 |

---

## Repository Structure

```
CodeAlpha_Backend/
├── task1_url_shortener/
│   ├── config/              # Django project settings, URLs, WSGI
│   ├── shortener/           # Main app — models, views, serializers
│   ├── static/              # Static assets
│   ├── requirements.txt     # Python dependencies
│   ├── manage.py            # Django management script
│   ├── Procfile             # Railway deployment config
│   └── README.md            # Project-level documentation
│
├── task2_event_registration/
│   ├── config/              # Django project settings, URLs, WSGI
│   ├── accounts/            # User authentication app
│   ├── events/              # Events and registration management
│   ├── requirements.txt
│   ├── manage.py
│   ├── Procfile
│   └── README.md
│
├── task3_restaurant_mgmt/
│   ├── config/              # Django project settings, URLs, WSGI
│   ├── accounts/            # User and staff management
│   ├── inventory/           # Stock and inventory tracking
│   ├── menu/                # Menu items and categories
│   ├── orders/              # Order processing and fulfillment
│   ├── media/               # Uploaded files
│   ├── requirements.txt
│   ├── manage.py
│   ├── Procfile
│   └── README.md
│
├── task4_job_board/
│   ├── config/              # Django project settings, URLs, WSGI
│   ├── accounts/            # User authentication and profiles
│   ├── applications/        # Job applications management
│   ├── jobs/                # Job postings and employer tools
│   ├── media/               # Resume uploads
│   ├── requirements.txt
│   ├── manage.py
│   ├── Procfile
│   └── README.md
│
└── README.md                # This file
```

---

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/Reagan-dev/codealpha_tasks.git
cd codeAlpha_tasks
```

### Run Any Project Locally

1. Navigate to the project folder:
   ```bash
   cd url-shortener  # or task2_event_registration, etc.
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment template and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials, SECRET_KEY, etc.
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Load seed data:
   ```bash
   python manage.py seed_demo_data  # Task 1, 2, 4
   # OR
   python manage.py seed_data       # Task 3
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. Visit the interactive API docs:
   - Swagger UI: http://127.0.0.1:8000/swagger/
   - ReDoc: http://127.0.0.1:8000/redoc/

Each project's README contains the full environment variable reference and seed data credentials.

---

## Live Deployments

| Project | Live Swagger URL | Status |
|---------|------------------|--------|
| URL Shortener | [https://codealphatasks-production-9019.up.railway.app/swagger/](https://codealpha-url-shortener.railway.app/swagger/) | ✅ Active |
| Event Registration | [https://codealphatasks-production-4c1d.up.railway.app/swagger/](https://codealpha-event-registration.railway.app/swagger/) | ✅ Active |
| Restaurant Management | [https://protective-reprieve-production-1460.up.railway.app/swagger/](https://codealpha-restaurant-mgmt.railway.app/swagger/) | ✅ Active |
| Job Board | [https://alluring-clarity-production-2529.up.railway.app/swagger/](https://codealpha-job-board.railway.app/swagger/) | ✅ Active |

All projects are deployed on Railway free tier. First request after inactivity may take 30 seconds to wake the service.

---


Authentication: JWT Bearer Token

---

## Development Standards

- **Code Style:** PEP 8 strictly enforced across all projects
- **View Architecture:** Class-based views throughout (APIView, generics, ViewSets)
- **Authentication:** JWT authentication only — no session-based auth in any project
- **Serializers:** Separate serializer classes for list, detail, create, and update operations
- **Permissions:** Object-level permissions on all sensitive endpoints using DRF's permission system
- **Database Atomicity:** F() expressions for all counter increments (click counts, applied count, etc.) to prevent race conditions
- **Email Reliability:** try/except blocks on all email-sending functions with logging
- **Demo Data:** Seed management command (`seed_demo_data` or `seed_data`) in every project for consistent testing
- **Testing:** Unit tests covering critical business logic in every project (model methods, serializer validation, endpoint permissions)

---

## Testing

Run tests for any project:

```bash
# Task 1 — URL Shortener
cd url-shortener && python manage.py test shortener -v 2

# Task 2 — Event Registration System
cd event-registration-system && python manage.py test -v 2

# Task 3 — Restaurant Management System
cd restaurant-management-system && python manage.py test orders -v 2

# Task 4 — Job Board Platform
cd job-board-platform && python manage.py test applications -v 2
```

| Project | Test Classes | Key Scenarios Covered |
|---------|--------------|----------------------|
| URL Shortener | `ShortenURLTest`, `AnalyticsTest`, `QRCodeTest` | URL validation, short code generation, click tracking, expiry enforcement, QR generation |
| Event Registration | `EventTest`, `RegistrationTest`, `WaitlistTest` | Event creation, registration capacity limits, waitlist auto-promotion, duplicate prevention |
| Restaurant Management | `OrderTest`, `InventoryTest`, `SignalTest` | Order creation, status transitions, stock deduction via signals, daily sales aggregation |
| Job Board | `JobTest`, `ApplicationTest`, `PermissionTest` | Job posting, application pipeline, resume validation, employer-only endpoints, candidate filtering |

---

## Deployment

All four projects are deployed independently on Railway with separate PostgreSQL databases. Each service is configured with environment variables for database credentials, SECRET_KEY, and external API keys (e.g., email provider credentials).

Railway automatically deploys the `main` branch on every push. Deployment configuration is defined in the `Procfile` in each project root.

| Project | Railway Service | Database |
|---------|-----------------|----------|
| URL Shortener | `codealpha-url-shortener` | `codealpha_url_shortener_db` |
| Event Registration | `codealpha-event-registration` | `codealpha_event_registration_db` |
| Restaurant Management | `codealpha-restaurant-mgmt` | `codealpha_restaurant_mgmt_db` |
| Job Board | `codealpha-job-board` | `codealpha_job_board_db` |

Each project is an independent Railway service with its own PostgreSQL database. See individual project READMEs for environment variable references and Railway configuration details.

---

## Author

**Name:** Reagan Simiyu

**Internship:** CodeAlpha Backend Development Internship — May 2026


---

## Acknowledgements

Special thanks to **CodeAlpha** for this invaluable backend development internship opportunity. This repository showcases real-world API design with Django, Django REST Framework, PostgreSQL, and Railway deployment.

---

## License

MIT License — See `LICENSE` file for details.

```
Copyright (c) 2026 Reagan Simiyu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```
