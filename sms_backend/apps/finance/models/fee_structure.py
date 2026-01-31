"""
Fee Structure model - Placeholder for future implementation.
"""

from django.db import models
from core.models import BaseModel, SoftDeleteModel


class FeeStructure(BaseModel, SoftDeleteModel):
    """
    Fee structure template for courses/classes.
    Placeholder for future implementation.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'

    def __str__(self):
        return self.name
