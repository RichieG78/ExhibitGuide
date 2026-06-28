from django.urls import path

from . import views

urlpatterns = [
    path('', views.scan_view, name='scan'),
    path('simulate-scan/', views.exhibit_preview_view, name='simulate-scan'),

]
