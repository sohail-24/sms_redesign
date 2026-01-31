"""
Grade service for grade management business logic.
"""

from typing import List, Dict
from django.db import transaction

from core.exceptions import BusinessLogicError, NotFoundError
from ..models import StudentProfile, Course, Grade


class GradeService:
    """
    Service class for grade-related business logic.
    """
    
    @staticmethod
    @transaction.atomic
    def add_grade(
        student: StudentProfile,
        course: Course,
        score: float,
        grade: str = '',
        date=None,
        remarks: str = '',
        added_by=None
    ) -> Grade:
        """
        Add a grade for a student in a course.
        
        Args:
            student: Student to grade
            course: Course
            score: Numeric score
            grade: Letter grade (optional)
            date: Date of grade (optional)
            remarks: Remarks (optional)
            added_by: User adding the grade
            
        Returns:
            Grade: Created grade
        """
        from django.utils import timezone
        
        if date is None:
            date = timezone.now().date()
        
        grade_obj = Grade.objects.create(
            student=student,
            course=course,
            score=score,
            grade=grade,
            date=date,
            remarks=remarks
        )
        
        return grade_obj
    
    @staticmethod
    def get_student_grades(
        student: StudentProfile,
        course: Course = None
    ) -> List[Grade]:
        """
        Get grades for a student.
        
        Args:
            student: Student to get grades for
            course: Optional course filter
            
        Returns:
            List[Grade]: List of grades
        """
        queryset = Grade.objects.filter(student=student)
        
        if course:
            queryset = queryset.filter(course=course)
        
        return list(queryset.order_by('-date'))
    
    @staticmethod
    def get_course_statistics(course: Course) -> Dict:
        """
        Get grade statistics for a course.
        
        Args:
            course: Course to get statistics for
            
        Returns:
            Dict: Statistics
        """
        from django.db.models import Avg, Max, Min, Count
        
        grades = Grade.objects.filter(course=course)
        
        stats = grades.aggregate(
            total=Count('id'),
            average=Avg('score'),
            highest=Max('score'),
            lowest=Min('score')
        )
        
        passing = grades.filter(score__gte=course.passing_score).count()
        
        return {
            'total': stats['total'] or 0,
            'average': round(stats['average'], 2) if stats['average'] else 0,
            'highest': stats['highest'] or 0,
            'lowest': stats['lowest'] or 0,
            'passing': passing,
            'pass_rate': round((passing / stats['total'] * 100), 2) if stats['total'] else 0
        }
