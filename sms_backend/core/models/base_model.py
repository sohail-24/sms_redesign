"""
Base model with common fields and functionality.
"""

import uuid
from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    """
    Mixin that adds created_at and updated_at fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDMixin(models.Model):
    """
    Mixin that adds UUID primary key.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    
    class Meta:
        abstract = True


class BaseModel(TimestampMixin, models.Model):
    """
    Abstract base model with common fields for all models.
    
    Features:
    - Auto timestamp fields
    - Soft delete support (via SoftDeleteModel)
    - Optimized for querying with indexes
    """
    
    class Meta:
        abstract = True
        # Default ordering by creation date (newest first)
        ordering = ['-created_at']
        # Create indexes on commonly queried fields
        indexes = [
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure updated_at is always set.
        """
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_recent(cls, limit=10):
        """Get recent records."""
        return cls.objects.all()[:limit]
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date):
        """Get records within a date range."""
        return cls.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
