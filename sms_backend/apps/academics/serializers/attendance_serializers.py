"""
Attendance serializers.
"""

from rest_framework import serializers
from ..models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Attendance serializer.
    """
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_name', 'course', 'course_title',
            'date', 'status', 'arrival_time', 'remarks', 'marked_by'
        ]
        read_only_fields = ['id']


class BulkAttendanceSerializer(serializers.Serializer):
    """
    Serializer for bulk attendance marking.
    """
    course_id = serializers.IntegerField()
    date = serializers.DateField()
    attendance_data = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
