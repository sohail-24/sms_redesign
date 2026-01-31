"""
URL configuration for academics app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.student_views import StudentViewSet
# from .views.course_views import CourseViewSet
# from .views.enrollment_views import EnrollmentViewSet
# from .views.attendance_views import AttendanceViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
# router.register(r'courses', CourseViewSet, basename='course')
# router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
# router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
]
