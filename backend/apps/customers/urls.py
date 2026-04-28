from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, ZoneViewSet

router = DefaultRouter()
router.register('zones',    ZoneViewSet,    basename='zone')
router.register('',         CustomerViewSet, basename='customer')

urlpatterns = router.urls
