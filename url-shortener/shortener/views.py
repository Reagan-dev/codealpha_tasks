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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# This file defines the API views for the URL shortener app. Views receive
# HTTP requests, call serializers and models, and return HTTP responses.
#
# ShortenURLView handles POST /api/shorten/. It extends CreateAPIView
# because it creates a new ShortURL object from request data.
#
# ShortenURLView uses AllowAny so both anonymous users and logged-in users
# can create short links.
#
# ShortenURLView.create validates the request with CreateShortURLSerializer.
# If custom_alias is provided, that alias becomes the short_code. If no
# custom alias is provided, generate_short_code() creates a unique random
# code.
#
# ShortenURLView.create also converts expires_in_days into an expires_at
# datetime. If the request user is authenticated, the new ShortURL is linked
# to that user through created_by. The response uses ShortURLSerializer so
# the client receives the saved link data.
#
# RedirectView handles GET /s/<short_code>/. It extends APIView because it
# performs custom redirect logic instead of normal JSON-only behavior.
#
# RedirectView looks up the ShortURL by short_code. If no row exists,
# get_object_or_404 returns a 404 response. If the link is expired, the view
# returns HTTP 410 Gone because the link used to exist but is no longer
# available.
#
# RedirectView increments click_count with an F() expression. This is
# atomic at the database level, so two visitors at the same time do not
# accidentally overwrite each other's click count.
#
# RedirectView returns HttpResponseRedirect to send the browser to the
# original URL.
#
# URLListView handles GET /api/links/. It extends ListAPIView because it
# returns a list of objects. It uses IsAuthenticated so only logged-in users
# can see their saved links.
#
# URLListView.get_queryset returns only links created by request.user. This
# protects each user's link list from other users.
#
# URLDetailView handles GET and DELETE for /api/links/<short_code>/. It
# extends RetrieveDestroyAPIView because it can retrieve one object or
# delete one object.
#
# URLDetailView uses short_code as the lookup field because API users know
# the short code, not the database id.
#
# URLDetailView.destroy checks ownership before deleting. If the logged-in
# user did not create the link, the view returns HTTP 403 Forbidden.
#
# QRCodeView handles GET /api/links/<short_code>/qr/. It allows anyone to
# request a QR code for a short link.
#
# QRCodeView builds the public short URL, passes it to generate_qr_code(),
# and returns the PNG bytes in an HttpResponse with content_type image/png.
#
# Important decisions made:
# - Code generation happens in the view because the serializer should only
#   validate and save data, not decide public routing behavior.
# - custom_alias becomes short_code so redirects can always look up one
#   field: short_code.
# - F() is used for click_count updates to keep increments safe under
#   concurrent requests.
# - Authenticated list responses are limited to request.user's links.
# - Delete permission is checked manually so users cannot delete links they
#   do not own.
# - QR code images are returned directly from memory instead of being saved
#   to disk.
#
# Before reviewing this code, read and understand:
# - DRF class-based views such as CreateAPIView, ListAPIView, and
#   RetrieveDestroyAPIView.
# - How permission_classes control anonymous and authenticated access.
# - How serializers validate input and format output.
# - How get_object_or_404 works.
# - Why F() expressions are useful for atomic database updates.
# - The difference between 404 Not Found, 403 Forbidden, and 410 Gone.
# - How HttpResponseRedirect and image/png HttpResponse objects work.
#
# ============================================================
# END OF REVIEW
# ============================================================
