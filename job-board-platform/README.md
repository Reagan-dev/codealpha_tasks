# Job Board Platform API

A Django REST Framework API for employers, candidates, job listings, resumes, applications, and hiring workflows.

Python 3.12 | Django 5 | DRF | JWT | File Uploads | SQLite/PostgreSQL | Render

## Features

- Two user roles: EMPLOYER and CANDIDATE with scoped access
- Employer profiles: company name, industry, size, location, logo
- Candidate profiles: headline, comma-separated skills, experience years
- Job listings with category, type, experience level, salary range, remote flag
- Advanced job search: keyword, location, salary range, filters
- View count tracking per listing (atomic via F() expressions)
- Resume upload with file type (.pdf / .docx) and size (5MB) validation
- Application workflow: APPLIED → REVIEWING → INTERVIEW → OFFER / REJECTED
- Private employer notes on applications (never visible to candidates)
- Email notifications: application confirmation, status updates, new application alert for employers
- Employer dashboard with stats: jobs, applications, views, top listings
- Swagger UI at /swagger/ and ReDoc at /redoc/
- Note: On Render free tier, uploaded files do not persist between deploys. Use Cloudinary or AWS S3 for production file storage.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Framework | Django 5, Django REST Framework |
| Auth | JWT with Simple JWT |
| API Docs | drf-yasg Swagger UI and ReDoc |
| Database | SQLite locally, PostgreSQL on Render |
| Deployment | Render, Gunicorn, WhiteNoise |
| File Storage | Local (dev) / Cloudinary or S3 (prod recommended) |

## Project Structure

```bash
accounts/
├── models.py
├── permissions.py
├── serializers.py
├── urls.py
└── views.py
jobs/
├── management/
│   └── commands/
│       └── seed_demo_data.py
├── models.py
├── serializers.py
├── urls.py
├── utils.py
└── views.py
applications/
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
git clone https://github.com/<your-username>/CodeAlpha_JobBoard.git
cd CodeAlpha_JobBoard
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

#### Employers

| Role | Email | Password | Company | Active Jobs |
| --- | --- | --- | --- | --- |
| EMPLOYER | techcorp@example.com | TestPass123! | TechCorp Kenya | 3 |
| EMPLOYER | greenbiz@example.com | TestPass123! | GreenBiz Africa | 3 |
| EMPLOYER | devhive@example.com | TestPass123! | DevHive Ltd | 3 |

#### Candidates

| Role | Email | Password | Headline | Applications |
| --- | --- | --- | --- | --- |
| CANDIDATE | alice@example.com | TestPass123! | Senior Django Developer | 3 |
| CANDIDATE | bob@example.com | TestPass123! | Frontend Engineer | 3 |
| CANDIDATE | carol@example.com | TestPass123! | Data Analyst | 3 |

### Seeded Application States

| Candidate | Job | Status |
| --- | --- | --- |
| Alice | Senior Backend Engineer | OFFER |
| Alice | DevOps Engineer | INTERVIEW |
| Alice | Full Stack Developer | APPLIED |
| Bob | React Frontend Developer | REVIEWING |
| Bob | UI/UX Designer Intern | APPLIED |
| Bob | Junior Python Developer | REJECTED |
| Carol | Data Scientist | INTERVIEW |
| Carol | Financial Analyst | APPLIED |
| Carol | Marketing Specialist | REVIEWING |

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

### Authentication & Profiles

| Method | Endpoint | Role | Description |
| --- | --- | --- | --- |
| POST | /api/auth/employer/register/ | AllowAny | Register employer |
| POST | /api/auth/candidate/register/ | AllowAny | Register candidate |
| POST | /api/auth/token/ | AllowAny | Obtain JWT tokens |
| POST | /api/auth/token/refresh/ | AllowAny | Refresh JWT access token |
| GET | /api/auth/profile/ | Authenticated | Retrieve current profile |
| PATCH | /api/auth/profile/ | Authenticated | Update current profile |

### Jobs

| Method | Endpoint | Role | Description |
| --- | --- | --- | --- |
| GET | /api/jobs/categories/ | AllowAny | List job categories |
| GET | /api/jobs/ | AllowAny | List and search jobs |
| POST | /api/jobs/ | EMPLOYER | Create job listing |
| GET | /api/jobs/<pk>/ | AllowAny | Retrieve job detail and increment views |
| PATCH | /api/jobs/<pk>/manage/ | Job owner | Update job listing |
| DELETE | /api/jobs/<pk>/manage/ | Job owner | Delete job listing |
| GET | /api/employer/dashboard/ | EMPLOYER | Employer dashboard stats |

### Resumes

| Method | Endpoint | Role | Description |
| --- | --- | --- | --- |
| GET | /api/applications/resumes/ | CANDIDATE | List own resumes |
| POST | /api/applications/resumes/ | CANDIDATE | Upload resume |
| DELETE | /api/applications/resumes/<pk>/ | CANDIDATE | Delete own resume |

### Applications

| Method | Endpoint | Role | Description |
| --- | --- | --- | --- |
| GET | /api/applications/ | CANDIDATE | List own applications |
| POST | /api/applications/ | CANDIDATE | Apply for a job |
| GET | /api/applications/employer/ | EMPLOYER | List applications for employer jobs |
| GET | /api/applications/<pk>/ | Authenticated | Retrieve application detail |
| PATCH | /api/applications/<pk>/status/ | EMPLOYER | Update application status |

### Job Search Query Parameters

| Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| search | string | Django | Searches title, description, company |
| category | integer | 1 | Filters by category ID |
| job_type | string | FULL_TIME | Filters by job type |
| experience_level | string | SENIOR | Filters by experience level |
| is_remote | boolean | true | Filters remote jobs |
| is_featured | boolean | true | Filters featured jobs |
| salary_min | number | 100000 | Minimum salary filter |
| salary_max | number | 200000 | Maximum salary filter |
| location | string | Nairobi | Case-insensitive location search |

### Key Business Logic

- File validation: extension must be .pdf or .docx, max 5MB.
- Application guard: candidate cannot apply twice to same job.
- Job guard: cannot apply to CLOSED or expired jobs.
- Status transitions: APPLIED→REVIEWING→INTERVIEW→OFFER or REJECTED.

## Authentication

This API uses JWT. Obtain a token pair via POST /api/auth/token/. Include the access token as a Bearer token in the Authorization header for protected endpoints.

```bash
Authorization: Bearer <access_token>
```

## File Uploads

Resume uploads are limited to 5MB and must use `.pdf` or `.docx` extensions. Render free tier media files do not persist between deploys, so production deployments should use Cloudinary, AWS S3, or another persistent storage backend.

## Email Notifications

| Trigger | Recipient | Description |
| --- | --- | --- |
| Application submitted | Candidate | Confirms application was received |
| Status changed | Candidate | Notifies candidate of workflow update |
| New application received | Employer | Alerts employer to review candidate |

## Running Tests

```bash
python manage.py test applications
```

## Deployment (Render.com)

1. Push the repository to GitHub.
2. Create a Render Web Service from the GitHub repo.
3. Set the build command to `bash build.sh`.
4. Set the start command from `Procfile`.
5. Add a Render PostgreSQL database and copy its `DATABASE_URL`.
6. Set all `.env` variables in Render's environment settings panel.
7. ⚠️ Media files (resumes, logos) do not persist on Render's free tier between deploys. Configure Cloudinary or AWS S3 for production. See django-storages documentation.

## Credits

Built for CodeAlpha Backend Development Internship — May 2026
