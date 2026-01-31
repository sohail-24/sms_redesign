"""
Exception handlers for DRF.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from .base_exceptions import SMSException


def custom_exception_handler(exc, context):
    """
    Custom exception handler that converts SMS exceptions to DRF responses.
    """
    # Handle SMS exceptions
    if isinstance(exc, SMSException):
        return Response(
            exc.to_dict(),
            status=exc.status_code
        )
    
    # Call DRF's default exception handler
    response = exception_handler(exc, context)
    
    # If DRF handled it, return the response
    if response is not None:
        # Wrap in standard format
        return Response({
            'success': False,
            'error': {
                'code': 'DRF_ERROR',
                'message': str(exc),
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data}
            }
        }, status=response.status_code)
    
    # Unhandled exception - return generic error
    return Response({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred',
            'details': {}
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def ratelimit_exceeded(request, exception):
    """
    Handler for rate limit exceeded.
    """
    return Response({
        'success': False,
        'error': {
            'code': 'RATE_LIMIT_EXCEEDED',
            'message': 'Too many requests. Please try again later.',
            'details': {}
        }
    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
