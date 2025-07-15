# Smart Nyuki Backend API

Smart Nyuki is a comprehensive apiary and honey production management system for beekeepers. This Django REST API backend supports both beekeepers with smart devices and those without.

## Table of Contents

- [Project Overview](#project-overview)
- [Stage 1: Accounts App (Current Implementation)](#stage-1-accounts-app-current-implementation)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Future Stages](#future-stages)

## Project Overview

The Smart Nyuki system is implemented in stages:

1. **Stage 1: Accounts (User Management)** ✅ IMPLEMENTED
2. **Stage 2: Apiaries (Beekeeping Structure)** ✅ IMPLEMENTED
3. **Stage 3: Devices (Smart Device Management)** ✅ IMPLEMENTED
4. **Stage 4: Inspections (Inspection Management)** ✅ IMPLEMENTED
5. **Stage 5: Production (Production & Monitoring)** ✅ IMPLEMENTED

## Installation

1. Clone the repository
2. Create virtual environment: `python -m venv .venv`
3. Activate virtual environment: `.\.venv\Scripts\Activate.ps1` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Run server: `python manage.py runserver`

### Additional Migration Commands for Stage 2

If you're adding Stage 2 to an existing installation:

```bash
python manage.py makemigrations apiaries
python manage.py migrate apiaries
```

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## Environment Variables

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Future Stages

### Stage 3: Devices (Smart Device Management)

- **Models**: SmartDevices, SensorReadings, AudioRecordings, DeviceImages
- **Endpoints**: Device registration, sensor data collection, media upload
- **Features**: IoT device integration, real-time monitoring

### Stage 4: Inspections (Inspection Management)

- **Models**: InspectionSchedules, InspectionReports
- **Endpoints**: Schedule management, inspection reporting
- **Features**: Automated scheduling, detailed inspection reports

### Stage 5: Production (Production & Monitoring)

- **Models**: Harvests, Alerts
- **Endpoints**: Harvest tracking, alert management
- **Features**: Production analytics, automated alerts

## Frontend Integration Notes

### Required Fields Summary for Forms

- **Registration**: email, first_name, last_name, password, password_confirm
- **Login**: email, password
- **Beekeeper Profile**: latitude, longitude, experience_level, established_date
- **Password Change**: old_password, new_password, new_password_confirm
- **Apiary Creation**: name, latitude, longitude
- **Hive Creation**: apiary, name, hive_type, installation_date

### State Management Recommendations

- Store user data and beekeeper profile in global state
- Cache JWT tokens securely
- Implement automatic token refresh
- Handle authentication state across app navigation

### Error Handling

- Implement field-level error display for forms
- Show appropriate error messages for API failures
- Handle network connectivity issues gracefully

This documentation will be updated as new stages are implemented.
