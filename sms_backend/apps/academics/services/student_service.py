"""
Student service for business logic encapsulation.
"""

from typing import Optional, Dict, List
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.auth_core.models import Role, UserRole
from core.exceptions import BusinessLogicError, NotFoundError, DuplicateError
from ..models import StudentProfile, ClassGroup

User = get_user_model()


class StudentService:
    """
    Service class for student-related business logic.
    
    All student operations should go through this service to ensure:
    - Business rules are enforced
    - Transactions are atomic
    - Audit logs are created
    - Notifications are sent
    """
    
    @staticmethod
    @transaction.atomic
    def create_student(
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        student_id: str,
        date_of_birth,
        gender: str,
        admission_date,
        class_group_id: Optional[int] = None,
        **additional_data
    ) -> StudentProfile:
        """
        Create a new student with user account.
        
        Args:
            email: Student's email address
            password: Initial password
            first_name, last_name: Student's name
            student_id: Unique student ID
            date_of_birth: Date of birth
            gender: Gender choice
            admission_date: Admission date
            class_group_id: Optional class group ID
            **additional_data: Additional student fields
            
        Returns:
            StudentProfile: Created student profile
            
        Raises:
            DuplicateError: If student ID or email already exists
            ValidationError: If data is invalid
        """
        # Validate unique constraints
        if User.objects.filter(email=email).exists():
            raise DuplicateError(f"User with email {email} already exists")
        
        if StudentProfile.objects.filter(student_id=student_id).exists():
            raise DuplicateError(f"Student ID {student_id} already exists")
        
        # Get class group if provided
        class_group = None
        if class_group_id:
            try:
                class_group = ClassGroup.objects.get(id=class_group_id)
                if not class_group.can_add_student():
                    raise BusinessLogicError("Class group is at full capacity")
            except ClassGroup.DoesNotExist:
                raise NotFoundError(f"Class group with ID {class_group_id} not found")
        
        # Create user account
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=additional_data.get('phone_number', '')
        )
        
        # Assign student role
        student_role, _ = Role.objects.get_or_create(
            name=Role.STUDENT,
            defaults={'description': 'Student', 'level': 1}
        )
        UserRole.objects.create(user=user, role=student_role, is_primary=True)
        
        # Create student profile
        student = StudentProfile.objects.create(
            user=user,
            student_id=student_id,
            date_of_birth=date_of_birth,
            gender=gender,
            admission_date=admission_date,
            class_group=class_group,
            address=additional_data.get('address', ''),
            city=additional_data.get('city', ''),
            state=additional_data.get('state', ''),
            postal_code=additional_data.get('postal_code', ''),
            roll_number=additional_data.get('roll_number', ''),
            emergency_contact_name=additional_data.get('emergency_contact_name', ''),
            emergency_contact_phone=additional_data.get('emergency_contact_phone', ''),
            emergency_contact_relation=additional_data.get('emergency_contact_relation', ''),
            blood_group=additional_data.get('blood_group', ''),
            allergies=additional_data.get('allergies', ''),
            medical_conditions=additional_data.get('medical_conditions', ''),
            previous_school=additional_data.get('previous_school', ''),
            remarks=additional_data.get('remarks', '')
        )
        
        # Send welcome email (async)
        from apps.notifications.tasks import send_welcome_email
        send_welcome_email.delay(user.id)
        
        return student
    
    @staticmethod
    def get_student(student_id: str) -> StudentProfile:
        """
        Get student by student ID.
        
        Args:
            student_id: Student's unique ID
            
        Returns:
            StudentProfile
            
        Raises:
            NotFoundError: If student not found
        """
        try:
            return StudentProfile.objects.select_related('user', 'class_group').get(
                student_id=student_id,
                deleted_at__isnull=True
            )
        except StudentProfile.DoesNotExist:
            raise NotFoundError(f"Student with ID {student_id} not found")
    
    @staticmethod
    @transaction.atomic
    def update_student(
        student: StudentProfile,
        updated_by: User,
        **data
    ) -> StudentProfile:
        """
        Update student information.
        
        Args:
            student: StudentProfile instance
            updated_by: User making the update
            **data: Fields to update
            
        Returns:
            StudentProfile: Updated student
        """
        # Track changes for audit
        old_data = {
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'phone_number': student.user.phone_number,
            'address': student.address,
            'class_group_id': student.class_group_id,
        }
        
        # Update user fields
        user_fields = ['first_name', 'last_name', 'phone_number']
        for field in user_fields:
            if field in data:
                setattr(student.user, field, data[field])
        student.user.save()
        
        # Update student fields
        student_fields = [
            'address', 'city', 'state', 'postal_code',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation', 'blood_group', 'allergies',
            'medical_conditions', 'remarks'
        ]
        for field in student_fields:
            if field in data:
                setattr(student, field, data[field])
        
        # Handle class group change
        if 'class_group_id' in data:
            new_class_group = None
            if data['class_group_id']:
                try:
                    new_class_group = ClassGroup.objects.get(id=data['class_group_id'])
                    if not new_class_group.can_add_student():
                        raise BusinessLogicError("New class group is at full capacity")
                except ClassGroup.DoesNotExist:
                    raise NotFoundError(f"Class group not found")
            student.class_group = new_class_group
        
        student.save()
        
        # Create audit log
        from core.models import AuditLog
        new_data = {
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'phone_number': student.user.phone_number,
            'address': student.address,
            'class_group_id': student.class_group_id,
        }
        AuditLog.log(
            user=updated_by,
            action='UPDATE',
            instance=student,
            previous_data=old_data,
            new_data=new_data
        )
        
        return student
    
    @staticmethod
    @transaction.atomic
    def transfer_student(
        student: StudentProfile,
        new_class_group: ClassGroup,
        transferred_by: User,
        reason: str = ''
    ) -> StudentProfile:
        """
        Transfer student to a new class group.
        
        Args:
            student: Student to transfer
            new_class_group: Destination class group
            transferred_by: User performing the transfer
            reason: Optional reason for transfer
            
        Returns:
            StudentProfile: Updated student
        """
        if not new_class_group.can_add_student():
            raise BusinessLogicError("Destination class is at full capacity")
        
        old_class = student.class_group
        student.class_group = new_class_group
        student.remarks = f"{student.remarks}\nTransferred from {old_class} to {new_class_group} on {timezone.now().date()}. Reason: {reason}"
        student.save()
        
        # Create audit log
        from core.models import AuditLog
        AuditLog.log(
            user=transferred_by,
            action='UPDATE',
            instance=student,
            previous_data={'class_group_id': old_class.id if old_class else None},
            new_data={'class_group_id': new_class_group.id}
        )
        
        return student
    
    @staticmethod
    def get_student_dashboard_data(student: StudentProfile) -> Dict:
        """
        Get all data needed for student dashboard.
        
        Args:
            student: StudentProfile instance
            
        Returns:
            dict: Dashboard data
        """
        from ..models import Assignment, Examination
        
        # Get enrolled courses with progress
        enrollments = student.enrollments.filter(status='active').select_related('course')
        courses_data = []
        for enrollment in enrollments:
            courses_data.append({
                'id': enrollment.course.id,
                'code': enrollment.course.course_code,
                'title': enrollment.course.title,
                'progress': enrollment.progress_percentage,
                'teacher': enrollment.course.teacher.get_full_name() if enrollment.course.teacher else None,
            })
        
        # Get attendance summary
        attendance_summary = student.get_attendance_summary()
        
        # Get grade summary
        grade_summary = student.get_grade_summary()
        
        # Get upcoming assignments
        from django.utils import timezone
        upcoming_assignments = Assignment.objects.filter(
            course__enrollments__student=student,
            due_date__gte=timezone.now(),
            is_active=True
        ).order_by('due_date')[:5]
        
        # Get upcoming exams
        upcoming_exams = Examination.objects.filter(
            course__enrollments__student=student,
            date__gte=timezone.now(),
            is_active=True
        ).order_by('date')[:5]
        
        return {
            'student': {
                'id': student.student_id,
                'name': student.get_full_name(),
                'email': student.email,
                'class_group': student.class_group.full_name if student.class_group else None,
                'roll_number': student.roll_number,
            },
            'courses': courses_data,
            'attendance': attendance_summary,
            'grades': grade_summary,
            'upcoming_assignments': [
                {
                    'id': a.id,
                    'title': a.title,
                    'course': a.course.title,
                    'due_date': a.due_date,
                } for a in upcoming_assignments
            ],
            'upcoming_exams': [
                {
                    'id': e.id,
                    'title': e.title,
                    'course': e.course.title,
                    'date': e.date,
                } for e in upcoming_exams
            ],
        }
