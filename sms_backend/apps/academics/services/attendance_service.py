"""
Attendance service for attendance tracking business logic.
"""

from typing import List, Dict, Optional
from datetime import date, timedelta
from django.db import transaction
from django.utils import timezone

from core.exceptions import BusinessLogicError, NotFoundError
from ..models import StudentProfile, Course, Attendance, Enrollment


class AttendanceService:
    """
    Service class for attendance-related business logic.
    """
    
    @staticmethod
    @transaction.atomic
    def mark_attendance(
        student: StudentProfile,
        course: Course,
        attendance_date: date,
        status: str,
        marked_by=None,
        remarks: str = '',
        arrival_time=None
    ) -> Attendance:
        """
        Mark attendance for a student.
        
        Args:
            student: Student to mark attendance for
            course: Course
            attendance_date: Date of attendance
            status: Attendance status
            marked_by: User marking the attendance
            remarks: Optional remarks
            arrival_time: Optional arrival time (for late status)
            
        Returns:
            Attendance: Created/updated attendance record
        """
        # Verify student is enrolled
        if not Enrollment.objects.filter(
            student=student,
            course=course,
            status=Enrollment.STATUS_ACTIVE
        ).exists():
            raise BusinessLogicError("Student is not enrolled in this course")
        
        # Get or create attendance record
        attendance, created = Attendance.objects.update_or_create(
            student=student,
            course=course,
            date=attendance_date,
            defaults={
                'status': status,
                'marked_by': marked_by,
                'remarks': remarks,
                'arrival_time': arrival_time
            }
        )
        
        return attendance
    
    @staticmethod
    @transaction.atomic
    def bulk_mark_attendance(
        course: Course,
        attendance_date: date,
        attendance_data: List[Dict],
        marked_by=None
    ) -> Dict:
        """
        Mark attendance for multiple students at once.
        
        Args:
            course: Course
            attendance_date: Date of attendance
            attendance_data: List of dicts with 'student_id', 'status', 'remarks'
            marked_by: User marking the attendance
            
        Returns:
            dict: Summary of operation
        """
        successful = []
        failed = []
        
        for data in attendance_data:
            try:
                student_id = data.get('student_id')
                status = data.get('status')
                remarks = data.get('remarks', '')
                arrival_time = data.get('arrival_time')
                
                try:
                    student = StudentProfile.objects.get(student_id=student_id)
                except StudentProfile.DoesNotExist:
                    failed.append({'student_id': student_id, 'error': 'Student not found'})
                    continue
                
                AttendanceService.mark_attendance(
                    student=student,
                    course=course,
                    attendance_date=attendance_date,
                    status=status,
                    marked_by=marked_by,
                    remarks=remarks,
                    arrival_time=arrival_time
                )
                successful.append(student_id)
                
            except Exception as e:
                failed.append({'student_id': student_id, 'error': str(e)})
        
        return {
            'total': len(attendance_data),
            'successful': len(successful),
            'failed': len(failed),
            'failed_details': failed
        }
    
    @staticmethod
    def get_attendance_report(
        course: Course = None,
        student: StudentProfile = None,
        start_date: date = None,
        end_date: date = None,
        group_by: str = 'day'
    ) -> Dict:
        """
        Generate attendance report.
        
        Args:
            course: Optional course filter
            student: Optional student filter
            start_date: Optional start date
            end_date: Optional end date
            group_by: How to group results ('day', 'week', 'month')
            
        Returns:
            dict: Attendance report data
        """
        queryset = Attendance.objects.all()
        
        if course:
            queryset = queryset.filter(course=course)
        if student:
            queryset = queryset.filter(student=student)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Calculate statistics
        total = queryset.count()
        present = queryset.filter(status=Attendance.STATUS_PRESENT).count()
        absent = queryset.filter(status=Attendance.STATUS_ABSENT).count()
        late = queryset.filter(status=Attendance.STATUS_LATE).count()
        excused = queryset.filter(status=Attendance.STATUS_EXCUSED).count()
        
        effective_present = present + late + excused
        percentage = (effective_present / total * 100) if total > 0 else 0
        
        # Get daily breakdown
        daily_breakdown = []
        if group_by == 'day':
            from django.db.models import Count, Case, When, IntegerField
            
            daily = queryset.values('date').annotate(
                total=Count('id'),
                present=Count(Case(When(status=Attendance.STATUS_PRESENT, then=1), output_field=IntegerField())),
                absent=Count(Case(When(status=Attendance.STATUS_ABSENT, then=1), output_field=IntegerField())),
                late=Count(Case(When(status=Attendance.STATUS_LATE, then=1), output_field=IntegerField())),
            ).order_by('date')
            
            daily_breakdown = list(daily)
        
        return {
            'summary': {
                'total_records': total,
                'present': present,
                'absent': absent,
                'late': late,
                'excused': excused,
                'percentage': round(percentage, 2)
            },
            'daily_breakdown': daily_breakdown,
            'filters': {
                'course': course.title if course else None,
                'student': student.get_full_name() if student else None,
                'start_date': start_date,
                'end_date': end_date
            }
        }
    
    @staticmethod
    def get_student_attendance_summary(
        student: StudentProfile,
        course: Course = None
    ) -> Dict:
        """
        Get comprehensive attendance summary for a student.
        
        Args:
            student: Student to get summary for
            course: Optional course filter
            
        Returns:
            dict: Attendance summary
        """
        queryset = Attendance.objects.filter(student=student)
        
        if course:
            queryset = queryset.filter(course=course)
        
        # Overall statistics
        total = queryset.count()
        present = queryset.filter(status=Attendance.STATUS_PRESENT).count()
        absent = queryset.filter(status=Attendance.STATUS_ABSENT).count()
        late = queryset.filter(status=Attendance.STATUS_LATE).count()
        excused = queryset.filter(status=Attendance.STATUS_EXCUSED).count()
        
        percentage = ((present + late + excused) / total * 100) if total > 0 else 0
        
        # Recent attendance (last 30 days)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent = queryset.filter(date__gte=thirty_days_ago)
        recent_total = recent.count()
        recent_present = recent.filter(status__in=[Attendance.STATUS_PRESENT, Attendance.STATUS_LATE]).count()
        recent_percentage = (recent_present / recent_total * 100) if recent_total > 0 else 0
        
        # Consecutive absences
        consecutive_absences = AttendanceService._calculate_consecutive_absences(student, course)
        
        return {
            'overall': {
                'total_classes': total,
                'present': present,
                'absent': absent,
                'late': late,
                'excused': excused,
                'percentage': round(percentage, 2)
            },
            'last_30_days': {
                'total_classes': recent_total,
                'present': recent_present,
                'percentage': round(recent_percentage, 2)
            },
            'consecutive_absences': consecutive_absences,
            'at_risk': consecutive_absences >= 3 or percentage < 75
        }
    
    @staticmethod
    def _calculate_consecutive_absences(
        student: StudentProfile,
        course: Course = None
    ) -> int:
        """Calculate consecutive absences."""
        queryset = Attendance.objects.filter(student=student)
        
        if course:
            queryset = queryset.filter(course=course)
        
        # Get recent attendance records ordered by date
        records = queryset.order_by('-date')[:30]
        
        consecutive = 0
        for record in records:
            if record.status == Attendance.STATUS_ABSENT:
                consecutive += 1
            else:
                break
        
        return consecutive
    
    @staticmethod
    def get_low_attendance_students(
        threshold: float = 75.0,
        course: Course = None
    ) -> List[Dict]:
        """
        Get students with attendance below threshold.
        
        Args:
            threshold: Minimum attendance percentage
            course: Optional course filter
            
        Returns:
            List of students with low attendance
        """
        from django.db.models import Count, Q, F, FloatField
        from django.db.models.functions import Cast
        
        queryset = Attendance.objects.all()
        
        if course:
            queryset = queryset.filter(course=course)
        
        # Calculate attendance percentage per student
        students_with_low_attendance = queryset.values('student').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status__in=[Attendance.STATUS_PRESENT, Attendance.STATUS_LATE, Attendance.STATUS_EXCUSED]))
        ).annotate(
            percentage=Cast(F('present'), FloatField()) / Cast(F('total'), FloatField()) * 100
        ).filter(percentage__lt=threshold)
        
        result = []
        for item in students_with_low_attendance:
            try:
                student = StudentProfile.objects.get(id=item['student'])
                result.append({
                    'student_id': student.student_id,
                    'name': student.get_full_name(),
                    'class_group': student.class_group.full_name if student.class_group else None,
                    'attendance_percentage': round(item['percentage'], 2),
                    'total_classes': item['total']
                })
            except StudentProfile.DoesNotExist:
                continue
        
        return result
