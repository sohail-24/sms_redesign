"""
Base exception classes for the School Management System.
"""


class SMSException(Exception):
    """
    Base exception for all SMS exceptions.
    
    Attributes:
        message: Error message
        code: Error code for client-side handling
        details: Additional error details
    """
    
    default_message = "An error occurred"
    default_code = "error"
    status_code = 500
    
    def __init__(self, message=None, code=None, details=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self):
        """Convert exception to dictionary for API response."""
        return {
            'success': False,
            'error': {
                'code': self.code,
                'message': self.message,
                'details': self.details
            }
        }


class BusinessLogicError(SMSException):
    """
    Exception for business logic violations.
    
    Example:
        - Trying to enroll in a full course
        - Trying to mark attendance for a non-enrolled student
    """
    
    default_message = "Business logic error"
    default_code = "BUSINESS_LOGIC_ERROR"
    status_code = 400


class ValidationError(SMSException):
    """
    Exception for validation errors.
    
    Example:
        - Invalid email format
        - Required field missing
    """
    
    default_message = "Validation error"
    default_code = "VALIDATION_ERROR"
    status_code = 400


class NotFoundError(SMSException):
    """
    Exception for resource not found.
    
    Example:
        - Student not found
        - Course not found
    """
    
    default_message = "Resource not found"
    default_code = "NOT_FOUND"
    status_code = 404


class DuplicateError(SMSException):
    """
    Exception for duplicate resources.
    
    Example:
        - Student ID already exists
        - Email already registered
    """
    
    default_message = "Resource already exists"
    default_code = "DUPLICATE_ERROR"
    status_code = 409


class PermissionDeniedError(SMSException):
    """
    Exception for permission denied.
    
    Example:
        - User trying to access another user's data
        - User without required role
    """
    
    default_message = "Permission denied"
    default_code = "PERMISSION_DENIED"
    status_code = 403


class AuthenticationError(SMSException):
    """
    Exception for authentication failures.
    
    Example:
        - Invalid credentials
        - Token expired
    """
    
    default_message = "Authentication failed"
    default_code = "AUTHENTICATION_ERROR"
    status_code = 401


class RateLimitError(SMSException):
    """
    Exception for rate limiting.
    """
    
    default_message = "Rate limit exceeded"
    default_code = "RATE_LIMIT_EXCEEDED"
    status_code = 429


class ServiceUnavailableError(SMSException):
    """
    Exception for service unavailable.
    
    Example:
        - External service down
        - Database connection lost
    """
    
    default_message = "Service temporarily unavailable"
    default_code = "SERVICE_UNAVAILABLE"
    status_code = 503
