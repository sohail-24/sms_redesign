"""
Course/Subject model.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel, SoftDeleteModel


class Course(BaseModel, SoftDeleteModel):
    """
    Represents a course/subject offered by the school.
    
    Features:
    - Unique course code
    - Credit hours
    - Assigned teacher
    - Class group association
    - Capacity management
    - Prerequisites support
    """
    
    # Course identification
    course_code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique course code (e.g., 'MATH101')"
    )
    
    title = models.CharField(max_length=200)
    
    description = models.TextField(blank=True)
    
    # Academic details
    credits = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Credit hours for this course"
    )
    
    # Relationships
    teacher = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )
    
    class_group = models.ForeignKey(
        'ClassGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )
    
    # Prerequisites (self-referencing many-to-many)
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='prerequisite_for',
        help_text="Courses that must be completed before enrolling"
    )
    
    # Capacity
    max_students = models.PositiveSmallIntegerField(
        default=40,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    
    # Duration
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Grading scheme
    passing_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=60.00,
        help_text="Minimum score to pass this course"
    )
    
    class Meta:
        ordering = ['course_code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        indexes = [
            models.Index(fields=['course_code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['teacher']),
            models.Index(fields=['class_group']),
        ]
    
    def __str__(self):
        return f"{self.course_code} - {self.title}"
    
    @property
    def enrolled_count(self):
        """Get the number of enrolled students."""
        return self.enrollments.filter(status='active').count()
    
    @property
    def available_seats(self):
        """Get the number of available seats."""
        return self.max_students - self.enrolled_count
    
    @property
    def is_full(self):
        """Check if the course is at full capacity."""
        return self.enrolled_count >= self.max_students
    
    @property
    def has_capacity(self):
        """Check if the course has available capacity."""
        return not self.is_full
    
    @property
    def is_available_for_enrollment(self):
        """Check if course is available for new enrollments."""
        return self.is_active and self.has_capacity and self.teacher and self.teacher.is_active
    
    def can_student_enroll(self, student):
        """
        Check if a specific student can enroll in this course.
        
        Args:
            student: StudentProfile instance
            
        Returns:
            tuple: (can_enroll: bool, reason: str)
        """
        from .enrollment import Enrollment
        
        # Check if already enrolled
        if Enrollment.objects.filter(student=student, course=self, status='active').exists():
            return False, "Already enrolled in this course"
        
        # Check if course is active
        if not self.is_active:
            return False, "Course is not active"
        
        # Check if teacher is active
        if not self.teacher or not self.teacher.is_active:
            return False, "Course has no active teacher"
        
        # Check capacity
        if self.is_full:
            return False, "Course is at full capacity"
        
        # Check prerequisites
        unmet_prereqs = self.prerequisites.exclude(
            enrollments__student=student,
            enrollments__status='completed'
        )
        if unmet_prereqs.exists():
            prereq_names = ", ".join([p.title for p in unmet_prereqs])
            return False, f"Prerequisites not met: {prereq_names}"
        
        # Check class group match (if specified)
        if self.class_group and student.class_group != self.class_group:
            return False, "Course is not available for your class"
        
        return True, "Eligible for enrollment"
    
    def get_student_progress(self, student):
        """
        Calculate progress percentage for a specific student.
        
        Args:
            student: StudentProfile instance
            
        Returns:
            float: Progress percentage (0-100)
        """
        from .assignment import Assignment, Submission
        from .attendance import Attendance
        
        # Get all assignments for this course
        assignments = Assignment.objects.filter(course=self)
        total_assignments = assignments.count()
        
        if total_assignments == 0:
            return 0.0
        
        # Count submitted assignments
        submitted = Submission.objects.filter(
            assignment__in=assignments,
            student=student
        ).count()
        
        # Calculate attendance rate
        attendance_records = Attendance.objects.filter(
            course=self,
            student=student
        )
        total_classes = attendance_records.count()
        present_classes = attendance_records.filter(status='present').count()
        attendance_rate = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        # Weighted progress: 60% assignments, 40% attendance
        assignment_progress = (submitted / total_assignments * 100) if total_assignments > 0 else 0
        progress = (assignment_progress * 0.6) + (attendance_rate * 0.4)
        
        return round(progress, 2)
