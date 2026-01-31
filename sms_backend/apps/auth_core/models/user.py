"""
Custom User model for the School Management System.
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator, RegexValidator

from core.models import TimestampMixin
from .user_manager import UserManager


class User(AbstractBaseUser, PermissionsMixin, TimestampMixin):
    """
    Custom User model with email as the primary identifier.
    
    Features:
    - Email-based authentication
    - UUID primary key
    - Soft delete support
    - Role-based permissions
    - Profile photo support
    
    Attributes:
        email: Primary identifier (unique)
        username: Optional display name
        first_name, last_name: User's name
        is_active: Account status
        is_staff: Admin panel access
        email_verified: Email verification status
        last_login_ip: For security tracking
    """
    
    # Primary key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Authentication fields
    email = models.EmailField(
        _('email address'),
        unique=True,
        validators=[EmailValidator()],
        error_messages={
            'unique': _('A user with this email already exists.'),
        }
    )
    
    username = models.CharField(
        _('username'),
        max_length=150,
        blank=True,
        help_text=_('Optional display name')
    )
    
    # Personal information
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_('Phone number must be in format: "+999999999". Up to 15 digits.')
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True
    )
    
    # Profile photo
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('Profile picture')
    )
    
    # Status fields
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user can log in.')
    )
    
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into the admin site.')
    )
    
    email_verified = models.BooleanField(
        _('email verified'),
        default=False,
        help_text=_('Designates whether the email address is verified.')
    )
    
    phone_verified = models.BooleanField(
        _('phone verified'),
        default=False,
        help_text=_('Designates whether the phone number is verified.')
    )
    
    # Security tracking
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    
    failed_login_attempts = models.PositiveSmallIntegerField(
        default=0,
        help_text=_('Number of consecutive failed login attempts')
    )
    
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Account locked until this time')
    )
    
    password_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Last password change timestamp')
    )
    
    # Soft delete
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True
    )
    
    # Metadata
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    
    # Custom manager
    objects = UserManager()
    
    # Authentication configuration
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'deleted_at']),
            models.Index(fields=['date_joined']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the user's full name."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email
    
    def get_short_name(self):
        """Return the user's short name."""
        return self.first_name or self.email
    
    @property
    def is_locked(self):
        """Check if the account is currently locked."""
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        return False
    
    @property
    def display_name(self):
        """Return the best display name for the user."""
        if self.username:
            return self.username
        return self.get_full_name()
    
    @property
    def roles(self):
        """Get all active roles for this user."""
        from .role import UserRole
        return UserRole.objects.filter(
            user=self,
            role__is_active=True
        ).select_related('role')
    
    @property
    def primary_role(self):
        """Get the user's primary role."""
        from .role import UserRole
        try:
            user_role = UserRole.objects.filter(
                user=self,
                is_primary=True,
                role__is_active=True
            ).select_related('role').first()
            return user_role.role if user_role else None
        except UserRole.DoesNotExist:
            return None
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return self.roles.filter(role__name=role_name).exists()
    
    def has_permission(self, codename):
        """Check if user has a specific permission."""
        if self.is_superuser:
            return True
        from .permission import Permission
        return Permission.has_permission(self, codename)
    
    def record_login(self, ip_address=None):
        """Record successful login."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login_ip = ip_address
        self.save(update_fields=['failed_login_attempts', 'locked_until', 'last_login_ip'])
    
    def record_failed_login(self):
        """Record failed login attempt."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        
        self.save(update_fields=['failed_login_attempts', 'locked_until'])
    
    def soft_delete(self):
        """Soft delete the user account."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at'])
    
    def restore(self):
        """Restore a soft-deleted user account."""
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=['is_active', 'deleted_at'])
