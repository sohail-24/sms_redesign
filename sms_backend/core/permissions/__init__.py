"""
Core permissions module.
"""

from .role_permissions import (
    IsSuperAdmin,
    IsAdmin,
    IsPrincipal,
    IsTeacher,
    IsStudent,
    IsAccountant,
    IsStaff,
    IsStudentOwnerOrAdmin,
    IsTeacherOrAdmin,
    ReadOnly,
)

__all__ = [
    'IsSuperAdmin',
    'IsAdmin',
    'IsPrincipal',
    'IsTeacher',
    'IsStudent',
    'IsAccountant',
    'IsStaff',
    'IsStudentOwnerOrAdmin',
    'IsTeacherOrAdmin',
    'ReadOnly',
]
