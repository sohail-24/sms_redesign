"""
Role-Based Access Control (RBAC) models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel

User = get_user_model()


class Role(BaseModel):
    """
    Role model for RBAC.
    
    Predefined roles:
    - SUPER_ADMIN: Full system access
    - ADMIN: School administrator
    - PRINCIPAL: School principal
    - ACCOUNTANT: Finance manager
    - TEACHER: Teacher
    - STUDENT: Student
    - STAFF: Support staff
    - PARENT: Parent/Guardian
    """
    
    # Role constants
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    PRINCIPAL = 'principal'
    ACCOUNTANT = 'accountant'
    TEACHER = 'teacher'
    STUDENT = 'student'
    STAFF = 'staff'
    PARENT = 'parent'
    
    ROLE_CHOICES = [
        (SUPER_ADMIN, 'Super Administrator'),
        (ADMIN, 'Administrator'),
        (PRINCIPAL, 'Principal'),
        (ACCOUNTANT, 'Accountant'),
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
        (STAFF, 'Staff'),
        (PARENT, 'Parent'),
    ]
    
    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True,
        db_index=True
    )
    
    description = models.TextField(blank=True)
    
    # Role hierarchy (higher number = more permissions)
    level = models.PositiveSmallIntegerField(
        default=0,
        help_text="Role hierarchy level (higher = more permissions)"
    )
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-level', 'name']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.get_name_display()
    
    @classmethod
    def get_default_role(cls):
        """Get the default role for new users."""
        return cls.STUDENT
    
    @property
    def permissions_list(self):
        """Get all permissions for this role."""
        return self.permissions.values_list('codename', flat=True)


class UserRole(BaseModel):
    """
    Many-to-many relationship between User and Role.
    
    A user can have multiple roles (e.g., Teacher + Staff).
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    
    # Optional: Role assignment can be time-bound
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Who assigned this role
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roles_assigned'
    )
    
    is_primary = models.BooleanField(
        default=False,
        help_text="Primary role for the user"
    )
    
    class Meta:
        unique_together = ['user', 'role']
        ordering = ['-is_primary', '-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.role}"
    
    @property
    def is_valid(self):
        """Check if this role assignment is currently valid."""
        from django.utils import timezone
        now = timezone.now()
        
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True
