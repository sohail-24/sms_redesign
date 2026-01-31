"""
Enrollment model for student-course relationships.
"""

from django.db import models
from django.core.exceptions import ValidationError
from core.models import BaseModel


class Enrollment(BaseModel):
    """
    Represents a student's enrollment in a course.
    
    Features:
    - Tracks enrollment status
    - Records enrollment date and completion
    - Supports grade/result tracking
    """
    
    # Status choices
    STATUS_PENDING = 'pending'
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_DROPPED = 'dropped'
    STATUS_WITHDRAWN = 'withdrawn'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_DROPPED, 'Dropped'),
        (STATUS_WITHDRAWN, 'Withdrawn'),
    ]
    
    # Relationships
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    # Enrollment details
    enrollment_date = models.DateField(auto_now_add=True)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )
    
    # Completion details
    completion_date = models.DateField(null=True, blank=True)
    final_grade = models.CharField(max_length=5, blank=True)
    final_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Who enrolled the student
    enrolled_by = models.ForeignKey(
        'auth_core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrollments_made'
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-enrollment_date']
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', 'status']),
            models.Index(fields=['enrollment_date']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.course}"
    
    def clean(self):
        """Validate enrollment."""
        super().clean()
        
        # Check if student and course are active
        if not self.student.is_active_student:
            raise ValidationError("Student is not active")
        
        if not self.course.is_active:
            raise ValidationError("Course is not active")
        
        # Check capacity only for new enrollments
        if self._state.adding and self.course.is_full:
            raise ValidationError("Course is at full capacity")
    
    def save(self, *args, **kwargs):
        """Save with validation."""
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def is_active_enrollment(self):
        """Check if enrollment is currently active."""
        return self.status == self.STATUS_ACTIVE
    
    @property
    def is_completed(self):
        """Check if enrollment is completed."""
        return self.status == self.STATUS_COMPLETED
    
    @property
    def progress_percentage(self):
        """Get student's progress in this course."""
        return self.course.get_student_progress(self.student)
    
    def complete(self, final_score=None, final_grade=None):
        """
        Mark enrollment as completed.
        
        Args:
            final_score: Optional final score
            final_grade: Optional final grade
        """
        from django.utils import timezone
        
        self.status = self.STATUS_COMPLETED
        self.completion_date = timezone.now().date()
        
        if final_score is not None:
            self.final_score = final_score
        if final_grade:
            self.final_grade = final_grade
        
        self.save(update_fields=['status', 'completion_date', 'final_score', 'final_grade'])
    
    def withdraw(self, reason=''):
        """
        Withdraw from the course.
        
        Args:
            reason: Optional reason for withdrawal
        """
        self.status = self.STATUS_WITHDRAWN
        if reason:
            self.notes = f"Withdrawn: {reason}"
        self.save(update_fields=['status', 'notes'])
