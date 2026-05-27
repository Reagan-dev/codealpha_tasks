from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Create users with email as the unique identifier."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError("The email address must be set.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with staff and superuser access."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True,
        help_text="The user's email address. Used for login.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

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
        return (
            self.expires_at is not None
            and self.expires_at <= timezone.now()
        )

    def __str__(self):
        return f"{self.short_code} — {self.original_url[:40]}"


