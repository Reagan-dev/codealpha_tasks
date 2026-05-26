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
# build.sh is the build command Render should run before starting the web
# service.
#
# set -o errexit stops the deploy immediately if any command fails.
#
# pip install -r requirements.txt installs the Python dependencies.
#
# python manage.py collectstatic --no-input gathers static files into
# STATIC_ROOT so WhiteNoise can serve them.
#
# python manage.py migrate applies database migrations to the production
# PostgreSQL database.
#
# Important decisions that were made and why
#
# Migrations run during the build so the database schema is updated before the
# new code starts serving requests.
#
# The script is short and explicit because Render logs each command, making
# failed deploys easier to debug.
#
# What you should read and understand before you review the code
#
# Read Render build commands.
#
# Read Django collectstatic and migrate.
#
# Read why build scripts should fail fast in production deploys.
#
# ============================================================
# END OF REVIEW
# ============================================================
