"""
Custom User Manager for the User model.
"""

from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user.
        
        Args:
            email: User's email address (required)
            password: User's password
            **extra_fields: Additional user fields
            
        Returns:
            User: Created user instance
            
        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError(_('Email address is required'))
        
        email = self.normalize_email(email)
        
        # Set defaults
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser.
        
        Args:
            email: Superuser's email address
            password: Superuser's password
            **extra_fields: Additional user fields
            
        Returns:
            User: Created superuser instance
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)
    
    def create_teacher(self, email, password=None, **extra_fields):
        """Create a teacher user."""
        from .role import Role, UserRole
        
        user = self.create_user(email, password, **extra_fields)
        
        # Assign teacher role
        teacher_role, _ = Role.objects.get_or_create(
            name=Role.TEACHER,
            defaults={'description': 'Teacher', 'level': 3}
        )
        UserRole.objects.create(user=user, role=teacher_role, is_primary=True)
        
        return user
    
    def create_student_user(self, email, password=None, **extra_fields):
        """Create a student user."""
        from .role import Role, UserRole
        
        user = self.create_user(email, password, **extra_fields)
        
        # Assign student role
        student_role, _ = Role.objects.get_or_create(
            name=Role.STUDENT,
            defaults={'description': 'Student', 'level': 1}
        )
        UserRole.objects.create(user=user, role=student_role, is_primary=True)
        
        return user
    
    def get_active(self):
        """Get all active (non-deleted) users."""
        return self.filter(is_active=True, deleted_at__isnull=True)
    
    def get_by_natural_key(self, email):
        """Get user by email (for authentication)."""
        return self.get(email=email)
