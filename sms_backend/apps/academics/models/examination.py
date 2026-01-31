"""
Examination and ExamSchedule models.
"""

from django.db import models
from core.models import BaseModel


class Examination(BaseModel):
    """
    Examination/exam record.
    """
    
    EXAM_TYPE_CHOICES = [
        ('midterm', 'Midterm'),
        ('final', 'Final'),
        ('quiz', 'Quiz'),
        ('other', 'Other'),
    ]
    
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='examinations'
    )
    
    title = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='other')
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title} ({self.course})"


class ExamSchedule(BaseModel):
    """
    Schedule for an examination.
    """
    
    examination = models.ForeignKey(
        Examination,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    
    class_group = models.ForeignKey(
        'ClassGroup',
        on_delete=models.CASCADE,
        related_name='exam_schedules'
    )
    
    room = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['examination__date']
    
    def __str__(self):
        return f"{self.examination} - {self.class_group}"
