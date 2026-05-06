import re
from datetime import timedelta

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from .models import ShortURL


class CreateShortURLSerializer(serializers.ModelSerializer):
    expires_in_days = serializers.IntegerField(
        required=False,
        write_only=True,
        min_value=1,
        help_text="Optional number of days before the short URL expires.",
    )

    class Meta:
        model = ShortURL
        fields = (
            "original_url",
            "custom_alias",
            "expires_in_days",
        )
        extra_kwargs = {
            "original_url": {
                "required": True,
                "help_text": "The full URL that should be shortened.",
            },
            "custom_alias": {
                "required": False,
                "allow_null": True,
                "allow_blank": False,
                "help_text": (
                    "Optional custom alias using letters, numbers, "
                    "and hyphens."
                ),
            },
        }

    def validate_original_url(self, value):
        validator = URLValidator()

        try:
            validator(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                "Enter a valid URL."
            ) from exc

        return value

    def validate_custom_alias(self, value):
        if value is None:
            return value

        if not re.fullmatch(r"[A-Za-z0-9-]+", value):
            raise serializers.ValidationError(
                "Custom alias may contain only letters, numbers, and hyphens."
            )

        if ShortURL.objects.filter(custom_alias=value).exists():
            raise serializers.ValidationError(
                "This custom alias is already in use."
            )

        return value

    def create(self, validated_data):
        expires_in_days = validated_data.pop("expires_in_days", None)

        if expires_in_days is not None:
            validated_data["expires_at"] = (
                timezone.now() + timedelta(days=expires_in_days)
            )

        return ShortURL.objects.create(**validated_data)


class ShortURLSerializer(serializers.ModelSerializer):
    is_expired = serializers.SerializerMethodField()
    short_url = serializers.SerializerMethodField()

    class Meta:
        model = ShortURL
        fields = (
            "id",
            "original_url",
            "short_code",
            "custom_alias",
            "short_url",
            "click_count",
            "expires_at",
            "created_at",
            "is_expired",
        )
        read_only_fields = fields

    def get_is_expired(self, obj):
        return obj.is_expired

    def get_short_url(self, obj):
        request = self.context.get("request")
        code_or_alias = obj.custom_alias or obj.short_code
        path = f"/{code_or_alias}/"

        if request is None:
            return path

        return request.build_absolute_uri(path)


class ShortURLStatsSerializer(ShortURLSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)

    class Meta(ShortURLSerializer.Meta):
        fields = ShortURLSerializer.Meta.fields + ("created_by",)
        read_only_fields = fields

    def get_created_by(self, obj):
        if obj.created_by is None:
            return None

        return obj.created_by.get_username()


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# This file defines serializers for the shortener app. Serializers convert
# model objects into JSON and validate incoming JSON before it is saved.
#
# CreateShortURLSerializer is used for the POST /api/shorten/ endpoint. It
# accepts only the fields needed when a user creates a short URL:
# original_url, custom_alias, and expires_in_days.
#
# expires_in_days is write-only because clients can send it when creating a
# short link, but the API response should show the real expires_at datetime
# instead. It has min_value=1 so users cannot create an expiration in zero
# or negative days.
#
# CreateShortURLSerializer.Meta connects the serializer to the ShortURL
# model and lists the input fields. The extra_kwargs section marks
# original_url as required and custom_alias as optional.
#
# validate_original_url checks that original_url has a real URL format. A
# URLField already does this, but the explicit validator keeps the rule
# clear and gives a simple error message.
#
# validate_custom_alias checks three things. It allows None because the
# alias is optional. It rejects spaces and special characters by allowing
# only letters, numbers, and hyphens. It also checks the database so the
# same alias cannot be used twice.
#
# create converts expires_in_days into expires_at. It does not generate
# short_code because the view is responsible for that. The view should call
# serializer.save(short_code=generated_code, created_by=request.user) or
# similar when saving.
#
# ShortURLSerializer is the read serializer. It returns saved ShortURL data
# to API clients.
#
# is_expired is a SerializerMethodField. It reads the model's is_expired
# property so the expiration logic stays in one place on the model.
#
# short_url is a SerializerMethodField. It uses the request from serializer
# context to build the full short URL. If no request is available, it
# returns only the path.
#
# get_is_expired returns the model property value. This keeps the serializer
# simple and avoids duplicating date comparison logic.
#
# get_short_url chooses custom_alias first and short_code second. This means
# the public short URL uses the custom alias when one exists.
#
# ShortURLStatsSerializer extends ShortURLSerializer. It keeps all normal
# read fields and adds created_by for statistics or admin-style responses.
#
# created_by is a SerializerMethodField because the project uses a custom
# email-based user model. Calling get_username() returns the configured user
# identifier, which is email in this project.
#
# Important decisions made:
# - short_code is not generated in the serializer because code generation
#   belongs in the view or service layer where collisions can be handled.
# - expires_in_days is accepted as input, but expires_at is returned as the
#   stored database value.
# - custom_alias is validated before saving so users get a clear API error
#   instead of a database integrity error.
# - short_url is built from request context so it can include the correct
#   domain during local development or deployment.
# - ShortURLStatsSerializer inherits from ShortURLSerializer to avoid
#   repeating the same read fields.
#
# Before reviewing this code, read and understand:
# - The difference between serializers.Serializer and ModelSerializer.
# - How field-level validation methods like validate_custom_alias work.
# - How SerializerMethodField works.
# - How serializer context passes the request into a serializer.
# - Why write-only fields are useful for create-only input.
# - Why database uniqueness should still be backed by model constraints.
#
# ============================================================
# END OF REVIEW
# ============================================================
