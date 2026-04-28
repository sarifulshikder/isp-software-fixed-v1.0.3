from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, DiscountViewSet

router = DefaultRouter()
router.register('invoices',  InvoiceViewSet,  basename='invoice')
router.register('discounts', DiscountViewSet, basename='discount')

urlpatterns = router.urls
