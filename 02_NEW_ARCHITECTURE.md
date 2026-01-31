# School Management System - New Architecture Design

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Web App    │  │  Mobile App │  │  Admin Panel│  │  Third Party│        │
│  │  (React)    │  │  (Flutter)  │  │  (Vue.js)   │  │  Integrations        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                   │
                         ┌─────────▼─────────┐
                         │   API Gateway     │
                         │   (Nginx/Kong)    │
                         │  Rate Limiting    │
                         │   SSL/TLS         │
                         └─────────┬─────────┘
                                   │
┌──────────────────────────────────┼──────────────────────────────────────────┐
│                         APPLICATION LAYER (Docker)                          │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Django REST Framework API                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │   Auth      │  │  Academics  │  │   Finance   │  │  Reports   │ │   │
│  │  │   Module    │  │   Module    │  │   Module    │  │   Module   │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Service Layer                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │   User      │  │  Enrollment │  │   Payment   │  │  Notification│ │   │
│  │  │   Service   │  │   Service   │  │   Service   │  │   Service    │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Background Workers (Celery)                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │   Email     │  │   Report    │  │   Payment   │  │   Cleanup  │ │   │
│  │  │   Tasks     │  │   Tasks     │  │   Tasks     │  │   Tasks    │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────┼──────────────────────────────────────────┐
│                         DATA LAYER                                          │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   PostgreSQL    │  │     Redis       │  │   MinIO/S3      │             │
│  │   (Primary DB)  │  │  (Cache/Queue)  │  │  (File Storage) │             │
│  │                 │  │                 │  │                 │             │
│  │  • Users        │  │  • Sessions     │  │  • Documents    │             │
│  │  • Academics    │  │  • Cache        │  │  • Photos       │             │
│  │  • Finance      │  │  • Rate Limit   │  │  • Reports      │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Domain-Driven Folder Structure

```
sms_backend/
├── apps/                                   # Domain-based applications
│   ├── __init__.py
│   ├── auth_core/                          # Authentication & Authorization
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py                     # Custom User model
│   │   │   ├── role.py                     # RBAC roles
│   │   │   └── permission.py               # Custom permissions
│   │   ├── serializers/
│   │   │   ├── __init__.py
│   │   │   ├── user_serializers.py
│   │   │   └── auth_serializers.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   └── user_service.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── auth_views.py
│   │   │   └── user_views.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── academics/                          # Academic Domain
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── student.py                  # Student profile
│   │   │   ├── teacher.py                  # Teacher profile
│   │   │   ├── course.py                   # Course/Subject
│   │   │   ├── class_group.py              # Class/Section
│   │   │   ├── enrollment.py               # Student-Course enrollment
│   │   │   ├── attendance.py               # Attendance records
│   │   │   ├── grade.py                    # Grades/Results
│   │   │   ├── assignment.py               # Assignments
│   │   │   ├── submission.py               # Assignment submissions
│   │   │   ├── schedule.py                 # Timetable/Schedule
│   │   │   └── examination.py              # Exams
│   │   ├── serializers/
│   │   ├── services/
│   │   │   ├── student_service.py
│   │   │   ├── enrollment_service.py
│   │   │   ├── attendance_service.py
│   │   │   └── grade_service.py
│   │   ├── views/
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── finance/                            # Finance Domain
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── fee_structure.py            # Fee templates
│   │   │   ├── fee.py                      # Individual fees
│   │   │   ├── invoice.py                  # Invoices
│   │   │   ├── payment.py                  # Payments
│   │   │   ├── expense.py                  # School expenses
│   │   │   └── scholarship.py              # Scholarships
│   │   ├── serializers/
│   │   ├── services/
│   │   │   ├── payment_service.py
│   │   │   ├── invoice_service.py
│   │   │   └── fee_service.py
│   │   ├── views/
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── notifications/                      # Notifications Domain
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── notice.py                   # School notices
│   │   │   ├── announcement.py             # Course announcements
│   │   │   ├── message.py                  # Internal messages
│   │   │   └── notification.py             # Push notifications
│   │   ├── services/
│   │   │   ├── email_service.py
│   │   │   ├── sms_service.py
│   │   │   └── push_service.py
│   │   ├── tasks.py                        # Celery tasks
│   │   └── tests/
│   │
│   └── reports/                            # Reports Domain
│       ├── __init__.py
│       ├── services/
│       │   ├── academic_report_service.py
│       │   ├── attendance_report_service.py
│       │   ├── financial_report_service.py
│       │   └── export_service.py
│       ├── views/
│       └── tests/
│
├── core/                                   # Shared/Core Components
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py                   # Abstract base model
│   │   ├── audit_model.py                  # Audit trail mixin
│   │   └── soft_delete.py                  # Soft delete mixin
│   ├── permissions/
│   │   ├── __init__.py
│   │   ├── base_permissions.py
│   │   └── role_permissions.py
│   ├── exceptions/
│   │   ├── __init__.py
│   │   ├── base_exceptions.py
│   │   └── validation_exceptions.py
│   ├── validators/
│   │   ├── __init__.py
│   │   └── common_validators.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── pagination.py
│   │   ├── filters.py
│   │   └── helpers.py
│   └── middleware/
│       ├── __init__.py
│       ├── audit_middleware.py
│       └── rate_limit_middleware.py
│
├── config/                                 # Project Configuration
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                         # Base settings
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py                             # Root URL config
│   ├── wsgi.py
│   └── asgi.py
│
├── infrastructure/                         # Infrastructure Layer
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── routers.py                      # DB routing
│   │   └── migrations/
│   ├── cache/
│   │   ├── __init__.py
│   │   └── cache_manager.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── storage_backend.py
│   └── celery/
│       ├── __init__.py
│       └── celery_app.py
│
├── tests/                                  # Integration Tests
│   ├── __init__.py
│   ├── conftest.py                         # pytest fixtures
│   ├── factories/                          # Model factories
│   └── integration/
│
├── scripts/                                # Utility Scripts
│   ├── __init__.py
│   ├── setup.py
│   └── seed_data.py
│
├── docs/                                   # Documentation
│   ├── api/                                # API Documentation
│   ├── architecture/                       # Architecture docs
│   └── deployment/                         # Deployment guides
│
├── docker/                                 # Docker Configuration
│   ├── Dockerfile
│   ├── Dockerfile.celery
│   ├── entrypoint.sh
│   └── celery-entrypoint.sh
│
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── manage.py
├── pytest.ini
├── setup.cfg
├── .env.example
├── .dockerignore
├── .gitignore
└── docker-compose.yml
```

