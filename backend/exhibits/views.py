"""Public views for scanning and viewing exhibits."""

from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets

from .models import Exhibit
from .serializers import ExhibitSerializer


def scan_view(request):
	"""Show a simple scan entry point that links to the newest exhibit."""
	latest_exhibit = Exhibit.objects.order_by('-publish_date').first()
	return render(request, 'exhibits/scan.html', {'latest_exhibit': latest_exhibit})


def exhibit_preview_view(request, qr_identifier):
	"""Look up an exhibit by its QR code number and show the public detail page."""
	featured_exhibit = get_object_or_404(Exhibit, qr_identifier=qr_identifier)
	return render(request, 'exhibits/base.html', {'featured_exhibit': featured_exhibit})


def exhibit_preview_by_id_view(request, exhibit_id):
	"""Fallback route that loads an exhibit directly by database id."""
	featured_exhibit = get_object_or_404(Exhibit, id=exhibit_id)
	return render(request, 'exhibits/base.html', {'featured_exhibit': featured_exhibit})


class ExhibitViewSet(viewsets.ReadOnlyModelViewSet):
	"""Read-only REST API endpoints for exhibits (list + detail).

	`ReadOnlyModelViewSet` provides GET-list and GET-detail only. Create/update/
	delete are intentionally left out until API authentication is added, so the
	public exhibit data is safely readable but not yet writable over the API.
	"""

	serializer_class = ExhibitSerializer
	# select_related pre-fetches the linked artwork/artist/show in one query, so
	# the serializer's derived fields (artist, medium, show_name, ...) do not each
	# trigger an extra database hit.
	queryset = (
		Exhibit.objects.select_related('artwork', 'artwork__artist', 'show')
		.order_by('-publish_date')
	)
