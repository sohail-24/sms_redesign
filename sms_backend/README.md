# School Management System (SMS) - Enterprise Edition

<p align="center">
  <img src="https://img.shields.io/badge/Django-4.2-green.svg" alt="Django 4.2">
  <img src="https://img.shields.io/badge/Python-3.11-blue.svg" alt="Python 3.11">
  <img src="https://img.shields.io/badge/DRF-3.14-orange.svg" alt="DRF 3.14">
  <img src="https://img.shields.io/badge/PostgreSQL-15-blue.svg" alt="PostgreSQL 15">
  <img src="https://img.shields.io/badge/Redis-7-red.svg" alt="Redis 7">
  <img src="https://img.shields.io/badge/Docker-Ready-blue.svg" alt="Docker Ready">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
</p>

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **School Management System (SMS)** is an enterprise-grade, production-ready platform designed for educational institutions of all sizes. Built with Django REST Framework, it provides a comprehensive solution for managing students, teachers, courses, attendance, grades, finances, and more.

### Key Highlights

- **Scalable Architecture**: Designed to handle 10,000+ concurrent users
- **Security-First**: JWT authentication, RBAC, audit logging, rate limiting
- **API-First**: RESTful API with OpenAPI documentation
- **Cloud-Ready**: Docker containerization with Kubernetes support
- **High Performance**: Redis caching, PostgreSQL with query optimization
- **Async Processing**: Celery for background tasks

---

## Architecture

### High-Level Architecture

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
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Domain-Driven Design

The system is organized into the following domains:

| Domain | Description | Key Entities |
|--------|-------------|--------------|
| **Auth Core** | Authentication & Authorization | User, Role, Permission |
| **Academics** | Academic operations | Student, Teacher, Course, Enrollment, Attendance, Grades |
| **Finance** | Financial management | Fee, Invoice, Payment, Expense |
| **Notifications** | Communication | Email, SMS, Push notifications |
| **Reports** | Analytics & Reporting | Academic reports, Financial reports |

---

## Features

### Core Features

#### Student Management
- Student registration with unique ID
- Profile management with photo upload
- Class/section assignment
- Guardian information
- Medical information
- Academic history tracking

#### Teacher Management
- Teacher registration with unique ID
- Profile and qualification management
- Course assignment
- Schedule management
- Performance tracking

#### Course Management
- Course creation with code and credits
- Prerequisite management
- Capacity management
- Teacher assignment
- Progress tracking

#### Enrollment Management
- Student enrollment in courses
- Bulk enrollment support
- Enrollment status tracking
- Prerequisite validation

#### Attendance Management
- Daily attendance marking
- Bulk attendance entry
- Attendance reports
- Low attendance alerts
- Consecutive absence tracking

#### Grade Management
- Grade entry and management
- Grade calculation
- Report card generation
- GPA calculation

#### Financial Management
- Fee structure management
- Invoice generation
- Payment processing
- Expense tracking
- Scholarship management

### Security Features

- **JWT Authentication**: Stateless, secure token-based auth
- **Role-Based Access Control (RBAC)**: Granular permissions
- **Audit Logging**: Complete audit trail of all actions
- **Rate Limiting**: Protection against abuse
- **Password Security**: Strong password policies
- **Account Lockout**: Protection against brute force

### Technical Features

- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Caching**: Multi-layer caching with Redis
- **Background Tasks**: Async processing with Celery
- **File Storage**: S3-compatible storage support
- **Health Checks**: Comprehensive system monitoring
- **Error Tracking**: Sentry integration

---

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git

### Run with Docker Compose

```bash
# Clone the repository
git clone https://github.com/your-org/sms-backend.git
cd sms-backend

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Run migrations and create superuser
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Access the application
# API: http://localhost:8000/api/v1/
# Admin: http://localhost:8000/admin/
# API Docs: http://localhost:8000/api/docs/
```

---

## Installation

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/development.txt

# Setup database
createdb sms_dev

# Configure environment
cp .env.example .env
# Edit .env with your local settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Production Setup

See [Deployment Guide](docs/deployment/README.md) for detailed production deployment instructions.

---

## API Documentation

### Authentication

The API uses JWT (JSON Web Token) authentication.

```bash
# Obtain access token
POST /api/v1/auth/login/
{
    "email": "user@example.com",
    "password": "your-password"
}

# Response
{
    "success": true,
    "data": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "id": "...",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
    }
}

# Use token in requests
Authorization: Bearer <access_token>
```

