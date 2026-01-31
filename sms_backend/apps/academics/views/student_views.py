"""
Student API views.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsAdmin, IsTeacher, IsStudentOwnerOrAdmin
from ..models import StudentProfile
from ..serializers import (
    StudentProfileSerializer,
    StudentListSerializer,
    StudentCreateSerializer,
    StudentUpdateSerializer,
    StudentDashboardSerializer,
)
from ..services import StudentService


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for student management.
    
    Provides CRUD operations for students with role-based access control.
    """
    
    queryset = StudentProfile.objects.filter(deleted_at__isnull=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'gender', 'class_group', 'admission_date']
    search_fields = ['student_id', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['created_at', 'student_id', 'user__first_name', 'admission_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return StudentListSerializer
        elif self.action == 'create':
            return StudentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return StudentUpdateSerializer
        return StudentProfileSerializer
    
    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdmin]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsStudentOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated, IsTeacher]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        
        # Super admins see all
        if user.is_superuser:
            return self.queryset
        
        # Teachers see students in their courses
        if user.has_role('teacher'):
            from ..models import Course
            teacher_courses = Course.objects.filter(teacher=user.teacher_profile)
            return self.queryset.filter(
                enrollments__course__in=teacher_courses
            ).distinct()
        
        # Students see only themselves
        if user.has_role('student'):
            return self.queryset.filter(user=user)
        
        return self.queryset
    
    def create(self, request, *args, **kwargs):
        """Create a new student with user account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            student = StudentService.create_student(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                student_id=serializer.validated_data['student_id'],
                date_of_birth=serializer.validated_data['date_of_birth'],
                gender=serializer.validated_data['gender'],
                admission_date=serializer.validated_data['admission_date'],
                class_group_id=serializer.validated_data.get('class_group'),
                **{
                    k: v for k, v in serializer.validated_data.items()
                    if k not in ['email', 'password', 'first_name', 'last_name', 
                                'student_id', 'date_of_birth', 'gender', 
                                'admission_date', 'class_group']
                }
            )
            
            response_serializer = StudentProfileSerializer(student)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """Update student information."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            student = StudentService.update_student(
                student=instance,
                updated_by=request.user,
                **serializer.validated_data
            )
            
            response_serializer = StudentProfileSerializer(student)
            return Response(response_serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete a student."""
        instance = self.get_object()
        instance.soft_delete(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get student dashboard data."""
        student = self.get_object()
        
        # Check permission
        if not (request.user.is_superuser or 
                request.user.has_role('teacher') or
                student.user == request.user):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = StudentService.get_student_dashboard_data(student)
        serializer = StudentDashboardSerializer(data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Get student attendance summary."""
        student = self.get_object()
        
        from ..services import AttendanceService
        summary = AttendanceService.get_student_attendance_summary(student)
        
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def grades(self, request, pk=None):
        """Get student grades."""
        student = self.get_object()
        
        from ..models import Grade
        grades = Grade.objects.filter(student=student).select_related('course')
        
        data = [{
            'id': g.id,
            'course': g.course.title,
            'score': g.score,
            'grade': g.grade,
            'date': g.date,
            'remarks': g.remarks
        } for g in grades]
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        """Get student's enrolled courses."""
        student = self.get_object()
        
        enrollments = student.enrollments.filter(status='active').select_related('course')
        
        data = [{
            'id': e.course.id,
            'code': e.course.course_code,
            'title': e.course.title,
            'teacher': e.course.teacher.get_full_name() if e.course.teacher else None,
            'progress': e.progress_percentage,
            'enrollment_date': e.enrollment_date
        } for e in enrollments]
        
        return Response(data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsTeacher])
    def low_attendance(self, request):
        """Get students with low attendance."""
        from ..services import AttendanceService
        
        threshold = request.query_params.get('threshold', 75)
        try:
            threshold = float(threshold)
        except ValueError:
            threshold = 75.0
        
        students = AttendanceService.get_low_attendance_students(threshold=threshold)
        return Response(students)
