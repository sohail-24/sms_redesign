"""
Schedule/Timetable model.
"""

from django.db import models
from core.models import BaseModel


class Schedule(BaseModel):
    """
    Class schedule/timetable entry.
    """
    
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    room = models.CharField(max_length=50, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.course} - {self.get_day_of_week_display()} {self.start_time}"