### Key Endpoints

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/v1/auth/login/` | POST | Login | Public |
| `/api/v1/auth/refresh/` | POST | Refresh token | Authenticated |
| `/api/v1/auth/logout/` | POST | Logout | Authenticated |
| `/api/v1/students/` | GET | List students | Teacher+ |
| `/api/v1/students/` | POST | Create student | Admin |
| `/api/v1/students/{id}/` | GET | Student details | Owner/Teacher/Admin |
| `/api/v1/students/{id}/attendance/` | GET | Student attendance | Owner/Teacher/Admin |
| `/api/v1/courses/` | GET | List courses | Authenticated |
| `/api/v1/courses/{id}/enroll/` | POST | Enroll in course | Admin/Student |
| `/api/v1/attendance/bulk/` | POST | Bulk attendance | Teacher |
| `/api/v1/reports/academic/` | GET | Academic reports | Admin |

### API Response Format

All API responses follow a standard format:

```json
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
```

Error responses:

```json
{
    "success": false,
    "data": null,
    "meta": null,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {
            "email": ["This field is required."]
        }
    }
}
```

---

## Deployment

### Docker Deployment

```bash
# Build production image
docker-compose -f docker-compose.yml build

# Start services
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f web
```

### Kubernetes Deployment

See [Kubernetes Deployment Guide](docs/deployment/kubernetes.md) for detailed instructions.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | Required |
| `DJANGO_DEBUG` | Debug mode | False |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts | localhost |
| `DB_NAME` | Database name | sms_db |
| `DB_USER` | Database user | sms_user |
| `DB_PASSWORD` | Database password | Required |
| `DB_HOST` | Database host | db |
| `REDIS_URL` | Redis connection URL | redis://redis:6379/0 |
| `CELERY_BROKER_URL` | Celery broker URL | redis://redis:6379/1 |

---

## Development

### Project Structure

```
sms_backend/
├── apps/                      # Domain applications
│   ├── auth_core/            # Authentication & Authorization
│   ├── academics/            # Academic domain
│   ├── finance/              # Finance domain
│   ├── notifications/        # Notifications
│   └── reports/              # Reports
├── core/                      # Shared components
│   ├── models/               # Base models
│   ├── permissions/          # Permission classes
│   ├── exceptions/           # Custom exceptions
│   └── utils/                # Utilities
├── infrastructure/            # Infrastructure layer
│   ├── database/             # Database config
│   ├── cache/                # Cache config
│   └── celery/               # Celery config
├── config/                    # Project configuration
│   └── settings/             # Environment settings
├── tests/                     # Test suite
├── docker/                    # Docker configuration
├── requirements/              # Python dependencies
└── docs/                      # Documentation
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest tests/test_students.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with black
black apps/ core/ tests/

# Sort imports
isort apps/ core/ tests/

# Run linter
flake8 apps/ core/ tests/

# Run type checker
mypy apps/ core/
```

---

## Testing

### Test Coverage

The project maintains >80% test coverage:

```bash
# Generate coverage report
pytest --cov=apps --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Test Structure

```
tests/
├── conftest.py               # pytest fixtures
├── factories/                # Model factories
├── unit/                     # Unit tests
│   ├── test_models.py
│   ├── test_services.py
│   └── test_serializers.py
├── integration/              # Integration tests
│   ├── test_api.py
│   └── test_auth.py
└── e2e/                      # End-to-end tests
```

---

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `pytest`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Standards

- Follow PEP 8 style guide
- Write docstrings for all public methods
- Maintain test coverage >80%
- Update documentation for new features

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

For support and questions:

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/sms-backend/issues)
- **Email**: support@your-school.edu

---

## Roadmap

### Phase 1 (Current)
- [x] Core domain models
- [x] Authentication & Authorization
- [x] Student & Teacher management
- [x] Course & Enrollment management
- [x] Attendance tracking
- [x] Grade management

### Phase 2 (Q2 2024)
- [ ] Mobile app API
- [ ] Parent portal
- [ ] Advanced reporting
- [ ] SMS notifications
- [ ] Payment gateway integration

### Phase 3 (Q3 2024)
- [ ] AI-powered insights
- [ ] Learning management
- [ ] Video conferencing
- [ ] Mobile apps (iOS/Android)

---

<p align="center">
  Built with ❤️ for Education
</p>
