"""
Audit middleware for logging requests.
"""

import time
import logging

logger = logging.getLogger('apps.audit')


class AuditMiddleware:
    """
    Middleware to log all requests for audit purposes.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Log request details
        duration = time.time() - start_time
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.info(
                f"Request: {request.method} {request.path} - "
                f"User: {request.user.email} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )
        
        return response
