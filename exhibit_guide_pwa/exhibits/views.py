from django.shortcuts import get_object_or_404, render

from .models import Exhibit


def scan_view(request):
	latest_exhibit = Exhibit.objects.order_by('-publish_date').first()
	return render(request, 'exhibits/scan.html', {'latest_exhibit': latest_exhibit})


def exhibit_preview_view(request, qr_identifier):
	featured_exhibit = get_object_or_404(Exhibit, qr_identifier=qr_identifier)
	return render(request, 'exhibits/base.html', {'featured_exhibit': featured_exhibit})


def exhibit_preview_by_id_view(request, exhibit_id):
	featured_exhibit = get_object_or_404(Exhibit, id=exhibit_id)
	return render(request, 'exhibits/base.html', {'featured_exhibit': featured_exhibit})
