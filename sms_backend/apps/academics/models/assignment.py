"""
Assignment and Submission models.
"""

from django.db import models
from core.models import BaseModel


class Assignment(BaseModel):
    """
    Assignment given to students in a course.
    """
    
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    due_date = models.DateTimeField()
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.title} ({self.course})"


class Submission(BaseModel):
    """
    Student submission for an assignment.
    """
    
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='submissions/%Y/%m/', blank=True, null=True)
    
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student} - {self.assignment}"
