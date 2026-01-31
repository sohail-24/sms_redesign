"""
Attendance model for tracking student attendance.
"""

from django.db import models
from django.core.exceptions import ValidationError
from core.models import BaseModel


class Attendance(BaseModel):
    """
    Attendance record for a student in a course.
    
    Features:
    - Tracks daily attendance
    - Supports multiple status types
    - Records who marked the attendance
    """
    
    # Status choices
    STATUS_PRESENT = 'present'
    STATUS_ABSENT = 'absent'
    STATUS_LATE = 'late'
    STATUS_EXCUSED = 'excused'
    STATUS_ON_LEAVE = 'on_leave'
    
    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Present'),
        (STATUS_ABSENT, 'Absent'),
        (STATUS_LATE, 'Late'),
        (STATUS_EXCUSED, 'Excused'),
        (STATUS_ON_LEAVE, 'On Leave'),
    ]
    
    # Relationships
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    
    # Attendance details
    date = models.DateField(db_index=True)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PRESENT,
        db_index=True
    )
    
    # For late arrivals
    arrival_time = models.TimeField(null=True, blank=True)
    
    # Remarks
    remarks = models.TextField(
        blank=True,
        help_text="Reason for absence/late arrival"
    )
    
    # Who marked the attendance
    marked_by = models.ForeignKey(
        'auth_core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_marked'
    )
    
    # For bulk operations
    is_bulk_entry = models.BooleanField(
        default=False,
        help_text="Whether this was a bulk entry"
    )
    
    class Meta:
        ordering = ['-date', 'course']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
        unique_together = ['student', 'course', 'date']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['course', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.course} - {self.date} - {self.get_status_display()}"
    
    def clean(self):
        """Validate attendance record."""
        super().clean()
        
        # Check if student is enrolled in the course
        from .enrollment import Enrollment
        if not Enrollment.objects.filter(
            student=self.student,
            course=self.course,
            status=Enrollment.STATUS_ACTIVE
        ).exists():
            raise ValidationError("Student is not enrolled in this course")
        
        # Late status requires arrival time
        if self.status == self.STATUS_LATE and not self.arrival_time:
            raise ValidationError("Arrival time is required for late status")
    
    def save(self, *args, **kwargs):
        """Save with validation."""
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def is_present(self):
        """Check if student was present."""
        return self.status in [self.STATUS_PRESENT, self.STATUS_LATE]
    
    @property
    def is_absent(self):
        """Check if student was absent."""
        return self.status == self.STATUS_ABSENT
    
    @classmethod
    def get_summary(cls, student=None, course=None, start_date=None, end_date=None):
        """
        Get attendance summary.
        
        Args:
            student: Optional student filter
            course: Optional course filter
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            dict: Attendance summary
        """
        queryset = cls.objects.all()
        
        if student:
            queryset = queryset.filter(student=student)
        if course:
            queryset = queryset.filter(course=course)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        total = queryset.count()
        present = queryset.filter(status=cls.STATUS_PRESENT).count()
        absent = queryset.filter(status=cls.STATUS_ABSENT).count()
        late = queryset.filter(status=cls.STATUS_LATE).count()
        excused = queryset.filter(status=cls.STATUS_EXCUSED).count()
        
        effective_present = present + late + excused
        percentage = (effective_present / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'percentage': round(percentage, 2)
        }
