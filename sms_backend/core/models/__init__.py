"""
Core models and mixins for the School Management System.
"""

from .base_model import BaseModel, TimestampMixin
from .soft_delete import SoftDeleteModel, SoftDeleteManager
from .audit_model import AuditMixin

__all__ = [
    'BaseModel',
    'TimestampMixin',
    'SoftDeleteModel',
    'SoftDeleteManager',
    'AuditMixin',
]
