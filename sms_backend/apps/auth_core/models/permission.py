"""
Permission models for granular access control.
"""

from django.db import models
from core.models import BaseModel


class Permission(BaseModel):
    """
    Custom permission model for fine-grained access control.
    
    Permissions are organized by module and action.
    Example: students.view, students.edit, finance.invoice.create
    """
    
    # Module choices
    MODULE_GENERAL = 'general'
    MODULE_AUTH = 'auth'
    MODULE_STUDENTS = 'students'
    MODULE_TEACHERS = 'teachers'
    MODULE_COURSES = 'courses'
    MODULE_ENROLLMENTS = 'enrollments'
    MODULE_ATTENDANCE = 'attendance'
    MODULE_GRADES = 'grades'
    MODULE_FINANCE = 'finance'
    MODULE_REPORTS = 'reports'
    MODULE_SETTINGS = 'settings'
    
    MODULE_CHOICES = [
        (MODULE_GENERAL, 'General'),
        (MODULE_AUTH, 'Authentication'),
        (MODULE_STUDENTS, 'Students'),
        (MODULE_TEACHERS, 'Teachers'),
        (MODULE_COURSES, 'Courses'),
        (MODULE_ENROLLMENTS, 'Enrollments'),
        (MODULE_ATTENDANCE, 'Attendance'),
        (MODULE_GRADES, 'Grades'),
        (MODULE_FINANCE, 'Finance'),
        (MODULE_REPORTS, 'Reports'),
        (MODULE_SETTINGS, 'Settings'),
    ]
    
    # Action choices
    ACTION_VIEW = 'view'
    ACTION_CREATE = 'create'
    ACTION_EDIT = 'edit'
    ACTION_DELETE = 'delete'
    ACTION_EXPORT = 'export'
    ACTION_IMPORT = 'import'
    ACTION_APPROVE = 'approve'
    ACTION_MANAGE = 'manage'
    
    ACTION_CHOICES = [
        (ACTION_VIEW, 'View'),
        (ACTION_CREATE, 'Create'),
        (ACTION_EDIT, 'Edit'),
        (ACTION_DELETE, 'Delete'),
        (ACTION_EXPORT, 'Export'),
        (ACTION_IMPORT, 'Import'),
        (ACTION_APPROVE, 'Approve'),
        (ACTION_MANAGE, 'Manage'),
    ]
    
    codename = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique permission code (e.g., 'students.view')"
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Human-readable permission name"
    )
    
    module = models.CharField(
        max_length=50,
        choices=MODULE_CHOICES,
        db_index=True
    )
    
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        db_index=True
    )
    
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['module', 'action', 'codename']
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        indexes = [
            models.Index(fields=['module', 'action']),
        ]
    
    def __str__(self):
        return f"{self.codename} ({self.name})"
    
    @classmethod
    def has_permission(cls, user, codename):
        """Check if user has a specific permission."""
        if user.is_superuser:
            return True
        return user.roles.filter(
            permissions__codename=codename,
            is_active=True
        ).exists()


class RolePermission(BaseModel):
    """
    Many-to-many relationship between Role and Permission.
    """
    
    role = models.ForeignKey(
        'Role',
        on_delete=models.CASCADE,
        related_name='permissions'
    )
    
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    
    # Optional: Permission can be scoped (e.g., only for specific classes)
    scope = models.JSONField(
        null=True,
        blank=True,
        help_text="Optional scope restrictions (JSON)"
    )
    
    class Meta:
        unique_together = ['role', 'permission']
    
    def __str__(self):
        return f"{self.role} - {self.permission}"
