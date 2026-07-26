"""REST API URL routing for the exhibits app.

A DRF router turns a ViewSet into a full set of REST URLs automatically:
    /exhibits/        -> list all exhibits (GET)
    /exhibits/<id>/   -> retrieve one exhibit (GET)
These are mounted under the /api/ prefix by the project URL config.
"""

from rest_framework.routers import DefaultRouter

from .views import ArtistViewSet, ArtworkViewSet, ExhibitViewSet, ShowViewSet

router = DefaultRouter()
router.register(r'exhibits', ExhibitViewSet, basename='exhibit')
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'artworks', ArtworkViewSet, basename='artwork')
router.register(r'shows', ShowViewSet, basename='show')

urlpatterns = router.urls
