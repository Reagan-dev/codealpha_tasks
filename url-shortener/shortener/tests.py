from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ShortURL
from .utils import generate_short_code


User = get_user_model()


class ShortURLModelTest(TestCase):
    def test_short_url_creation(self):
        """Create a ShortURL and confirm its saved field values."""
        user = User.objects.create_user(
            email="model@example.com",
            password="testpass123",
        )
        expires_at = timezone.now() + timedelta(days=7)
        short_url = ShortURL.objects.create(
            original_url="https://example.com/articles/django",
            short_code="abc123",
            custom_alias="django-link",
            click_count=3,
            expires_at=expires_at,
            created_by=user,
        )

        self.assertEqual(
            short_url.original_url,
            "https://example.com/articles/django",
        )
        self.assertEqual(short_url.short_code, "abc123")
        self.assertEqual(short_url.custom_alias, "django-link")
        self.assertEqual(short_url.click_count, 3)
        self.assertEqual(short_url.expires_at, expires_at)
        self.assertEqual(short_url.created_by, user)
        self.assertIsNotNone(short_url.created_at)
        self.assertIsNotNone(short_url.updated_at)

    def test_is_expired_false(self):
        """Return False when the ShortURL expires in the future."""
        short_url = ShortURL.objects.create(
            original_url="https://example.com/future",
            short_code="future",
            expires_at=timezone.now() + timedelta(days=1),
        )

        self.assertFalse(short_url.is_expired)

    def test_is_expired_true(self):
        """Return True when the ShortURL expiration date is in the past."""
        short_url = ShortURL.objects.create(
            original_url="https://example.com/past",
            short_code="past",
            expires_at=timezone.now() - timedelta(days=1),
        )

        self.assertTrue(short_url.is_expired)


class GenerateShortCodeTest(TestCase):
    def test_generates_unique_code(self):
        """Generate 100 short codes and confirm there are no duplicates."""
        codes = {generate_short_code() for _ in range(100)}

        self.assertEqual(len(codes), 100)

    def test_code_length(self):
        """Generate a short code and confirm it is 6 characters long."""
        short_code = generate_short_code()

        self.assertEqual(len(short_code), 6)


class ShortenURLViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="shorten@example.com",
            password="testpass123",
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_shorten_valid_url(self):
        """Create a short URL from a valid original URL."""
        response = self.client.post(
            "/api/shorten/",
            {"original_url": "https://example.com/valid"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("short_code", response.data)

    def test_shorten_invalid_url(self):
        """Reject a request when original_url is not a valid URL."""
        response = self.client.post(
            "/api/shorten/",
            {"original_url": "not-a-valid-url"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_shorten_duplicate_alias(self):
        """Reject the second request when custom_alias is already used."""
        payload = {
            "original_url": "https://example.com/duplicate",
            "custom_alias": "duplicate-alias",
        }
        first_response = self.client.post(
            "/api/shorten/",
            payload,
            format="json",
        )
        second_response = self.client.post(
            "/api/shorten/",
            payload,
            format="json",
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_shorten_with_custom_alias(self):
        """Use custom_alias as the public short_code when it is provided."""
        response = self.client.post(
            "/api/shorten/",
            {
                "original_url": "https://example.com/custom",
                "custom_alias": "my-custom-link",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["short_code"], "my-custom-link")


class RedirectViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.short_url = ShortURL.objects.create(
            original_url="https://example.com/redirect",
            short_code="redir1",
        )
        cls.expired_url = ShortURL.objects.create(
            original_url="https://example.com/expired",
            short_code="expired",
            expires_at=timezone.now() - timedelta(days=1),
        )

    def test_redirect_valid_code(self):
        """Redirect to original_url when short_code exists and is active."""
        response = self.client.get("/s/redir1/")

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], self.short_url.original_url)

    def test_redirect_increments_click(self):
        """Increment click_count each time a short URL is visited."""
        self.client.get("/s/redir1/")
        self.client.get("/s/redir1/")
        self.short_url.refresh_from_db()

        self.assertEqual(self.short_url.click_count, 2)

    def test_redirect_expired_link(self):
        """Return 410 Gone when the short URL has expired."""
        response = self.client.get("/s/expired/")

        self.assertEqual(response.status_code, status.HTTP_410_GONE)

    def test_redirect_not_found(self):
        """Return 404 when no ShortURL matches the requested code."""
        response = self.client.get("/s/missing/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class URLListViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_a = User.objects.create_user(
            email="usera@example.com",
            password="testpass123",
        )
        cls.user_b = User.objects.create_user(
            email="userb@example.com",
            password="testpass123",
        )
        ShortURL.objects.create(
            original_url="https://example.com/a-one",
            short_code="aone",
            created_by=cls.user_a,
        )
        ShortURL.objects.create(
            original_url="https://example.com/a-two",
            short_code="atwo",
            created_by=cls.user_a,
        )
        ShortURL.objects.create(
            original_url="https://example.com/b-one",
            short_code="bone",
            created_by=cls.user_b,
        )

    def test_list_requires_auth(self):
        """Return 401 when an anonymous user requests the link list."""
        response = self.client.get("/api/links/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_returns_only_own_links(self):
        """Return only the authenticated user's ShortURL records."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/api/links/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)


