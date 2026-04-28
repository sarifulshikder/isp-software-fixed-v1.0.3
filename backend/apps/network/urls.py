from rest_framework.routers import DefaultRouter
from .views import IPPoolViewSet, IPAddressViewSet, NetworkDeviceViewSet, RADIUSSessionViewSet, NetworkAlertViewSet
router = DefaultRouter()
router.register('ip-pools',   IPPoolViewSet,         basename='ippool')
router.register('ip-address', IPAddressViewSet,       basename='ipaddress')
router.register('devices',    NetworkDeviceViewSet,   basename='device')
router.register('sessions',   RADIUSSessionViewSet,   basename='session')
router.register('alerts',     NetworkAlertViewSet,    basename='alert')
urlpatterns = router.urls
