"""
Role-based permission classes for the ISP application.

Use these in DRF ViewSet `permission_classes` to restrict actions to
specific staff roles. They build on top of `IsAuthenticated`.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


def _has_role(user, *roles):
    return bool(user and user.is_authenticated and getattr(user, 'role', None) in roles)


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request.user, 'superadmin') or (request.user and request.user.is_superuser)


class IsAdminRole(BasePermission):
    """Admin or higher (superadmin)."""
    def has_permission(self, request, view):
        return _has_role(request.user, 'superadmin', 'admin') or (request.user and request.user.is_superuser)


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request.user, 'superadmin', 'admin', 'manager')


class IsBilling(BasePermission):
    """Accountants/managers/admins can manage billing & payments."""
    def has_permission(self, request, view):
        return _has_role(request.user, 'superadmin', 'admin', 'manager', 'accountant')


class IsTechnician(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request.user, 'superadmin', 'admin', 'manager', 'technician')


class IsSupportStaff(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request.user, 'superadmin', 'admin', 'manager', 'support')


class IsStaffReadOnlyOrAdminWrite(BasePermission):
    """Any authenticated staff can read; only admin/manager can write."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return _has_role(request.user, 'superadmin', 'admin', 'manager')
