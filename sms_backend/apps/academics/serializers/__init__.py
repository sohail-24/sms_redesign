"""
Academics domain serializers.
"""

from .student_serializers import (
    StudentProfileSerializer,
    StudentCreateSerializer,
    StudentUpdateSerializer,
    StudentListSerializer,
    StudentDashboardSerializer,
)
from .course_serializers import (
    CourseSerializer,
    CourseListSerializer,
    CourseDetailSerializer,
)
from .enrollment_serializers import (
    EnrollmentSerializer,
    EnrollmentCreateSerializer,
)
from .attendance_serializers import (
    AttendanceSerializer,
    BulkAttendanceSerializer,
)

__all__ = [
    'StudentProfileSerializer',
    'StudentCreateSerializer',
    'StudentUpdateSerializer',
    'StudentListSerializer',
    'StudentDashboardSerializer',
    'CourseSerializer',
    'CourseListSerializer',
    'CourseDetailSerializer',
    'EnrollmentSerializer',
    'EnrollmentCreateSerializer',
    'AttendanceSerializer',
    'BulkAttendanceSerializer',
]
