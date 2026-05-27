# Job Board Platform API

This is a Django REST API for a job board platform with employer accounts,
candidate accounts, job listings, resumes, and applications.

## Render Deployment

Use these settings when creating the Render web service:

- Build Command: `bash build.sh`
- Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
- Environment: Python 3
- Database: Render PostgreSQL

Set the environment variables from `.env.example` in the Render dashboard.
At minimum, production needs `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`,
`CSRF_TRUSTED_ORIGINS`, `DATABASE_URL`, `PYTHON_VERSION`, and email settings
if application emails should be sent.

If `build.sh` is committed with executable permissions, `./build.sh` also
works as the Render build command.

## Media Files

Uploaded resumes and images are media files. On Render's free tier, files
written to the local filesystem do not persist between deploys. For production
file storage, use Cloudinary, AWS S3, or another persistent object storage
service.

## Useful Commands

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --no-input
python manage.py test
```

# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================

What each class or function does and why it was written that way

requirements.txt lists the runtime packages Render installs before starting
the app.

Procfile defines the web process that starts Gunicorn with the Django WSGI
application.

build.sh installs dependencies, collects static files, and runs database
migrations during the Render build.

.env.example documents the environment variables needed for local and
production configuration.

config/settings.py contains the production settings additions for Render,
WhiteNoise, HTTPS, allowed hosts, CSRF, CORS, and database configuration.

README.md explains how to deploy the app and warns that Render free tier media
files do not persist between deploys.

Important decisions that were made and why

Gunicorn is used because Render needs a production WSGI server instead of
Django's development server.

WhiteNoise is used so Django can serve collected static files on Render without
needing a separate static file server.

PostgreSQL is expected in production because SQLite files are not appropriate
for deployed multi-user APIs.

Media uploads are documented separately because static files and user-uploaded
media files are different. collectstatic does not preserve uploaded resumes.

PYTHON_VERSION is documented because Django 6 needs a modern Python runtime
and Render allows the runtime to be pinned through an environment variable.

What you should read and understand before you review the code

Read Render's Django deployment guide.

Read Django deployment settings for DEBUG, ALLOWED_HOSTS, CSRF, HTTPS, static
files, and media files.

Read WhiteNoise static file serving for Django.

Read Gunicorn WSGI deployment basics.

# ============================================================
# END OF REVIEW
# ============================================================
