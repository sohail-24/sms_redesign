"""
Class/Grade and Section model.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel, SoftDeleteModel


class ClassGroup(BaseModel, SoftDeleteModel):
    """
    Represents a class/grade with section (e.g., "Grade 10 - Section A").
    
    This model handles:
    - Class/grade levels (1-12, or custom)
    - Sections (A, B, C, etc.)
    - Academic year
    - Capacity management
    """
    
    # Grade/Class level
    grade_level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Grade level (1-12)"
    )
    
    # Section (A, B, C, etc.)
    section = models.CharField(max_length=10)
    
    # Academic year (e.g., "2024-2025")
    academic_year = models.CharField(max_length=20)
    
    # Capacity
    max_students = models.PositiveSmallIntegerField(
        default=40,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    
    # Class teacher
    class_teacher = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_classes'
    )
    
    # Room assignment
    room_number = models.CharField(max_length=20, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-academic_year', 'grade_level', 'section']
        verbose_name = 'Class Group'
        verbose_name_plural = 'Class Groups'
        unique_together = ['grade_level', 'section', 'academic_year']
        indexes = [
            models.Index(fields=['grade_level', 'section']),
            models.Index(fields=['academic_year']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Grade {self.grade_level} - Section {self.section} ({self.academic_year})"
    
    @property
    def full_name(self):
        """Return the full class name."""
        return f"Grade {self.grade_level} - Section {self.section}"
    
    @property
    def current_students_count(self):
        """Get the number of currently enrolled students."""
        return self.students.filter(status='active').count()
    
    @property
    def available_seats(self):
        """Get the number of available seats."""
        return self.max_students - self.current_students_count
    
    @property
    def is_full(self):
        """Check if the class is at full capacity."""
        return self.current_students_count >= self.max_students
    
    @property
    def has_capacity(self):
        """Check if the class has available capacity."""
        return not self.is_full
    
    def can_add_student(self):
        """Check if a new student can be added to this class."""
        return self.is_active and self.has_capacity
