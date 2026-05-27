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


