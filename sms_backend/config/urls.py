"""
Root URL configuration for SMS.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connections
from django.core.cache import cache
import redis

from django.http import JsonResponse

def health_liveness(request):
    return JsonResponse({"status": "ok"})


@api_view(['GET'])
def health_check(request):
    """
    Full health check for diagnostics (SAFE, non-blocking).
    """
    checks = {
        "status": "healthy",
        "services": {}
    }

    # Database
    try:
        connections['default'].cursor().execute("SELECT 1")
        checks["services"]["database"] = "ok"
    except Exception as e:
        checks["services"]["database"] = str(e)
        checks["status"] = "unhealthy"

    # Cache
    try:
        cache.set("health_check", "ok", 5)
        checks["services"]["cache"] = "ok"
    except Exception as e:
        checks["services"]["cache"] = str(e)
        checks["status"] = "unhealthy"

    return Response(
        checks,
        status=200 if checks["status"] == "healthy" else 503
    )




@api_view(['GET'])
def api_root(request):
    """
    API root endpoint with available endpoints.
    """
    return Response({
        'name': 'School Management System API',
        'version': '1.0.0',
        'documentation': '/api/docs/',
        'endpoints': {
            'auth': '/api/v1/auth/',
            'users': '/api/v1/users/',
            'students': '/api/v1/students/',
            'teachers': '/api/v1/teachers/',
            'courses': '/api/v1/courses/',
            'enrollments': '/api/v1/enrollments/',
            'attendance': '/api/v1/attendance/',
            'grades': '/api/v1/grades/',
            'finance': '/api/v1/finance/',
            'reports': '/api/v1/reports/',
        }
    })


urlpatterns = [


    path('health/', health_liveness, name='health_liveness'),
    # Health check
    path('health/full/', health_check, name='health_check'),
    # Admin
    path('admin/', admin.site.urls),
   

    # API Root
    path('api/', api_root, name='api_root'),
    
    # API v1
    path('api/v1/auth/', include('apps.auth_core.urls')),
    path('api/v1/academics/', include('apps.academics.urls')),
    # path('api/v1/finance/', include('apps.finance.urls')),
    # path('api/v1/reports/', include('apps.reports.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
