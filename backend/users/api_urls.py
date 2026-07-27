"""REST API URL routing for auth + the collector experience (React SPA)."""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import api_views

urlpatterns = [
    # Auth
    path('auth/register/', api_views.RegisterView.as_view(), name='api_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='api_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_refresh'),
    path('auth/me/', api_views.MeView.as_view(), name='api_me'),
    # Collector data (per-user, requires auth)
    path('collection/', api_views.CollectionView.as_view(), name='api_collection'),
    path('saved/', api_views.SavedCreateView.as_view(), name='api_saved_create'),
    path('saved/<int:exhibit_id>/', api_views.SavedDeleteView.as_view(), name='api_saved_delete'),
    path('inquiries/', api_views.InquiryCreateView.as_view(), name='api_inquiries'),
]
