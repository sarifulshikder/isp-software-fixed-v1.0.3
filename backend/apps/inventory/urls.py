from rest_framework.routers import DefaultRouter
from .views import ProductCategoryViewSet, ProductViewSet, StockMovementViewSet, CustomerEquipmentViewSet

router = DefaultRouter()
router.register('categories', ProductCategoryViewSet, basename='category')
router.register('products',   ProductViewSet,          basename='product')
router.register('movements',  StockMovementViewSet,    basename='movement')
router.register('equipment',  CustomerEquipmentViewSet, basename='equipment')

urlpatterns = router.urls
