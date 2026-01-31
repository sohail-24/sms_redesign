"""
Course serializers.
"""

from rest_framework import serializers
from ..models import Course


class CourseSerializer(serializers.ModelSerializer):
    """
    Full course serializer.
    """
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    enrolled_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'title', 'description', 'credits',
            'teacher', 'teacher_name', 'class_group', 'max_students',
            'enrolled_count', 'start_date', 'end_date', 'is_active',
            'passing_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for course list views.
    """
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'title', 'credits',
            'teacher_name', 'is_active'
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Detailed course serializer with related data.
    """
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    enrolled_count = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'title', 'description', 'credits',
            'teacher', 'teacher_name', 'class_group', 'max_students',
            'enrolled_count', 'available_seats', 'start_date', 'end_date',
            'is_active', 'passing_score', 'created_at', 'updated_at'
        ]
