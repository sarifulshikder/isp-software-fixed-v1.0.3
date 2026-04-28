from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Permission

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ['email','first_name','last_name','role','is_active']
    list_filter   = ['role','is_active']
    search_fields = ['email','first_name','last_name']
    ordering      = ['-date_joined']
    fieldsets     = UserAdmin.fieldsets + (
        ('ISP Role', {'fields': ('role','phone','avatar','is_2fa_enabled')}),
    )

admin.site.register(Permission)
