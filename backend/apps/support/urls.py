from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, KnowledgeBaseViewSet
router = DefaultRouter()
router.register('tickets', TicketViewSet, basename='ticket')
router.register('kb',      KnowledgeBaseViewSet, basename='kb')
urlpatterns = router.urls
