"""
Academics domain services.
"""

from .student_service import StudentService
from .enrollment_service import EnrollmentService
from .attendance_service import AttendanceService
from .grade_service import GradeService

__all__ = [
    'StudentService',
    'EnrollmentService',
    'AttendanceService',
    'GradeService',
]
