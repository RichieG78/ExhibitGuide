"""Serializers translate model instances to/from JSON for the REST API.

An `Exhibit` row in the database becomes a JSON object the React frontend can
read, and incoming JSON can be validated back into an `Exhibit`. This is the
"translator at the kitchen window" between Django (backend) and React (frontend).
"""

from rest_framework import serializers

from users.models import Prospect

from .models import Artist, Artwork, Exhibit, Show


class ArtistSerializer(serializers.ModelSerializer):
    """JSON representation of an artist.

    Adds a convenience `full_name` (from the model's __str__) so the frontend
    can display the artist's name without combining first/last itself.
    """

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = [
            'artist_id',
            'firstname',
            'lastname',
            'full_name',
            'nationality',
        ]

    def get_full_name(self, obj):
        return str(obj)


class ExhibitSerializer(serializers.ModelSerializer):
    """JSON representation of a public exhibit record.

    Alongside the concrete model fields, this exposes several read-only values
    that the `Exhibit` model derives from its linked `Artwork` and `Show`
    (artist name, medium, dimensions, provenance, show name). Exposing them here
    means the frontend gets ready-to-display data without extra API calls.
    """

    # The artwork's title, exposed for the detail page heading.
    title = serializers.SerializerMethodField()
    # Derived, read-only values that come from the Exhibit model's @property
    # methods (they read through to the related Artwork / Show).
    artist = serializers.ReadOnlyField()
    medium = serializers.ReadOnlyField()
    dimensions_height = serializers.ReadOnlyField()
    dimensions_width = serializers.ReadOnlyField()
    provenance = serializers.ReadOnlyField()
    show_name = serializers.ReadOnlyField()

    class Meta:
        model = Exhibit
        fields = [
            'id',
            'gallery_name',
            'show',
            'show_name',
            'artwork',
            'title',
            'artist',
            'medium',
            'dimensions_height',
            'dimensions_width',
            'provenance',
            'price',
            'currency',
            'tldr',
            'full_text',
            'audio_url',
            'video_url',
            'image',
            'image_url',
            'qr_identifier',
            'publish_date',
            'user',
        ]
        # Generated automatically on save, so never accept it from the client.
        read_only_fields = ['qr_identifier']

    def get_title(self, obj):
        return obj.artwork.title if obj.artwork_id else ''


class ArtworkSerializer(serializers.ModelSerializer):
    """JSON representation of a reusable artwork.

    Includes the linked artist as both an id (`artist`) and a readable
    `artist_name`, so the frontend can display the name without a second call.
    """

    artist_name = serializers.SerializerMethodField()

    class Meta:
        model = Artwork
        fields = [
            'artwork_id',
            'title',
            'artist',
            'artist_name',
            'medium',
            'dimensions_height',
            'dimensions_width',
            'provenance',
        ]

    def get_artist_name(self, obj):
        return str(obj.artist) if obj.artist_id else ''


class ShowSerializer(serializers.ModelSerializer):
    """JSON representation of an exhibition/show."""

    class Meta:
        model = Show
        fields = [
            'show_id',
            'show_name',
            'start_date',
            'end_date',
        ]


class ProspectSerializer(serializers.ModelSerializer):
    """Captures an anonymous visitor's interest in an exhibit (a lead).

    Only an email and the exhibit are required — the rest of the visitor-
    intelligence fields (name, phone, dwell time, call-back) are optional so the
    frontend can capture a lead with just an email address.
    """

    name = serializers.CharField(required=False, allow_blank=True, default='')
    phone = serializers.CharField(required=False, allow_blank=True, default='')
    dwell_time = serializers.IntegerField(required=False, min_value=0, default=0)
    call_back_request = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Prospect
        fields = [
            'id',
            'exhibit',
            'name',
            'email',
            'phone',
            'dwell_time',
            'call_back_request',
            'saved_at',
        ]
        read_only_fields = ['id', 'saved_at']
