"""
Grade model for student grades/marks.
"""

from django.db import models
from core.models import BaseModel


class Grade(BaseModel):
    """
    Grade record for a student in a course.
    """
    
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='grades'
    )
    
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='grades'
    )
    
    score = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5, blank=True)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    
    date = models.DateField()
    remarks = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student} - {self.course} - {self.score}"
    
    @property
    def is_passing(self):
        return self.score >= self.course.passing_score
    
    @property
    def percentage(self):
        if self.max_score > 0:
            return (self.score / self.max_score) * 100
        return 0
