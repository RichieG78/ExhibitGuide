from django.shortcuts import render

from .models import Exhibit


def scan_view(request):
	return render(request, 'exhibits/scan.html')


def exhibit_preview_view(request):
	featured_exhibit = Exhibit.objects.order_by('-publish_date').first()
	return render(request, 'exhibits/base.html', {'featured_exhibit': featured_exhibit})
