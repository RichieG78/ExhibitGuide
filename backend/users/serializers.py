"""Serializers for the token-based auth + collector API (React SPA)."""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from exhibits.serializers import ExhibitSerializer

from .models import GalleryInquiry, SavedExhibit


class UserSerializer(serializers.ModelSerializer):
    """Public shape of the authenticated user."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    """Creates a new account (username + email + validated password)."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CollectionItemSerializer(ExhibitSerializer):
    """An exhibit in the user's collection, tagged with its per-user status.

    `status` is 'enquired' when the user has sent a GalleryInquiry for the work,
    otherwise 'watching'. The enquired ids are provided via serializer context.
    """

    status = serializers.SerializerMethodField()

    class Meta(ExhibitSerializer.Meta):
        fields = ExhibitSerializer.Meta.fields + ['status']

    def get_status(self, obj):
        enquired_ids = self.context.get('enquired_ids', set())
        return 'enquired' if obj.id in enquired_ids else 'watching'


class SavedExhibitSerializer(serializers.ModelSerializer):
    """Write serializer for adding an exhibit to the watchlist."""

    class Meta:
        model = SavedExhibit
        fields = ['id', 'exhibit', 'saved_at']
        read_only_fields = ['id', 'saved_at']


class InquirySerializer(serializers.ModelSerializer):
    """Write serializer for sending a gallery inquiry about an exhibit."""

    message = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = GalleryInquiry
        fields = ['id', 'exhibit', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']
