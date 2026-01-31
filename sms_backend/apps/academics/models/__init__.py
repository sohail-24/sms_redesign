"""
Academics domain models.
"""

from .class_group import ClassGroup
from .course import Course
from .student_profile import StudentProfile
from .teacher_profile import TeacherProfile
from .enrollment import Enrollment
from .attendance import Attendance
from .grade import Grade
from .assignment import Assignment, Submission
from .schedule import Schedule
from .examination import Examination, ExamSchedule

__all__ = [
    'ClassGroup',
    'Course',
    'StudentProfile',
    'TeacherProfile',
    'Enrollment',
    'Attendance',
    'Grade',
    'Assignment',
    'Submission',
    'Schedule',
    'Examination',
    'ExamSchedule',
]
