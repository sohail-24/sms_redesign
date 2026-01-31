"""
Enrollment serializers.
"""

from rest_framework import serializers
from ..models import Enrollment


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Enrollment serializer.
    """
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_name', 'course', 'course_title',
            'course_code', 'enrollment_date', 'status', 'completion_date',
            'final_grade', 'final_score', 'progress_percentage', 'notes'
        ]
        read_only_fields = ['id', 'enrollment_date']


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating enrollments.
    """
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'notes']
