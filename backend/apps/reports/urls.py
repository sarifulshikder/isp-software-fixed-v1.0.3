from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, ReportTemplateViewSet

router = DefaultRouter()
router.register('templates', ReportTemplateViewSet, basename='report-template')
router.register('',          ReportViewSet,          basename='report')

urlpatterns = router.urls