---

## 3. Domain Separation Strategy

### 3.1 Auth Core Domain
**Responsibilities:**
- User authentication (JWT)
- Role-based access control
- Permission management
- Session management
- Password management

**Entities:**
- User (custom, extends AbstractBaseUser)
- Role (Admin, Teacher, Student, Staff, Parent)
- Permission (granular permissions)
- UserRole (many-to-many mapping)

### 3.2 Academics Domain
**Responsibilities:**
- Student management
- Teacher management
- Course/Subject management
- Enrollment management
- Attendance tracking
- Grade management
- Assignment management
- Examination management
- Scheduling/Timetable

**Entities:**
- StudentProfile (extends User)
- TeacherProfile (extends User)
- Course
- ClassGroup (Class + Section)
- Enrollment
- Attendance
- Grade
- Assignment
- Submission
- Schedule
- Examination

### 3.3 Finance Domain
**Responsibilities:**
- Fee structure management
- Invoice generation
- Payment processing
- Expense tracking
- Financial reporting
- Scholarship management

**Entities:**
- FeeStructure
- Fee
- Invoice
- Payment
- Expense
- Scholarship

### 3.4 Notifications Domain
**Responsibilities:**
- Email notifications
- SMS notifications
- Push notifications
- Internal messaging
- Notice board

**Entities:**
- Notice
- Announcement
- Message
- Notification

---

## 4. Role-Based Access Control (RBAC) Design

### 4.1 Role Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                        SUPER_ADMIN                           │
│              (Full system access - School Owner)             │
└─────────────────────────────┬───────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼───────┐    ┌────────▼────────┐   ┌───────▼───────┐
│    ADMIN      │    │     PRINCIPAL   │   │    ACCOUNTANT │
│  (System Mgmt)│    │  (Academic Mgmt)│   │  (Finance Mgmt)│
└───────┬───────┘    └────────┬────────┘   └───────────────┘
        │                     │
        │         ┌───────────┼───────────┐
        │         │           │           │
