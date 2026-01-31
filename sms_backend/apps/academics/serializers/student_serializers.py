"""
Student serializers.
"""

from rest_framework import serializers
from apps.auth_core.serializers import UserSerializer
from ..models import StudentProfile, ClassGroup


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Full student profile serializer.
    """
    user = UserSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    class_group_name = serializers.CharField(source='class_group.full_name', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'student_id', 'full_name', 'date_of_birth', 'age',
            'gender', 'photo', 'address', 'city', 'state', 'country', 'postal_code',
            'admission_date', 'class_group', 'class_group_name', 'roll_number',
            'status', 'graduation_date', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relation',
            'blood_group', 'allergies', 'medical_conditions',
            'previous_school', 'remarks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for student list views.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    class_group_name = serializers.CharField(source='class_group.full_name', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'student_id', 'full_name', 'email', 'gender',
            'class_group_name', 'roll_number', 'status', 'admission_date'
        ]


class StudentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new student.
    """
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=10)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = StudentProfile
        fields = [
            'student_id', 'email', 'password', 'first_name', 'last_name',
            'phone_number', 'date_of_birth', 'gender', 'admission_date',
            'class_group', 'roll_number', 'address', 'city', 'state',
            'postal_code', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation', 'blood_group', 'allergies',
            'medical_conditions', 'previous_school', 'remarks'
        ]
    
    def validate_student_id(self, value):
        """Validate student ID is unique."""
        if StudentProfile.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("Student ID already exists.")
        return value
    
    def validate_email(self, value):
        """Validate email is unique."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    
    def validate(self, data):
        """Validate class group has capacity."""
        class_group = data.get('class_group')
        if class_group and not class_group.can_add_student():
            raise serializers.ValidationError({
                'class_group': 'Class group is at full capacity.'
            })
        return data


class StudentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating student information.
    """
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    phone_number = serializers.CharField(source='user.phone_number', required=False)
    
    class Meta:
        model = StudentProfile
        fields = [
            'first_name', 'last_name', 'phone_number', 'address', 'city',
            'state', 'postal_code', 'class_group', 'roll_number',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation', 'blood_group', 'allergies',
            'medical_conditions', 'remarks'
        ]
    
    def validate_class_group(self, value):
        """Validate new class group has capacity."""
        instance = self.instance
        if value and instance and instance.class_group != value:
            if not value.can_add_student():
                raise serializers.ValidationError("New class group is at full capacity.")
        return value


class StudentDashboardSerializer(serializers.Serializer):
    """
    Serializer for student dashboard data.
    """
    student = serializers.DictField()
    courses = serializers.ListField()
    attendance = serializers.DictField()
    grades = serializers.DictField()
    upcoming_assignments = serializers.ListField()
    upcoming_exams = serializers.ListField()
