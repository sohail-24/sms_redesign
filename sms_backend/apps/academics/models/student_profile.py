"""
Student Profile model.
"""

from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from core.models import BaseModel, SoftDeleteModel

User = get_user_model()


class StudentProfile(BaseModel, SoftDeleteModel):
    """
    Extended profile for student users.
    
    This model contains student-specific information separate from the
    base User model to maintain clean separation of concerns.
    
    Features:
    - Student ID (unique identifier)
    - Personal information
    - Academic information
    - Guardian information
    - Status tracking
    """
    
    # Status choices
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_GRADUATED = 'graduated'
    STATUS_SUSPENDED = 'suspended'
    STATUS_TRANSFERRED = 'transferred'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_GRADUATED, 'Graduated'),
        (STATUS_SUSPENDED, 'Suspended'),
        (STATUS_TRANSFERRED, 'Transferred'),
    ]
    
    # Gender choices
    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'
    GENDER_OTHER = 'other'
    
    GENDER_CHOICES = [
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    ]
    
    # Link to User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    
    # Student ID (unique identifier for the school)
    student_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique student ID assigned by the school"
    )
    
    # Personal information
    date_of_birth = models.DateField()
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )
    
    photo = models.ImageField(
        upload_to='student_photos/%Y/%m/',
        blank=True,
        null=True
    )
    
    # Contact information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default='India')
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Academic information
    admission_date = models.DateField()
    
    class_group = models.ForeignKey(
        'ClassGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    
    roll_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Roll number within the class"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        db_index=True
    )
    
    # Graduation/Leaving information
    graduation_date = models.DateField(null=True, blank=True)
    leaving_reason = models.TextField(blank=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    
    # Medical information
    blood_group = models.CharField(max_length=10, blank=True)
    allergies = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)
    
    # Additional info
    previous_school = models.CharField(max_length=200, blank=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['status']),
            models.Index(fields=['class_group']),
            models.Index(fields=['admission_date']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.student_id})"
    
    @property
    def full_name(self):
        """Return student's full name."""
        return self.user.get_full_name()
    
    def get_full_name(self):
        """Return student's full name (alias for full_name)."""
        return self.full_name
    
    @property
    def email(self):
        """Return student's email."""
        return self.user.email
    
    @property
    def phone_number(self):
        """Return student's phone number."""
        return self.user.phone_number
    
    @property
    def is_active_student(self):
        """Check if student is currently active."""
        return self.status == self.STATUS_ACTIVE
    
    @property
    def age(self):
        """Calculate student's age."""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def enrolled_courses(self):
        """Get all courses the student is enrolled in."""
        from .enrollment import Enrollment
        return Course.objects.filter(
            enrollments__student=self,
            enrollments__status='active'
        )
    
    def get_attendance_summary(self, course=None, start_date=None, end_date=None):
        """
        Get attendance summary for the student.
        
        Args:
            course: Optional course filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            dict: Attendance statistics
        """
        from .attendance import Attendance
        
        queryset = Attendance.objects.filter(student=self)
        
        if course:
            queryset = queryset.filter(course=course)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        total = queryset.count()
        present = queryset.filter(status='present').count()
        absent = queryset.filter(status='absent').count()
        late = queryset.filter(status='late').count()
        excused = queryset.filter(status='excused').count()
        
        percentage = (present / total * 100) if total > 0 else 0
        
        return {
            'total_classes': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'percentage': round(percentage, 2)
        }
    
    def get_grade_summary(self, course=None):
        """
        Get grade summary for the student.
        
        Args:
            course: Optional course filter
            
        Returns:
            dict: Grade statistics
        """
        from .grade import Grade
        
        queryset = Grade.objects.filter(student=self)
        
        if course:
            queryset = queryset.filter(course=course)
        
        grades = list(queryset)
        
        if not grades:
            return {
                'total_grades': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
                'pass_rate': 0
            }
        
        scores = [g.score for g in grades]
        passing = sum(1 for g in grades if g.is_passing)
        
        return {
            'total_grades': len(grades),
            'average_score': round(sum(scores) / len(scores), 2),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'pass_rate': round((passing / len(grades) * 100), 2)
        }


# Import Course here to avoid circular import
from .course import Course
