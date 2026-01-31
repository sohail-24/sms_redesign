"""
Rate limiting middleware.
"""

from django.core.cache import cache
from django.http import JsonResponse


class RateLimitMiddleware:
    """
    Middleware to apply rate limiting per user/IP.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip rate limiting for health checks
        if request.path == '/health/':
            return self.get_response(request)
        
        # Get identifier (user ID if authenticated, else IP)
        if hasattr(request, 'user') and request.user.is_authenticated:
            key = f"rate_limit:user:{request.user.id}"
        else:
            key = f"rate_limit:ip:{self.get_client_ip(request)}"
        
        # Check rate limit (simple implementation)
        requests = cache.get(key, 0)
        if requests > 1000:  # 1000 requests per hour
            return JsonResponse({
                'success': False,
                'error': {
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Too many requests. Please try again later.'
                }
            }, status=429)
        
        # Increment counter
        cache.set(key, requests + 1, 3600)  # 1 hour expiry
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
