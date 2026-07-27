"""Token-based auth + collector API views for the React SPA.

Mirrors the collector flow already implemented for the session-based site in
`users/views.py` (register, watchlist via SavedExhibit, enquiries via
GalleryInquiry), exposed as JWT-authenticated JSON endpoints.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from exhibits.models import Exhibit

from .models import GalleryInquiry, SavedExhibit, UserProfile
from .serializers import (
    CollectionItemSerializer,
    InquirySerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileSerializer,
    RegisterSerializer,
    SavedExhibitSerializer,
    UserSerializer,
)


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class RegisterView(APIView):
    """Create an account and return the user plus a fresh token pair (auto-login)."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'user': UserSerializer(user).data, **_tokens_for_user(user)},
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    """Return the currently authenticated user."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ProfileView(APIView):
    """Read and update account/profile data for the signed-in user."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response(ProfileSerializer(profile).data)

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={'user': request.user},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProfileSerializer(profile).data)


class PasswordResetRequestView(APIView):
    """Send password reset links pointing to the React frontend."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
        users = User.objects.filter(email__iexact=email, is_active=True)

        for user in users:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f'{frontend_url}/reset-password?uid={uid}&token={token}'
            send_mail(
                subject='Reset your ExhibitGuide password',
                message=(
                    'You requested a password reset for your ExhibitGuide account.\n\n'
                    f'Reset link: {reset_url}\n\n'
                    'If you did not request this, you can ignore this message.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

        # Prevent user-enumeration by returning the same response either way.
        return Response(
            {'detail': 'If that email exists, a password reset link has been sent.'},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """Validate reset token and set a new account password."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)


class CollectionView(APIView):
    """The user's engaged exhibits (watchlist + enquiries), each with a status."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        saved_ids = set(
            SavedExhibit.objects.filter(user=request.user).values_list('exhibit_id', flat=True)
        )
        enquired_ids = set(
            GalleryInquiry.objects.filter(user=request.user).values_list('exhibit_id', flat=True)
        )
        engaged_ids = saved_ids | enquired_ids
        exhibits = (
            Exhibit.objects.filter(id__in=engaged_ids)
            .select_related('artwork', 'artwork__artist', 'show')
            .order_by('-publish_date')
        )
        serializer = CollectionItemSerializer(
            exhibits,
            many=True,
            context={'request': request, 'enquired_ids': enquired_ids},
        )
        return Response(serializer.data)


class SavedCreateView(generics.CreateAPIView):
    """Add an exhibit to the user's watchlist (idempotent)."""

    serializer_class = SavedExhibitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved, _created = SavedExhibit.objects.get_or_create(
            user=request.user,
            exhibit=serializer.validated_data['exhibit'],
        )
        return Response(self.get_serializer(saved).data, status=status.HTTP_201_CREATED)


class SavedDeleteView(APIView):
    """Remove an exhibit from the user's watchlist."""

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, exhibit_id):
        deleted, _ = SavedExhibit.objects.filter(
            user=request.user, exhibit_id=exhibit_id
        ).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Not in watchlist.'}, status=status.HTTP_404_NOT_FOUND)


class InquiryCreateView(generics.CreateAPIView):
    """Send a gallery inquiry for an exhibit (marks it 'enquired')."""

    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        exhibit = serializer.validated_data.get('exhibit')
        message = (serializer.validated_data.get('message') or '').strip()
        if not message:
            message = (
                f'I am interested in {exhibit.artwork}. Please contact me.'
                if exhibit
                else 'I am interested in this artwork. Please contact me.'
            )
        serializer.save(user=self.request.user, message=message)
