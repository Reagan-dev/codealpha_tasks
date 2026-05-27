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


