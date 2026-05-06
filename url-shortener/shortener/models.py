from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True,
        help_text="The user's email address. Used for login.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class ShortURL(models.Model):
    original_url = models.URLField(
        max_length=2000,
        help_text="The full original URL that will be shortened.",
    )
    short_code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text="The generated short code used in the shortened URL.",
    )
    custom_alias = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="An optional custom alias chosen by the user.",
    )
    click_count = models.PositiveIntegerField(
        default=0,
        help_text="The number of times this short URL has been visited.",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date and time when this short URL should expire.",
    )
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="short_urls",
        help_text="The user who created this short URL.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when this short URL was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="The date and time when this short URL was last updated.",
    )

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_expired(self):
        return self.expires_at is not None and self.expires_at <= timezone.now()

    def __str__(self):
        return f"{self.short_code} — {self.original_url[:40]}"


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# This file defines the database models for the shortener app. A model is a
# Python class that Django turns into a database table.
#
# User extends Django's AbstractUser. AbstractUser already contains the
# normal user fields, password handling, permissions, groups, and admin
# support. This custom User removes username and makes email the login
# identifier. It was written this way because modern APIs usually ask users
# to log in with an email address instead of a username.
#
# The email field is unique so two accounts cannot use the same email
# address. USERNAME_FIELD tells Django to authenticate users by email.
# REQUIRED_FIELDS is empty because email and password are enough when
# creating a user from the command line.
#
# User.__str__ returns the user's email. This makes users easier to read in
# the Django admin, shell, logs, and debugging output.
#
# ShortURL stores one shortened link. Each ShortURL row represents one
# original URL and the code or alias that points to it.
#
# original_url stores the full URL that the user wants to shorten. It uses
# URLField so Django validates that the value looks like a URL. max_length
# is 2000 because real URLs can be long.
#
# short_code stores the generated short code. It is unique so no two links
# share the same code. It has db_index=True because redirects will often
# search by this field, and an index makes that lookup faster.
#
# custom_alias stores an optional user-chosen alias. It is unique because
# two short URLs cannot safely use the same alias. null=True allows the
# database to store no value, and blank=True allows forms and serializers to
# accept an empty value.
#
# click_count stores how many times the short URL has been visited. It uses
# PositiveIntegerField because a click count should never be negative.
#
# expires_at stores an optional expiration date and time. If it is empty,
# the short URL does not expire.
#
# created_by connects a short URL to the user who created it. It allows
# null and blank so anonymous users can still create links if the API later
# allows that. SET_NULL keeps the short URL if the user account is deleted.
#
# created_at is filled once when the row is created. updated_at changes
# every time the row is saved. These fields are useful for sorting,
# auditing, and debugging.
#
# ShortURL.Meta sets ordering to newest first. This is useful because API
# list responses usually show the most recent links first.
#
# is_expired is a property method. It returns True only when expires_at has
# a value and that value is in the past. It uses timezone.now() so the
# comparison works correctly with Django's timezone-aware datetime settings.
#
# ShortURL.__str__ returns the short code and the first 40 characters of the
# original URL. This keeps admin and shell output readable without showing a
# very long URL every time.
#
# Important decisions made:
# - The custom User model is created now, before migrations, because
#   changing the user model later is difficult in Django.
# - Email is used as the identifier because it is familiar for API users.
# - short_code and custom_alias are unique to prevent routing conflicts.
# - short_code is indexed because it will be used for fast redirect lookups.
# - created_by uses SET_NULL so link data is not deleted when a user is
#   deleted.
# - is_expired is a property because it is calculated from expires_at and
#   should not be stored separately in the database.
#
# Before reviewing this code, read and understand:
# - Django models and how they become database tables.
# - The difference between AbstractUser and Django's default User model.
# - Why AUTH_USER_MODEL must be set before running migrations.
# - How unique fields and database indexes work.
# - The difference between null=True and blank=True.
# - How ForeignKey relationships work.
# - How timezone-aware datetimes work in Django.
#
# ============================================================
# END OF REVIEW
# ============================================================
