"""REST API views for exhibits, artists, artworks, shows, and lead capture.

The public server-rendered pages (scan, exhibit preview) were retired when the
React frontend took over; this module is now API-only.
"""

import json
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

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


class ExhibitByQrView(generics.RetrieveAPIView):
	"""Public lookup of one exhibit by its printed QR identifier.

	Printed QR codes encode /qr/<qr_identifier> on the frontend, which resolves
	the work through this endpoint. Deliberately public: scanning a code in the
	gallery must never hit a login wall.
	"""

	serializer_class = ExhibitSerializer
	permission_classes = [permissions.AllowAny]
	authentication_classes = []
	lookup_field = 'qr_identifier'
	queryset = Exhibit.objects.select_related('artwork', 'artwork__artist', 'show')


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


def _fetch_json(url):
	"""Fetch JSON from a third-party API with a short timeout."""
	request = Request(url, headers={'User-Agent': 'ExhibitGuide/1.0'})
	with urlopen(request, timeout=6) as response:
		payload = response.read().decode('utf-8')
		return json.loads(payload)


class ExchangeRatesView(APIView):
	"""Public exchange-rate proxy using Frankfurter (third-party API)."""

	permission_classes = [permissions.AllowAny]
	authentication_classes = []

	def get(self, request):
		base = (request.query_params.get('base') or 'USD').upper().strip()
		symbols_raw = (request.query_params.get('symbols') or 'EUR,GBP').upper()
		symbols = [symbol.strip() for symbol in symbols_raw.split(',') if symbol.strip()]

		if not base.isalpha() or len(base) != 3:
			return Response({'detail': 'Invalid base currency.'}, status=status.HTTP_400_BAD_REQUEST)

		valid_symbols = [symbol for symbol in symbols if symbol.isalpha() and len(symbol) == 3]
		if not valid_symbols:
			return Response({'detail': 'At least one valid target currency is required.'}, status=status.HTTP_400_BAD_REQUEST)

		url = (
			'https://api.frankfurter.app/latest'
			f'?from={base}&to={",".join(valid_symbols)}'
		)

		try:
			data = _fetch_json(url)
		except (URLError, TimeoutError, json.JSONDecodeError):
			return Response(
				{'detail': 'Exchange-rate service is currently unavailable.'},
				status=status.HTTP_502_BAD_GATEWAY,
			)

		return Response(
			{
				'provider': 'frankfurter',
				'base': data.get('base', base),
				'date': data.get('date'),
				'rates': data.get('rates', {}),
			}
		)


class MuseumSearchView(APIView):
	"""Public museum lookup proxy using The Met Collection API."""

	permission_classes = [permissions.AllowAny]
	authentication_classes = []

	def get(self, request):
		query = (request.query_params.get('q') or '').strip()
		limit_raw = request.query_params.get('limit') or '3'

		if not query:
			return Response({'detail': 'Query parameter q is required.'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			limit = max(1, min(int(limit_raw), 6))
		except ValueError:
			limit = 3

		search_url = (
			'https://collectionapi.metmuseum.org/public/collection/v1/search'
			f'?hasImages=true&q={quote_plus(query)}'
		)

		try:
			search_data = _fetch_json(search_url)
		except (URLError, TimeoutError, json.JSONDecodeError):
			return Response(
				{'detail': 'Museum data service is currently unavailable.'},
				status=status.HTTP_502_BAD_GATEWAY,
			)

		object_ids = (search_data.get('objectIDs') or [])[:limit]
		results = []
		for object_id in object_ids:
			object_url = (
				'https://collectionapi.metmuseum.org/public/collection/v1/objects/'
				f'{object_id}'
			)
			try:
				item = _fetch_json(object_url)
			except (URLError, TimeoutError, json.JSONDecodeError):
				continue

			results.append(
				{
					'object_id': item.get('objectID'),
					'title': item.get('title'),
					'artist': item.get('artistDisplayName'),
					'date': item.get('objectDate'),
					'image': item.get('primaryImageSmall') or item.get('primaryImage'),
					'url': item.get('objectURL'),
					'museum': item.get('repository'),
				}
			)

		return Response(
			{
				'provider': 'the-met',
				'query': query,
				'total_found': search_data.get('total', 0),
				'results': results,
			}
		)
