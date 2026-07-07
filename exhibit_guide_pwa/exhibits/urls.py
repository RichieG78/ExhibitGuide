from django.urls import path

from . import views

urlpatterns = [
    path('', views.scan_view, name='scan'),
    path('<int:exhibit_id>/', views.exhibit_preview_by_id_view, name='exhibit_preview'),
    path('qr/<int:qr_identifier>/', views.exhibit_preview_view, name='exhibit_preview_by_qr'),

]
