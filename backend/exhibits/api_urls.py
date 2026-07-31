"""REST API URL routing for the exhibits app.

A DRF router turns a ViewSet into a full set of REST URLs automatically:
    /exhibits/        -> list all exhibits (GET)
    /exhibits/<id>/   -> retrieve one exhibit (GET)
These are mounted under the /api/ prefix by the project URL config.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ArtistViewSet,
    ArtworkViewSet,
    ExchangeRatesView,
    ExhibitByQrView,
    ExhibitViewSet,
    MuseumSearchView,
    ProspectCreateView,
    ShowViewSet,
)

router = DefaultRouter()
router.register(r'exhibits', ExhibitViewSet, basename='exhibit')
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'artworks', ArtworkViewSet, basename='artwork')
router.register(r'shows', ShowViewSet, basename='show')

urlpatterns = [
    # Must precede the router: its /exhibits/<pk>/ pattern would otherwise
    # capture the literal "qr" segment as a primary key.
    path(
        'exhibits/qr/<int:qr_identifier>/',
        ExhibitByQrView.as_view(),
        name='exhibit_by_qr',
    ),
] + router.urls + [
    # Public lead capture (POST): a visitor expressing interest in an exhibit.
    path('interest/', ProspectCreateView.as_view(), name='interest'),
    # Public third-party integrations used by the frontend.
    path('external/exchange-rates/', ExchangeRatesView.as_view(), name='external_exchange_rates'),
    path('external/museum-search/', MuseumSearchView.as_view(), name='external_museum_search'),
]
