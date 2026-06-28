from django.shortcuts import render


def scan_view(request):
	return render(request, 'exhibits/scan.html')


def exhibit_preview_view(request):
	return render(request, 'exhibits/base.html')
