from datetime import timedelta

from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ShortURL
from .serializers import (
    CreateShortURLSerializer,
    ShortURLSerializer,
    ShortURLStatsSerializer,
)
from .utils import generate_qr_code, generate_short_code


class ShortenURLView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CreateShortURLSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        custom_alias = serializer.validated_data.get("custom_alias")
        expires_in_days = serializer.validated_data.get("expires_in_days")
        short_code = custom_alias or generate_short_code()
        expires_at = None
        created_by = None

        if expires_in_days is not None:
            expires_at = timezone.now() + timedelta(days=expires_in_days)

        if request.user.is_authenticated:
            created_by = request.user

        short_url = serializer.save(
            short_code=short_code,
            expires_at=expires_at,
            created_by=created_by,
        )
        response_serializer = ShortURLSerializer(
            short_url,
            context=self.get_serializer_context(),
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class RedirectView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, short_code):
        short_url = get_object_or_404(ShortURL, short_code=short_code)

        if short_url.is_expired:
            return Response(
                {"detail": "This short URL has expired."},
                status=status.HTTP_410_GONE,
            )

        ShortURL.objects.filter(pk=short_url.pk).update(
            click_count=F("click_count") + 1,
        )

        return HttpResponseRedirect(short_url.original_url)


class URLListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ShortURLStatsSerializer

    def get_queryset(self):
        return ShortURL.objects.filter(
            created_by=self.request.user,
        ).select_related("created_by")


class URLDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ShortURLStatsSerializer
    lookup_field = "short_code"
    lookup_url_kwarg = "short_code"

    def get_queryset(self):
        return ShortURL.objects.select_related("created_by")

    def destroy(self, request, *args, **kwargs):
        short_url = self.get_object()

        if short_url.created_by_id != request.user.id:
            return Response(
                {"detail": "You do not have permission to delete this link."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().destroy(request, *args, **kwargs)


class QRCodeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, short_code):
        short_url = get_object_or_404(ShortURL, short_code=short_code)
        public_url = request.build_absolute_uri(f"/s/{short_url.short_code}/")
        qr_buffer = generate_qr_code(public_url)

        return HttpResponse(
            qr_buffer.getvalue(),
            content_type="image/png",
        )


