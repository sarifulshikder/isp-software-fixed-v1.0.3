from rest_framework.routers import DefaultRouter
from .views import ResellerViewSet, ResellerCommissionViewSet

router = DefaultRouter()
router.register('commissions', ResellerCommissionViewSet, basename='commission')
router.register('',            ResellerViewSet,           basename='reseller')

urlpatterns = router.urls
