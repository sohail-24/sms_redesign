"""
Enrollment service for course enrollment business logic.
"""

from typing import List, Tuple
from django.db import transaction
from django.utils import timezone

from core.exceptions import BusinessLogicError, NotFoundError, DuplicateError
from ..models import StudentProfile, Course, Enrollment


class EnrollmentService:
    """
    Service class for enrollment-related business logic.
    """
    
    @staticmethod
    @transaction.atomic
    def enroll_student(
        student: StudentProfile,
        course: Course,
        enrolled_by=None
    ) -> Enrollment:
        """
        Enroll a student in a course.
        
        Args:
            student: Student to enroll
            course: Course to enroll in
            enrolled_by: User performing the enrollment (optional)
            
        Returns:
            Enrollment: Created enrollment
            
        Raises:
            BusinessLogicError: If enrollment is not allowed
            DuplicateError: If already enrolled
        """
        # Check if already enrolled
        existing = Enrollment.objects.filter(
            student=student,
            course=course
        ).first()
        
        if existing:
            if existing.status == Enrollment.STATUS_ACTIVE:
                raise DuplicateError("Student is already enrolled in this course")
            elif existing.status == Enrollment.STATUS_WITHDRAWN:
                # Re-enroll
                existing.status = Enrollment.STATUS_ACTIVE
                existing.enrollment_date = timezone.now().date()
                existing.save()
                return existing
            else:
                raise DuplicateError(f"Cannot enroll - current status: {existing.status}")
        
        # Check eligibility
        can_enroll, reason = course.can_student_enroll(student)
        if not can_enroll:
            raise BusinessLogicError(reason)
        
        # Create enrollment
        enrollment = Enrollment.objects.create(
            student=student,
            course=course,
            status=Enrollment.STATUS_ACTIVE,
            enrolled_by=enrolled_by
        )
        
        # Send notification
        from apps.notifications.tasks import send_enrollment_notification
        send_enrollment_notification.delay(enrollment.id)
        
        return enrollment
    
    @staticmethod
    @transaction.atomic
    def bulk_enroll(
        students: List[StudentProfile],
        course: Course,
        enrolled_by=None
    ) -> Tuple[List[Enrollment], List[dict]]:
        """
        Bulk enroll multiple students in a course.
        
        Args:
            students: List of students to enroll
            course: Course to enroll in
            enrolled_by: User performing the enrollment
            
        Returns:
            Tuple: (successful_enrollments, failed_enrollments)
        """
        successful = []
        failed = []
        
        for student in students:
            try:
                enrollment = EnrollmentService.enroll_student(
                    student=student,
                    course=course,
                    enrolled_by=enrolled_by
                )
                successful.append(enrollment)
            except Exception as e:
                failed.append({
                    'student_id': student.student_id,
                    'student_name': student.get_full_name(),
                    'error': str(e)
                })
        
        return successful, failed
    
    @staticmethod
    @transaction.atomic
    def withdraw_student(
        enrollment: Enrollment,
        reason: str = '',
        withdrawn_by=None
    ) -> Enrollment:
        """
        Withdraw a student from a course.
        
        Args:
            enrollment: Enrollment to withdraw
            reason: Reason for withdrawal
            withdrawn_by: User performing the withdrawal
            
        Returns:
            Enrollment: Updated enrollment
        """
        if enrollment.status != Enrollment.STATUS_ACTIVE:
            raise BusinessLogicError(f"Cannot withdraw - enrollment is {enrollment.status}")
        
        enrollment.withdraw(reason)
        
        # Create audit log
        from core.models import AuditLog
        AuditLog.log(
            user=withdrawn_by,
            action='UPDATE',
            instance=enrollment,
            previous_data={'status': Enrollment.STATUS_ACTIVE},
            new_data={'status': Enrollment.STATUS_WITHDRAWN, 'reason': reason}
        )
        
        return enrollment
    
    @staticmethod
    @transaction.atomic
    def complete_enrollment(
        enrollment: Enrollment,
        final_score: float = None,
        final_grade: str = '',
        completed_by=None
    ) -> Enrollment:
        """
        Mark enrollment as completed.
        
        Args:
            enrollment: Enrollment to complete
            final_score: Optional final score
            final_grade: Optional final grade
            completed_by: User completing the enrollment
            
        Returns:
            Enrollment: Updated enrollment
        """
        if enrollment.status != Enrollment.STATUS_ACTIVE:
            raise BusinessLogicError("Only active enrollments can be completed")
        
        enrollment.complete(final_score, final_grade)
        
        # Create audit log
        from core.models import AuditLog
        AuditLog.log(
            user=completed_by,
            action='UPDATE',
            instance=enrollment,
            previous_data={'status': Enrollment.STATUS_ACTIVE},
            new_data={
                'status': Enrollment.STATUS_COMPLETED,
                'final_score': final_score,
                'final_grade': final_grade
            }
        )
        
        return enrollment
    
    @staticmethod
    def get_enrollment_statistics(course: Course = None) -> dict:
        """
        Get enrollment statistics.
        
        Args:
            course: Optional course filter
            
        Returns:
            dict: Enrollment statistics
        """
        queryset = Enrollment.objects.all()
        
        if course:
            queryset = queryset.filter(course=course)
        
        total = queryset.count()
        active = queryset.filter(status=Enrollment.STATUS_ACTIVE).count()
        completed = queryset.filter(status=Enrollment.STATUS_COMPLETED).count()
        withdrawn = queryset.filter(status=Enrollment.STATUS_WITHDRAWN).count()
        dropped = queryset.filter(status=Enrollment.STATUS_DROPPED).count()
        pending = queryset.filter(status=Enrollment.STATUS_PENDING).count()
        
        return {
            'total': total,
            'active': active,
            'completed': completed,
            'withdrawn': withdrawn,
            'dropped': dropped,
            'pending': pending,
            'completion_rate': round((completed / total * 100), 2) if total > 0 else 0
        }
