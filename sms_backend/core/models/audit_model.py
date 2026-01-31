"""
Audit trail mixin for tracking changes to models.
"""

from django.db import models


class AuditMixin(models.Model):
    """
    Mixin that adds audit fields for tracking who created/modified records.
    
    Features:
    - Tracks creator and modifier
    - Timestamps for creation and modification
    """
    
    created_by = models.ForeignKey(
        'auth_core.User',  # Use string reference to avoid circular import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(class)s',
        help_text="User who created this record"
    )
    
    updated_by = models.ForeignKey(
        'auth_core.User',  # Use string reference to avoid circular import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_%(class)s',
        help_text="User who last updated this record"
    )
    
    class Meta:
        abstract = True
    
    def save_with_user(self, user=None, *args, **kwargs):
        """
        Save with user tracking.
        
        Args:
            user: The user performing the save operation
        """
        if not self.pk:
            # Creating new record
            self.created_by = user
        self.updated_by = user
        self.save(*args, **kwargs)


class AuditLog(models.Model):
    """
    Detailed audit log for tracking all changes.
    
    This model stores a history of changes made to other models.
    """
    
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('EXPORT', 'Export'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('OTHER', 'Other'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        'auth_core.User',  # Use string reference to avoid circular import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True
    )
    
    # Model information
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=255, blank=True)
    
    # Change details
    previous_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    changes = models.JSONField(null=True, blank=True)
    
    # Request information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model_name', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} {self.model_name} by {self.user} at {self.timestamp}"
    
    @classmethod
    def log(cls, user, action, instance, previous_data=None, new_data=None, 
            ip_address=None, user_agent=None):
        """
        Create an audit log entry.
        
        Args:
            user: The user performing the action
            action: The action type (CREATE, UPDATE, DELETE, etc.)
            instance: The model instance being acted upon
            previous_data: Previous state (for updates)
            new_data: New state (for creates/updates)
            ip_address: Client IP address
            user_agent: Client user agent
        """
        changes = None
        if previous_data and new_data:
            changes = {
                key: {'old': previous_data.get(key), 'new': new_data.get(key)}
                for key in set(previous_data.keys()) | set(new_data.keys())
                if previous_data.get(key) != new_data.get(key)
            }
        
        return cls.objects.create(
            user=user,
            action=action,
            model_name=instance.__class__.__name__,
            object_id=str(instance.pk),
            object_repr=str(instance)[:255],
            previous_data=previous_data,
            new_data=new_data,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else ''
        )
