from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, StaffProfileViewSet, AttendanceViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register('departments', DepartmentViewSet, basename='department')
router.register('staff',       StaffProfileViewSet, basename='staff')
router.register('attendance',  AttendanceViewSet,   basename='attendance')
router.register('leaves',      LeaveRequestViewSet, basename='leave')

urlpatterns = router.urls