┌───────▼───────┐ │  ┌────────▼──────┐   ┌▼──────────────┐
│     STAFF     │ │  │    TEACHER    │   │    STUDENT    │
│  (Operations) │ │  │ (Class Mgmt)  │   │ (Self Service)│
└───────────────┘ │  └───────────────┘   └───────────────┘
                  │
                  │  ┌─────────────────┐
                  └──┤     PARENT      │
                     │ (View-only)     │
                     └─────────────────┘
```

### 4.2 Permission Matrix

| Resource | Create | Read | Update | Delete | Special |
|----------|--------|------|--------|--------|---------|
| **User Management** |
| Users | Super Admin | Self, Admin | Self, Admin | Super Admin | - |
| Roles | Super Admin | All | Super Admin | - | - |
| **Academics** |
| Students | Admin, Staff | Teacher+, Self | Admin, Self | Super Admin | Export: Admin+ |
| Teachers | Admin | All | Self, Admin | Super Admin | Assign Course: Admin |
| Courses | Admin | All | Admin | Admin | - |
| Classes | Admin | All | Admin | Admin | - |
| Enrollments | Admin, Staff | Teacher+, Self | Admin | Admin | - |
| Attendance | Teacher | Teacher+, Self | Teacher | - | Bulk: Teacher |
| Grades | Teacher | Teacher+, Self | Teacher | - | Bulk: Teacher |
| Assignments | Teacher | Enrolled | Teacher | Teacher | Submit: Student |
| Exams | Admin | All | Admin | Admin | - |
| **Finance** |
| Fee Structures | Accountant | Accountant+ | Accountant | - | - |
| Invoices | Accountant | Self, Accountant | Accountant | - | - |
| Payments | System | Self, Accountant | - | - | Process: System |
| Expenses | Accountant | Accountant+ | Accountant | Super Admin | - |
| **Reports** |
| Academic | Admin | Admin+ | - | - | Generate: Admin+ |
| Financial | Accountant | Accountant+ | - | - | Generate: Accountant+ |
| Attendance | Teacher | Teacher+ | - | - | Generate: Teacher+ |

### 4.3 Permission Implementation

```python
# core/permissions/role_permissions.py

from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.role == Role.ADMIN
        )

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in [Role.TEACHER, Role.ADMIN, Role.SUPER_ADMIN]
        )

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Students can only access their own data
        if hasattr(obj, 'student'):
            return obj.student.user == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.role == Role.ADMIN:
            return True
        return obj.user == request.user
```

---

## 5. API-First Design

### 5.1 API Versioning Strategy

```
/api/v1/auth/          # Authentication endpoints
/api/v1/users/         # User management
/api/v1/students/      # Student operations
/api/v1/teachers/      # Teacher operations
/api/v1/courses/       # Course management
/api/v1/enrollments/   # Enrollment operations
/api/v1/attendance/    # Attendance tracking
/api/v1/grades/        # Grade management
/api/v1/fees/          # Fee operations
/api/v1/payments/      # Payment processing
/api/v1/invoices/      # Invoice management
/api/v1/reports/       # Report generation
/api/v1/notifications/ # Notifications
```

### 5.2 API Response Standard

```python
# Standard API Response Format
{
    "success": true,
    "data": { ... },
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 100,
        "total_pages": 5
    },
    "error": null
}

# Error Response Format
{
    "success": false,
    "data": null,
    "meta": null,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {
            "email": ["This field is required."],
            "age": ["Must be at least 5 years old."]
        }
    }
}
```

### 5.3 Key API Endpoints

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/v1/auth/login/` | POST | JWT login | Public |
| `/api/v1/auth/refresh/` | POST | Refresh token | Authenticated |
| `/api/v1/auth/logout/` | POST | Logout | Authenticated |
| `/api/v1/users/me/` | GET | Current user profile | Authenticated |
| `/api/v1/students/` | GET | List students | Admin, Teacher |
| `/api/v1/students/` | POST | Create student | Admin, Staff |
| `/api/v1/students/{id}/` | GET | Student detail | Admin, Teacher, Self |
| `/api/v1/students/{id}/attendance/` | GET | Student attendance | Admin, Teacher, Self |
| `/api/v1/students/{id}/grades/` | GET | Student grades | Admin, Teacher, Self |
| `/api/v1/courses/` | GET | List courses | Authenticated |
| `/api/v1/courses/{id}/enroll/` | POST | Enroll in course | Admin, Student |
| `/api/v1/attendance/bulk/` | POST | Bulk attendance | Teacher |
| `/api/v1/grades/bulk/` | POST | Bulk grade entry | Teacher |
| `/api/v1/fees/{id}/pay/` | POST | Process payment | Admin, Accountant |
| `/api/v1/reports/academic/` | GET | Academic reports | Admin |
| `/api/v1/reports/financial/` | GET | Financial reports | Accountant |

