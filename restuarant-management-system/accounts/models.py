from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for restaurant customers and team members."""

    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        STAFF = "STAFF", "Staff"
        MANAGER = "MANAGER", "Manager"

    email = models.EmailField(
        unique=True,
        help_text="Unique email address used to sign in.",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        help_text="Access role for this user inside the restaurant system.",
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Optional contact phone number for this user.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["email"]

    def __str__(self):
        return self.email


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# User extends Django's AbstractUser so the project keeps Django's built-in
# password, permissions, username, first_name, last_name, and staff fields.
# This is the safest way to customize users without rebuilding authentication
# from scratch.
#
# Role is a TextChoices class. It keeps the allowed role values in one place
# and makes migrations, forms, serializers, and admin screens easier to read.
#
# email is unique because USERNAME_FIELD is set to "email". Django needs the
# login field to identify one user clearly.
#
# role defaults to CUSTOMER because most users in a restaurant system are
# customers unless a manager or admin assigns a staff role.
#
# phone_number allows null and blank because not every user will provide a
# phone number.
#
# USERNAME_FIELD tells Django to authenticate users by email. REQUIRED_FIELDS
# keeps username required when creating a superuser from the command line,
# because AbstractUser still includes the username field.
#
# __str__ returns the email address because it is unique and easy to recognize
# in the Django admin, logs, and shell.
#
# Important decisions that were made and why
#
# The model keeps AbstractUser's username field instead of removing it. This
# keeps the change small and compatible with Django's default user behavior.
#
# The role values are uppercase because they are stable database values. The
# human-readable labels use normal title case for forms and admin screens.
#
# What you should read and understand before you review the code
#
# Read Django's custom user model documentation, especially AbstractUser,
# USERNAME_FIELD, REQUIRED_FIELDS, and AUTH_USER_MODEL.
#
# Read Django TextChoices so you understand how role choices are stored and
# displayed.
#
# ============================================================
# END OF REVIEW
# ============================================================
