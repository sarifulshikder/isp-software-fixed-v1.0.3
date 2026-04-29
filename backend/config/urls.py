"""
ISP Software - Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

API_V1 = 'api/v1/'

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Health Check
    path('api/health/', include('utils.health_urls')),

    # Prometheus Metrics
    path('', include('django_prometheus.urls')),

    # API v1 Routes
    path(API_V1 + 'auth/',          include('apps.accounts.urls')),
    path(API_V1 + 'customers/',     include('apps.customers.urls')),
    path(API_V1 + 'billing/',       include('apps.billing.urls')),
    path(API_V1 + 'payments/',      include('apps.payments.urls')),
    path(API_V1 + 'packages/',      include('apps.packages.urls')),
    path(API_V1 + 'network/',       include('apps.network.urls')),
    path(API_V1 + 'support/',       include('apps.support.urls')),
    path(API_V1 + 'inventory/',     include('apps.inventory.urls')),
    path(API_V1 + 'reseller/',      include('apps.reseller.urls')),
    path(API_V1 + 'reports/',       include('apps.reports.urls')),
    path(API_V1 + 'hr/',            include('apps.hr.urls')),
    path(API_V1 + 'notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