---

## 6. Service Layer Pattern

### 6.1 Service Design Principles

```python
# apps/academics/services/student_service.py

from django.db import transaction
from core.exceptions import ValidationError, NotFoundError
from ..models import StudentProfile, Enrollment

class StudentService:
    """
    Encapsulates all business logic related to student management.
    All student operations MUST go through this service.
    """
    
    @staticmethod
    @transaction.atomic
    def create_student(user_data: dict, student_data: dict) -> StudentProfile:
        """
        Create a new student with user account.
        
        Args:
            user_data: Dict containing user fields (email, password, etc.)
            student_data: Dict containing student-specific fields
            
        Returns:
            StudentProfile: Created student profile
            
        Raises:
            ValidationError: If data is invalid
            DuplicateError: If student ID or email already exists
        """
        # Validation
        StudentValidator.validate_student_data(student_data)
        
        # Check for duplicates
        if StudentService._student_exists(student_data.get('student_id')):
            raise DuplicateError("Student ID already exists")
        
        # Create user account
        user = UserService.create_user(user_data, role=Role.STUDENT)
        
        # Create student profile
        student = StudentProfile.objects.create(
            user=user,
            **student_data
        )
        
        # Audit log
        AuditService.log_action(
            action='STUDENT_CREATED',
            user=user,
            object_id=student.id,
            details=student_data
        )
        
        return student
    
    @staticmethod
    def enroll_student_in_course(
        student_id: int, 
        course_id: int,
        enrolled_by: User
    ) -> Enrollment:
        """
        Enroll a student in a course with business rule validation.
        """
        student = StudentService.get_student(student_id)
        course = CourseService.get_course(course_id)
        
        # Business rules
        if not course.is_active:
            raise ValidationError("Course is not active")
        
        if not course.has_capacity:
            raise ValidationError("Course is at full capacity")
        
        if Enrollment.objects.filter(student=student, course=course).exists():
            raise DuplicateError("Student already enrolled")
        
        enrollment = Enrollment.objects.create(
            student=student,
            course=course,
            enrolled_by=enrolled_by
        )
        
        # Send notification
        NotificationService.send_course_enrollment_notification(enrollment)
        
        return enrollment
```

### 6.2 Service Registry Pattern

```python
# core/services/registry.py

class ServiceRegistry:
    """
    Central registry for all services.
    Enables dependency injection and easier testing.
    """
    _services = {}
    
    @classmethod
    def register(cls, name: str, service_class):
        cls._services[name] = service_class
    
    @classmethod
    def get(cls, name: str):
        return cls._services.get(name)
    
    @classmethod
    def inject(cls, *service_names):
        """Decorator for dependency injection"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                for name in service_names:
                    kwargs[name] = cls.get(name)
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Register services
ServiceRegistry.register('student', StudentService)
ServiceRegistry.register('payment', PaymentService)
ServiceRegistry.register('notification', NotificationService)
```

---

## 7. Database Design Improvements

### 7.1 Indexing Strategy

```python
# apps/academics/models/student.py

class StudentProfile(models.Model):
    class Meta:
        indexes = [
            # Primary lookup indexes
            models.Index(fields=['student_id'], name='idx_student_id'),
            models.Index(fields=['user__email'], name='idx_student_email'),
            
            # Filter indexes
            models.Index(fields=['status', 'admission_date'], name='idx_status_admission'),
            models.Index(fields=['grade_level', 'status'], name='idx_grade_status'),
            
            # Composite index for common queries
            models.Index(fields=['class_group', 'status'], name='idx_class_status'),
        ]
```

### 7.2 Soft Delete Implementation

