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
        path = f"/s/{code_or_alias}/"

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



