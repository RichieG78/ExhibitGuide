"""REST API views for exhibits, artists, artworks, shows, and lead capture.

The public server-rendered pages (scan, exhibit preview) were retired when the
React frontend took over; this module is now API-only.
"""

from django.utils import timezone
from rest_framework import generics, permissions, viewsets

from users.models import Prospect

from .models import Artist, Artwork, Exhibit, Show
from .serializers import (
	ArtistSerializer,
	ArtworkSerializer,
	ExhibitSerializer,
	ProspectSerializer,
	ShowSerializer,
)


class IsStaffOrReadOnly(permissions.BasePermission):
	"""Anyone may read exhibits; only staff (gallery owners) may write them."""

	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		return bool(request.user and request.user.is_staff)


class ExhibitViewSet(viewsets.ModelViewSet):
	"""REST API endpoints for exhibits.

	Reads (list + detail) are public; create/update/delete are restricted to
	staff (gallery owners) via IsStaffOrReadOnly. Image uploads work through
	DRF's default multipart parser.
	"""

	serializer_class = ExhibitSerializer
	permission_classes = [IsStaffOrReadOnly]
	# select_related pre-fetches the linked artwork/artist/show in one query, so
	# the serializer's derived fields (artist, medium, show_name, ...) do not each
	# trigger an extra database hit.
	queryset = (
		Exhibit.objects.select_related('artwork', 'artwork__artist', 'show')
		.order_by('-publish_date')
	)

	def perform_create(self, serializer):
		# The owner is the staff user creating it; fill required fields the form
		# may omit (string fields already default to '').
		extra = {'user': self.request.user}
		if not serializer.validated_data.get('publish_date'):
			extra['publish_date'] = timezone.now()
		if serializer.validated_data.get('price') is None:
			extra['price'] = 0
		serializer.save(**extra)


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
	"""Read-only REST API endpoints for artists (list + detail)."""

	serializer_class = ArtistSerializer
	queryset = Artist.objects.order_by('lastname', 'firstname')


class ArtworkViewSet(viewsets.ReadOnlyModelViewSet):
	"""Read-only REST API endpoints for artworks (list + detail)."""

	serializer_class = ArtworkSerializer
	# Pre-fetch the linked artist so `artist_name` doesn't add a query per row.
	queryset = Artwork.objects.select_related('artist').order_by('title')


class ShowViewSet(viewsets.ReadOnlyModelViewSet):
	"""Read-only REST API endpoints for shows (list + detail)."""

	serializer_class = ShowSerializer
	queryset = Show.objects.order_by('show_name')


class ProspectCreateView(generics.CreateAPIView):
	"""Public endpoint to capture a visitor's interest in an exhibit (a lead).

	Open to anonymous visitors — no login required — so scanning a work and
	expressing interest never hits an auth wall. This is write-only (create).
	"""

	serializer_class = ProspectSerializer
	queryset = Prospect.objects.all()
	permission_classes = [permissions.AllowAny]
	authentication_classes = []
