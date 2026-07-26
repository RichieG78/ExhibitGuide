"""Public URL patterns for scan and exhibit pages."""

from django.urls import path

from . import views

urlpatterns = [
    # The scan route is the main public entry point into the exhibit experience.
    path('', views.scan_view, name='scan'),
    # This route is useful for previews, testing, and direct links from admin.
    path('<int:exhibit_id>/', views.exhibit_preview_by_id_view, name='exhibit_preview'),
    # Printed QR codes resolve through this stable public route.
    path('qr/<int:qr_identifier>/', views.exhibit_preview_view, name='exhibit_preview_by_qr'),
]
