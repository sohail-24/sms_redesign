"""
Role-based permission classes for DRF.
"""

from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission that only allows super admins.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_superuser
        )


class IsAdmin(permissions.BasePermission):
    """
    Permission that allows super admins and admins.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.has_role('admin')


class IsPrincipal(permissions.BasePermission):
    """
    Permission that allows super admins, admins, and principals.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser or request.user.has_role('admin'):
            return True
        
        return request.user.has_role('principal')


class IsTeacher(permissions.BasePermission):
    """
    Permission that allows teachers and above.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        allowed_roles = ['admin', 'principal', 'teacher']
        return any(request.user.has_role(role) for role in allowed_roles)


class IsAccountant(permissions.BasePermission):
    """
    Permission that allows accountants and above.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser or request.user.has_role('admin'):
            return True
        
        return request.user.has_role('accountant')


class IsStaff(permissions.BasePermission):
    """
    Permission that allows staff and above.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        allowed_roles = ['admin', 'principal', 'staff']
        return any(request.user.has_role(role) for role in allowed_roles)


class IsStudent(permissions.BasePermission):
    """
    Permission that allows students and above.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        allowed_roles = ['admin', 'principal', 'teacher', 'student']
        return any(request.user.has_role(role) for role in allowed_roles)


class IsStudentOwnerOrAdmin(permissions.BasePermission):
    """
    Permission that allows students to access only their own data,
    while admins can access all student data.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Super admins and admins have full access
        if request.user.is_superuser or request.user.has_role('admin'):
            return True
        
        # Teachers can access students in their courses
        if request.user.has_role('teacher'):
            from apps.academics.models import Course
            teacher_courses = Course.objects.filter(teacher=request.user.teacher_profile)
            return obj.enrollments.filter(course__in=teacher_courses).exists()
        
        # Students can only access their own data
        if request.user.has_role('student'):
            return obj.user == request.user
        
        return False


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Permission that allows teachers to access their own course data,
    while admins have full access.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser or request.user.has_role('admin'):
            return True
        
        return request.user.has_role('teacher')
    
    def has_object_permission(self, request, view, obj):
        # Super admins and admins have full access
        if request.user.is_superuser or request.user.has_role('admin'):
            return True
        
        # Teachers can only access their own course data
        if request.user.has_role('teacher'):
            if hasattr(obj, 'teacher'):
                return obj.teacher == request.user.teacher_profile
            if hasattr(obj, 'course'):
                return obj.course.teacher == request.user.teacher_profile
        
        return False


class ReadOnly(permissions.BasePermission):
    """
    Permission that only allows read-only access.
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission that allows owners full access, others read-only.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.user == request.user


class HasPermission(permissions.BasePermission):
    """
    Permission that checks for a specific permission codename.
    
    Usage:
        permission_classes = [IsAuthenticated, HasPermission('students.view')]
    """
    
    def __init__(self, codename):
        self.codename = codename
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.has_permission(self.codename)
