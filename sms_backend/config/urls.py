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


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint for monitoring.
    """
    checks = {
        'status': 'healthy',
        'timestamp': __import__('django.utils.timezone').utils.timezone.now().isoformat(),
        'services': {}
    }
    
    # Check database
    try:
        connections['default'].cursor().execute('SELECT 1')
        checks['services']['database'] = {'status': 'healthy'}
    except Exception as e:
        checks['services']['database'] = {'status': 'unhealthy', 'error': str(e)}
        checks['status'] = 'unhealthy'
    
    # Check cache
    try:
        cache.set('health_check', 'ok', 10)
        value = cache.get('health_check')
        if value == 'ok':
            checks['services']['cache'] = {'status': 'healthy'}
        else:
            checks['services']['cache'] = {'status': 'unhealthy', 'error': 'Cache read failed'}
            checks['status'] = 'unhealthy'
    except Exception as e:
        checks['services']['cache'] = {'status': 'unhealthy', 'error': str(e)}
        checks['status'] = 'unhealthy'
    
    # Check Celery (via Redis)
    try:
        from infrastructure.celery.celery_app import app
        inspector = app.control.inspect()
        stats = inspector.stats()
        if stats:
            checks['services']['celery'] = {'status': 'healthy', 'workers': len(stats)}
        else:
            checks['services']['celery'] = {'status': 'warning', 'message': 'No workers running'}
    except Exception as e:
        checks['services']['celery'] = {'status': 'unhealthy', 'error': str(e)}
    
    status_code = 200 if checks['status'] == 'healthy' else 503
    return Response(checks, status=status_code)


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
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
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
