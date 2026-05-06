import random
import string
from io import BytesIO

import qrcode
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import ShortURL


def generate_short_code(length=6):
    """Return a unique random short code."""
    characters = string.ascii_letters + string.digits

    while True:
        short_code = "".join(random.choices(characters, k=length))

        if not ShortURL.objects.filter(short_code=short_code).exists():
            return short_code


def generate_qr_code(url):
    """Generate a QR code PNG image and return it in a BytesIO buffer."""
    buffer = BytesIO()
    image = qrcode.make(url)
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


def is_valid_url(url):
    """Return True when the given value is a valid URL."""
    validator = URLValidator()

    try:
        validator(url)
    except ValidationError:
        return False

    return True


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# This file contains small helper functions used by the URL shortener app.
# Utility functions live here so views and serializers can stay focused on
# request handling and validation.
#
# generate_short_code creates a random short code. It uses letters and
# numbers because those characters are URL-friendly and easy to share. The
# default length is 6 because that keeps links short while still giving many
# possible combinations.
#
# Inside generate_short_code, random.choices picks characters from
# string.ascii_letters and string.digits. The function then checks the
# ShortURL table to make sure the generated code is not already used.
#
# The while loop keeps generating a new code until it finds one that does
# not exist in the database. This is important because short codes must be
# unique. If two links had the same short code, the app would not know which
# original URL to redirect to.
#
# generate_qr_code creates a QR code image for a URL. It uses the qrcode
# library because QR code generation is a solved problem and should not be
# written manually.
#
# generate_qr_code saves the QR image into a BytesIO buffer instead of a
# file on disk. This is useful for an API because the view can return the
# buffer directly as an HTTP response.
#
# buffer.seek(0) moves the read position back to the start of the image.
# Without this, the response could try to read from the end of the buffer
# and return an empty file.
#
# is_valid_url checks whether a string is a valid URL. It uses Django's
# URLValidator so the app follows Django's normal URL validation rules.
#
# is_valid_url catches ValidationError and returns False instead of raising
# an exception. This makes it simple for other code to use the function in
# if statements.
#
# Important decisions made:
# - Short codes use uppercase letters, lowercase letters, and digits to keep
#   them compact and URL-safe.
# - The database is checked before returning a short code to avoid duplicate
#   redirect codes.
# - QR codes are generated in memory because API responses do not need to
#   create temporary image files on disk.
# - Django's URLValidator is reused so URL validation stays consistent with
#   the rest of the Django project.
#
# Before reviewing this code, read and understand:
# - How random.choices works.
# - Why unique short codes are required for redirects.
# - What BytesIO is and how in-memory files work.
# - How QR code images can be returned from an HTTP response.
# - How Django's URLValidator raises ValidationError for invalid URLs.
#
# ============================================================
# END OF REVIEW
# ============================================================