```python
# core/models/soft_delete.py

from django.db import models
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'auth_core.User', 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='deleted_%(class)s'
    )
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None):
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()
    
    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.save()
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None
```

---

## 8. Caching Strategy

### 8.1 Cache Layers

```python
# infrastructure/cache/cache_manager.py

from django.core.cache import cache
from django_redis import get_redis_connection

class CacheManager:
    """
    Multi-layer caching strategy:
    1. Request cache (per-request)
    2. Process cache (local memory)
    3. Redis cache (distributed)
    """
    
    # Cache TTLs
    TTL_SHORT = 60        # 1 minute
    TTL_MEDIUM = 300      # 5 minutes
    TTL_LONG = 3600       # 1 hour
    TTL_DAY = 86400       # 24 hours
    
    @staticmethod
    def get_student_profile(student_id: int):
        cache_key = f"student:profile:{student_id}"
        
        # Try cache first
        data = cache.get(cache_key)
        if data:
            return data
        
        # Cache miss - fetch from DB
        student = StudentProfile.objects.select_related('user').get(id=student_id)
        
        # Store in cache
        cache.set(cache_key, student, CacheManager.TTL_MEDIUM)
        
        return student
    
    @staticmethod
    def invalidate_student_cache(student_id: int):
        """Invalidate all cached data for a student"""
        patterns = [
            f"student:profile:{student_id}",
            f"student:attendance:{student_id}:*",
            f"student:grades:{student_id}:*",
        ]
        redis = get_redis_connection()
        for pattern in patterns:
            for key in redis.scan_iter(match=pattern):
                cache.delete(key)
```

---

## 9. Background Task Processing

### 9.1 Celery Task Design

```python
# apps/notifications/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

@shared_task(bind=True, max_retries=3)
def send_email_notification(self, template_name, recipient, context):
    """
    Send email notification asynchronously.
    
    Args:
        template_name: Email template to use
        recipient: Email address
        context: Template context data
    """
    try:
        subject = context.get('subject', 'Notification')
        html_message = render_to_string(f'emails/{template_name}.html', context)
        
        send_mail(
            subject=subject,
            message='',  # Plain text version
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@shared_task
def generate_monthly_report(month, year):
    """
    Generate monthly academic report.
    Heavy computation - runs in background.
    """
    from apps.reports.services import AcademicReportService
    
    report = AcademicReportService.generate_monthly_report(month, year)
    
    # Store report file
    file_path = report.save_to_storage()
    
    # Notify admins
    NotificationService.notify_admins(
        f"Monthly report for {month}/{year} is ready",
        link=file_path
    )
```

---

## 10. Monitoring & Observability

### 10.1 Health Checks

```python
# apps/core/views/health.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connections
from django.core.cache import cache
import redis

@api_view(['GET'])
def health_check(request):
    """
    Comprehensive health check for all services.
    """
    checks = {
        'database': _check_database(),
        'cache': _check_cache(),
        'celery': _check_celery(),
        'storage': _check_storage(),
    }
    
    all_healthy = all(c['status'] == 'healthy' for c in checks.values())
    
    return Response(
        {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'checks': checks,
            'timestamp': timezone.now().isoformat(),
        },
        status=200 if all_healthy else 503
    )

def _check_database():
    try:
        connections['default'].cursor().execute('SELECT 1')
        return {'status': 'healthy', 'response_time_ms': 10}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}

def _check_cache():
    try:
        cache.set('health_check', 'ok', 10)
        value = cache.get('health_check')
        return {'status': 'healthy' if value == 'ok' else 'unhealthy'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}
```

---

## 11. Summary of Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Architecture** | Monolithic | Modular, Domain-Driven |
| **Code Organization** | Single files | Domain-based packages |
| **Business Logic** | In views | Service layer |
| **API** | Server-side rendered | REST API with DRF |
| **Authentication** | Sessions | JWT |
| **Permissions** | Basic | Granular RBAC |
| **Database** | SQLite | PostgreSQL with indexes |
| **Caching** | None | Redis multi-layer |
| **Async Tasks** | Synchronous | Celery |
| **Testing** | None | pytest with >80% coverage |
| **Deployment** | Manual | Docker + CI/CD |
| **Monitoring** | None | Health checks + Sentry |
| **Documentation** | None | OpenAPI/Swagger |

---

*Architecture design complete. Proceed to implementation.*
