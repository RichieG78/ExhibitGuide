"""Top-level URL routing for the project.

The frontend is a separate React app that talks to the REST API under /api/.
Django here serves the API and the admin only — the old server-rendered pages
(scan, exhibit, register/login/logout, dashboard, profile, password reset) were
retired when React took over.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Back-office content management (artists, artworks, shows, exhibits, leads).
    path('admin/', admin.site.urls),
    # REST API endpoints (React frontend).
    path('api/', include('exhibits.api_urls')),
    # Auth + per-user collector API (JWT).
    path('api/', include('users.api_urls')),
]

if settings.DEBUG:
    # Serve uploaded media files directly in local development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
