from rest_framework.routers import DefaultRouter
from .views import NotificationTemplateViewSet, NotificationLogViewSet

router = DefaultRouter()
router.register('templates', NotificationTemplateViewSet, basename='notif-template')
router.register('logs',      NotificationLogViewSet,      basename='notif-log')

urlpatterns = router.urls
