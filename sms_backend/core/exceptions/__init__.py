"""
Core exceptions module.
"""

from .base_exceptions import (
    SMSException,
    BusinessLogicError,
    ValidationError,
    NotFoundError,
    DuplicateError,
    PermissionDeniedError,
)

__all__ = [
    'SMSException',
    'BusinessLogicError',
    'ValidationError',
    'NotFoundError',
    'DuplicateError',
    'PermissionDeniedError',
]
