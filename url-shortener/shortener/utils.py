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


