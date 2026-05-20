from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        MEMBER = "MEMBER", "Member"
        ORGANIZER = "ORGANIZER", "Organizer"

    email = models.EmailField(
        unique=True,
        help_text="Required. Used for login and account communication.",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
        help_text="Controls whether the user is a member or an organizer.",
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Optional contact phone number for the user.",
    )
    bio = models.TextField(
        null=True,
        blank=True,
        help_text="Optional short profile description for the user.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["email"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# User is the custom account model for the project. It extends AbstractUser so
# Django still provides username, password, first_name, last_name, permissions,
# groups, is_active, is_staff, and is_superuser.
#
# Role is a TextChoices class. It stores a fixed list of valid role values:
# MEMBER and ORGANIZER. This prevents random role text from being saved.
#
# email is unique because the project uses email as the login field. No two
# users should be able to sign in with the same email address.
#
# role stores whether a user is a normal member or an organizer. MEMBER is the
# default because most new accounts are expected to register for events, not
# create them.
#
# phone_number and bio are optional profile fields. They use null=True and
# blank=True so they can be empty in both the database and Django forms.
#
# USERNAME_FIELD = "email" tells Django authentication to use email for login.
# REQUIRED_FIELDS = ["username"] means createsuperuser will still ask for a
# username in addition to email and password.
#
# Meta.ordering sorts users by email by default. verbose_name and
# verbose_name_plural make the admin display names clean.
#
# __str__ returns the email so users are easy to identify in the Django admin,
# shell, logs, and related object displays.
#
# Important decisions that were made and why
#
# AbstractUser was used instead of AbstractBaseUser because it gives a complete
# working user model with less custom authentication code.
#
# The email field was explicitly redefined as unique because AbstractUser's
# default email field is not unique.
#
# The role values are uppercase constants because they are stable database
# values and easy to compare in permissions code.
#
# What you should read and understand before you review the code
#
# Read Django custom user model documentation before running migrations.
# Custom user models should be created before the first migration.
#
# Read Django model field options: unique, null, blank, default, choices, and
# help_text.
#
# Read Django TextChoices so you understand why Role.choices is used.
#
# ============================================================
# END OF REVIEW
# ============================================================
