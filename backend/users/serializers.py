"""Serializers for the token-based auth + collector API (React SPA)."""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers

from exhibits.serializers import ExhibitSerializer

from .models import GalleryInquiry, SavedExhibit, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Public shape of the authenticated user."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']


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

    Status mapping:
    - 'prospect': the user sent a high-intent purchase enquiry.
    - 'lead': the user expressed interest and opened callback.
    - 'watching': saved-only (no inquiry yet).
    """

    status = serializers.SerializerMethodField()

    class Meta(ExhibitSerializer.Meta):
        fields = ExhibitSerializer.Meta.fields + ['status']

    def get_status(self, obj):
        prospect_ids = self.context.get('prospect_ids', set())
        enquired_ids = self.context.get('enquired_ids', set())
        if obj.id in prospect_ids:
            return 'prospect'
        if obj.id in enquired_ids:
            return 'lead'
        return 'watching'


class SavedExhibitSerializer(serializers.ModelSerializer):
    """Write serializer for adding an exhibit to the watchlist."""

    class Meta:
        model = SavedExhibit
        fields = ['id', 'exhibit', 'saved_at']
        read_only_fields = ['id', 'saved_at']


class InquirySerializer(serializers.ModelSerializer):
    """Write serializer for sending a gallery inquiry about an exhibit."""

    message = serializers.CharField(required=False, allow_blank=True, default='')
    purchase_intent = serializers.BooleanField(required=False, default=False, write_only=True)

    class Meta:
        model = GalleryInquiry
        fields = ['id', 'exhibit', 'message', 'purchase_intent', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProfileSerializer(serializers.Serializer):
    """Read/write shape for profile management in the React app."""

    username = serializers.CharField(required=False, max_length=150)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=30)
    preferred_contact_method = serializers.ChoiceField(
        required=False,
        allow_blank=True,
        choices=UserProfile.PreferredContactMethod.choices,
    )
    bio = serializers.CharField(required=False, allow_blank=True)

    def to_representation(self, profile):
        user = profile.user
        return {
            'username': user.username,
            'email': user.email,
            'first_name': profile.firstname or user.first_name,
            'last_name': profile.lastname or user.last_name,
            'phone': profile.phone,
            'preferred_contact_method': profile.preferred_contact_method,
            'bio': profile.bio,
            'image_url': profile.image.url if profile.image else None,
        }

    def validate(self, attrs):
        method = attrs.get('preferred_contact_method')
        if method in {'phone', 'text'}:
            phone = attrs.get('phone')
            current_phone = self.instance.phone if self.instance else ''
            candidate_phone = (phone if phone is not None else current_phone).strip()
            if not candidate_phone:
                raise serializers.ValidationError({'phone': 'Phone is required when preferred contact method is phone or text.'})
        return attrs

    def validate_username(self, value):
        user = self.context.get('user')
        if not user:
            return value
        conflict = User.objects.filter(username=value).exclude(id=user.id).exists()
        if conflict:
            raise serializers.ValidationError('This username is already taken.')
        return value

    def update(self, profile, validated_data):
        user = profile.user

        if 'username' in validated_data:
            user.username = validated_data['username']
        if 'email' in validated_data:
            user.email = validated_data['email']

        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        if first_name is not None:
            user.first_name = first_name
            profile.firstname = first_name
        if last_name is not None:
            user.last_name = last_name
            profile.lastname = last_name
        if 'phone' in validated_data:
            profile.phone = validated_data['phone']
        if 'preferred_contact_method' in validated_data:
            profile.preferred_contact_method = validated_data['preferred_contact_method']
        if 'bio' in validated_data:
            profile.bio = validated_data['bio']

        user.save(update_fields=['username', 'email', 'first_name', 'last_name'])
        profile.save(update_fields=['firstname', 'lastname', 'phone', 'preferred_contact_method', 'bio'])
        return profile


class PasswordResetRequestSerializer(serializers.Serializer):
    """Accept an email address for password reset initiation."""

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Validate a reset token and set a new password."""

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        uid = attrs.get('uid')
        token = attrs.get('token')

        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
        except Exception as exc:
            raise serializers.ValidationError({'uid': 'Invalid reset link.'}) from exc

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({'token': 'Invalid or expired reset token.'})

        validate_password(attrs['new_password'], user)
        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user
