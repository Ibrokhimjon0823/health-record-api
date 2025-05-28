# Health Record Management API

A secure REST API for managing personal health records, built with Django REST Framework. This system allows patients to upload health records, select doctors, and enables doctors to annotate these records with professional insights.

## 🚀 Quick Start

```bash
# Clone the repository
git clone git@github.com:Ibrokhimjon0823/health-record-api.git
cd health-record-api

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

## 🌐 Live Demo

The API is deployed and available for testing at: `http://51.20.144.224`

### Admin Panel Access
- **URL**: http://51.20.144.224/admin/
- **Username**: admin@gmail.com
- **Password**: admin

The admin panel provides access to:
- User management
- Health records overview
- Notification monitoring
- Database administration

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack & Architecture](#tech-stack--architecture)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Key Features](#key-features)
- [Security](#security)
- [Testing](#testing)
- [Deployment](#deployment)

## 🎯 Project Overview

This API provides a comprehensive health record management system with the following core functionalities:

1. **User Management**: Registration and authentication for patients and doctors
2. **Health Records**: Patients can upload medical records with file attachments
3. **Doctor Assignment**: Patients can assign specific doctors to their health records
4. **Professional Annotations**: Doctors can add professional notes to assigned records
5. **Notifications**: Real-time notifications for record assignments and updates

## 🛠 Tech Stack & Architecture

### Core Technologies

- **Django 5.2.1**: Chosen for its robust ORM, built-in admin, and excellent security features
- **Django REST Framework 3.16.0**: Industry-standard for building REST APIs in Django
- **PostgreSQL**: Production-ready database with strong data integrity
- **Redis & Celery**: Asynchronous task processing for notifications
- **JWT Authentication**: Stateless, secure authentication mechanism

### Architecture Decisions

1. **Modular App Structure**: Separated concerns into `accounts`, `records`, and `notifications` apps for maintainability
2. **Custom User Model**: Extended Django's AbstractBaseUser for role-based access control
3. **Signal-Driven Notifications**: Automatic notifications using Django signals for loose coupling
4. **Service Layer Pattern**: Business logic separated from views for testability

### Key Libraries

- **drf-spectacular**: Auto-generated OpenAPI documentation
- **django-cors-headers**: CORS support for frontend integration
- **pytest-django**: Comprehensive testing framework
- **factory-boy**: Test data generation

## 📚 API Documentation

### Authentication

All endpoints except registration and login require JWT authentication.

```http
Authorization: Bearer <access_token>
```

### Base URL

**Local Development**:
```
http://localhost:8000/api
```

**Live Server**:
```
http://51.20.144.224/api
```

### Endpoints Overview

#### 🔐 Authentication & User Management

| Method | Endpoint                    | Description              | Access        |
| ------ | --------------------------- | ------------------------ | ------------- |
| POST   | `/accounts/register/`       | Register new user        | Public        |
| POST   | `/accounts/login/`          | Login and get JWT tokens | Public        |
| POST   | `/accounts/profile-create/` | Create user profile      | Authenticated |
| PATCH  | `/accounts/profile-update/` | Update user profile      | Authenticated |
| GET    | `/accounts/doctors/`        | List all doctors         | Patients only |

#### 📋 Health Records

| Method | Endpoint                            | Description              | Access        |
| ------ | ----------------------------------- | ------------------------ | ------------- |
| GET    | `/records/patient/`                 | List patient's records   | Patients only |
| POST   | `/records/patient/`                 | Create new health record | Patients only |
| GET    | `/records/patient/{id}/`            | Get specific record      | Patients only |
| PATCH  | `/records/patient/{id}/`            | Update health record     | Patients only |
| DELETE | `/records/files/{id}/`              | Delete record file       | Patients only |
| GET    | `/records/doctor/`                  | List assigned records    | Doctors only  |
| GET    | `/records/doctor/{id}/`             | View assigned record     | Doctors only  |
| POST   | `/records/doctor/annotations/`      | Add annotation           | Doctors only  |
| PATCH  | `/records/doctor/annotations/{id}/` | Update annotation        | Doctors only  |

#### 🔔 Notifications

| Method | Endpoint                        | Description                      | Access        |
| ------ | ------------------------------- | -------------------------------- | ------------- |
| GET    | `/notifications/`               | List user notifications          | Authenticated |
| GET    | `/notifications/{id}/`          | Get notification (marks as read) | Authenticated |
| POST   | `/notifications/mark-all-read/` | Mark all as read                 | Authenticated |
| DELETE | `/notifications/delete-all/`    | Delete all notifications         | Authenticated |

### Sample API Requests

#### User Registration

```json
POST /api/accounts/register/
{
    "email": "patient@example.com",
    "password": "securepassword",
    "first_name": "John",
    "last_name": "Doe",
    "role": "patient"
}

Response:
{
    "pk": "uuid",
    "email": "patient@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "patient",
    "tokens": {
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token"
    }
}
```

#### Create Health Record

```json
POST /api/records/patient/
{
    "doctor": "doctor_uuid",
    "record_type": "lab_result",
    "description": "Blood test results",
    "files": [file1, file2]  // multipart/form-data
}
```

## 📁 Project Structure

```
health-record-api/
├── apps/
│   ├── accounts/         # User authentication and profiles
│   │   ├── models.py     # User, PatientProfile, DoctorProfile
│   │   ├── views.py      # Authentication endpoints
│   │   ├── serializers.py
│   │   └── permissions.py # Role-based permissions
│   ├── records/          # Health record management
│   │   ├── models.py     # HealthRecord, HealthRecordFile, DoctorAnnotation
│   │   ├── views.py      # CRUD operations
│   │   ├── signals.py    # Notification triggers
│   │   └── serializers.py
│   └── notifications/    # Notification system
│       ├── models.py     # Notification model
│       ├── views.py      # Notification endpoints
│       └── tasks.py      # Async email tasks
├── conf/                 # Project configuration
│   ├── settings.py       # Django settings
│   ├── urls.py           # URL routing
│   └── celery.py         # Celery configuration
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker setup
└── pytest.ini           # Test configuration
```

## 🔑 Key Features

### 1. Role-Based Access Control

- **Patients**: Can manage their own records and assign doctors
- **Doctors**: Can only view and annotate assigned records
- Custom permissions ensure data privacy

### 2. File Management

- Secure file uploads for medical documents
- Support for multiple file types (PDF, images, etc.)
- Files stored in `mediafiles/` directory

### 3. Real-Time Notifications

- Automatic notifications on record assignment
- Notifications when doctors add annotations
- Email notifications via Celery (async)

### 4. Data Validation

- Strong input validation using serializers
- Role-specific profile requirements
- File size and type restrictions

## 🔒 Security

1. **Authentication**: JWT tokens with configurable expiration
2. **Authorization**: Role-based permissions on all endpoints
3. **Data Privacy**: Users can only access their own data
4. **Password Security**: Bcrypt hashing with Django's auth system
5. **CORS**: Configured for specific frontend origins
6. **SQL Injection**: Protected by Django ORM
7. **XSS Protection**: Built-in Django middleware

## 🧪 Testing

The project includes comprehensive test coverage (91 tests):

```bash
# Run all tests
./run_tests.sh

# Run specific app tests
DJANGO_SETTINGS_MODULE=test_settings python -m pytest apps/accounts/

# Generate coverage report
python -m pytest --cov=apps --cov-report=html
```

Test coverage includes:

- Model validations
- API endpoint responses
- Permission checks
- Signal handlers
- Edge cases and error handling

## 🚢 Deployment

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run migrations in container
docker-compose exec web python manage.py migrate
```

### Environment Variables

Create a `.env` file with:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,yourdomain.com
DB_NAME=health_records_db
DB_USER=postgres
DB_PASSWORD=secure_password
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure allowed hosts
- [ ] Set up SSL/TLS
- [ ] Configure production database
- [ ] Set up media file storage (S3 recommended)
- [ ] Configure email backend for notifications
- [ ] Set up monitoring and logging

## 📝 API Design Decisions

1. **RESTful Design**: Clear resource-based URLs with standard HTTP methods
2. **Consistent Response Format**: All responses follow similar structure
3. **Pagination**: List endpoints support pagination (disabled in tests)
4. **Error Handling**: Standardized error responses with appropriate status codes
5. **Versioning Ready**: URL structure supports future API versioning

## 📄 License

This project is created as part of a technical assessment.

## 📖 Additional Documentation

### Swagger/OpenAPI Documentation

Access the interactive API documentation:

**Local Development**:
```
http://localhost:8000/api/schema/swagger-ui/
```

**Live Server**:
```
http://51.20.144.224/api/schema/swagger-ui/
```

The Swagger UI provides:
- Complete API reference
- Interactive endpoint testing
- Request/response examples
- Authentication setup
