"""
Teacher Profile model.
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from core.models import BaseModel, SoftDeleteModel

User = get_user_model()


class TeacherProfile(BaseModel, SoftDeleteModel):
    """
    Extended profile for teacher users.
    
    This model contains teacher-specific information separate from the
    base User model to maintain clean separation of concerns.
    """
    
    # Gender choices
    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'
    GENDER_OTHER = 'other'
    
    GENDER_CHOICES = [
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    ]
    
    # Employment status
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_ON_LEAVE = 'on_leave'
    STATUS_RESIGNED = 'resigned'
    STATUS_TERMINATED = 'terminated'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_ON_LEAVE, 'On Leave'),
        (STATUS_RESIGNED, 'Resigned'),
        (STATUS_TERMINATED, 'Terminated'),
    ]
    
    # Link to User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    
    # Teacher ID (unique identifier for the school)
    teacher_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique teacher ID assigned by the school"
    )
    
    # Personal information
    date_of_birth = models.DateField(null=True, blank=True)
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )
    
    photo = models.ImageField(
        upload_to='teacher_photos/%Y/%m/',
        blank=True,
        null=True
    )
    
    # Contact information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default='India')
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Professional information
    department = models.CharField(max_length=100, blank=True)
    
    designation = models.CharField(
        max_length=100,
        blank=True,
        help_text="Job title (e.g., 'Senior Teacher', 'HOD')"
    )
    
    qualification = models.CharField(
        max_length=200,
        blank=True,
        help_text="Educational qualifications"
    )
    
    specialization = models.CharField(
        max_length=200,
        blank=True,
        help_text="Subject specialization"
    )
    
    experience_years = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Years of teaching experience"
    )
    
    # Employment details
    joining_date = models.DateField()
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        db_index=True
    )
    
    resignation_date = models.DateField(null=True, blank=True)
    
    # Subjects taught (can teach multiple subjects)
    subjects = models.JSONField(
        default=list,
        blank=True,
        help_text="List of subjects the teacher can teach"
    )
    
    # Employment type
    EMPLOYMENT_FULL_TIME = 'full_time'
    EMPLOYMENT_PART_TIME = 'part_time'
    EMPLOYMENT_CONTRACT = 'contract'
    
    EMPLOYMENT_CHOICES = [
        (EMPLOYMENT_FULL_TIME, 'Full Time'),
        (EMPLOYMENT_PART_TIME, 'Part Time'),
        (EMPLOYMENT_CONTRACT, 'Contract'),
    ]
    
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_CHOICES,
        default=EMPLOYMENT_FULL_TIME
    )
    
    # Salary information (optional, can be in finance module)
    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Additional info
    bio = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Teacher Profile'
        verbose_name_plural = 'Teacher Profiles'
        indexes = [
            models.Index(fields=['teacher_id']),
            models.Index(fields=['status']),
            models.Index(fields=['department']),
            models.Index(fields=['joining_date']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.teacher_id})"
    
    @property
    def full_name(self):
        """Return teacher's full name."""
        return self.user.get_full_name()
    
    def get_full_name(self):
        """Return teacher's full name (alias for full_name)."""
        return self.full_name
    
    @property
    def email(self):
        """Return teacher's email."""
        return self.user.email
    
    @property
    def phone_number(self):
        """Return teacher's phone number."""
        return self.user.phone_number
    
    @property
    def is_active(self):
        """Check if teacher is currently active."""
        return self.status == self.STATUS_ACTIVE
    
    @property
    def active_courses_count(self):
        """Get the number of active courses taught by this teacher."""
        return self.courses.filter(is_active=True).count()
    
    @property
    def total_students(self):
        """Get the total number of students across all courses."""
        from .enrollment import Enrollment
        return Enrollment.objects.filter(
            course__teacher=self,
            status='active'
        ).values('student').distinct().count()
    
    def get_schedule(self, day_of_week=None):
        """
        Get teacher's schedule.
        
        Args:
            day_of_week: Optional day filter (monday, tuesday, etc.)
            
        Returns:
            QuerySet: Schedule entries
        """
        from .schedule import Schedule
        
        queryset = Schedule.objects.filter(
            course__teacher=self,
            is_active=True
        )
        
        if day_of_week:
            queryset = queryset.filter(day_of_week=day_of_week)
        
        return queryset.order_by('day_of_week', 'start_time')
    
    def get_attendance_summary(self, start_date=None, end_date=None):
        """
        Get attendance summary for this teacher's courses.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            dict: Attendance statistics
        """
        from .attendance import Attendance
        
        queryset = Attendance.objects.filter(course__teacher=self)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        total = queryset.count()
        present = queryset.filter(status='present').count()
        absent = queryset.filter(status='absent').count()
        
        percentage = (present / total * 100) if total > 0 else 0
        
        return {
            'total_records': total,
            'present': present,
            'absent': absent,
            'percentage': round(percentage, 2)
        }
