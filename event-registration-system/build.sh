#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# This file does not define classes or functions. It defines the shell commands
# Render should run when building the service.
#
# pip install -r requirements.txt installs Django, DRF, database, email,
# Swagger, static-file, and production server dependencies.
#
# python manage.py collectstatic --no-input gathers static files into
# STATIC_ROOT so WhiteNoise can serve them in production.
#
# python manage.py migrate applies database migrations so the production
# database has the latest tables and columns.
#
# Important decisions that were made and why
#
# set -o errexit stops the build if any command fails. This prevents Render from
# deploying a broken build after a failed install, collectstatic, or migration.
#
# gunicorn is started from the Procfile, not this build script, because Render
# separates build commands from the web process command.
#
# What you should read and understand before you review the code
#
# Read Render's Django deployment guide.
#
# Read Django collectstatic and migrations.
#
# Read WhiteNoise static file serving.
#
# Read Procfile web process syntax.
#
# ============================================================
# END OF REVIEW
# ============================================================
