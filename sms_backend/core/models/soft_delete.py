"""
Soft delete implementation for models.
"""

from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """
    QuerySet that supports soft delete operations.
    """
    
    def active(self):
        """Return only non-deleted records."""
        return self.filter(deleted_at__isnull=True)
    
    def deleted(self):
        """Return only deleted records."""
        return self.filter(deleted_at__isnull=False)
    
    def with_deleted(self):
        """Return all records including deleted."""
        return self.all()


class SoftDeleteManager(models.Manager):
    """
    Manager that filters out soft-deleted records by default.
    """
    
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).active()
    
    def deleted(self):
        """Return only deleted records."""
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()
    
    def with_deleted(self):
        """Return all records including deleted."""
        return SoftDeleteQuerySet(self.model, using=self._db).with_deleted()


class SoftDeleteModel(models.Model):
    """
    Abstract model that implements soft delete functionality.
    
    Instead of permanently deleting records, this sets a deleted_at timestamp.
    Records can be restored if needed.
    
    Usage:
        class MyModel(SoftDeleteModel):
            name = models.CharField(max_length=100)
            
        obj = MyModel.objects.create(name='Test')
        obj.soft_delete()  # Soft delete
        obj.restore()      # Restore
    """
    
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deleted_by = models.ForeignKey(
        'auth_core.User',  # Use string reference to avoid circular import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_%(class)s',
        help_text="User who deleted this record"
    )
    
    # Default manager - excludes deleted records
    objects = SoftDeleteManager()
    
    # Manager that includes all records (for admin purposes)
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['deleted_at']),
        ]
    
    def soft_delete(self, user=None):
        """
        Soft delete this record.
        
        Args:
            user: The user performing the deletion (for audit)
        """
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=['deleted_at', 'deleted_by'])
    
    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['deleted_at', 'deleted_by'])
    
    def hard_delete(self):
        """
        Permanently delete this record.
        Use with caution - this cannot be undone!
        """
        super().delete()
    
    @property
    def is_deleted(self):
        """Check if this record has been soft deleted."""
        return self.deleted_at is not None
    
    @property
    def is_active(self):
        """Check if this record is active (not deleted)."""
        return self.deleted_at is None
    
    def delete(self, using=None, keep_parents=False):
        """
        Override delete to perform soft delete by default.
        """
        self.soft_delete()
