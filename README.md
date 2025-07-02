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
5. **Stage 5: Production (Production & Monitoring)**

## Stage 1: Accounts App (Current Implementation)

### Models

#### User Model
- **Purpose**: Custom user model for authentication
- **Database Table**: `users`
- **Fields**:
  - `id` (UUID, Primary Key) - Auto-generated
  - `email` (String, Unique, Required) - User's email address
  - `first_name` (String, Required) - User's first name
  - `last_name` (String, Required) - User's last name
  - `phone_number` (String, Optional) - User's phone number
  - `is_active` (Boolean, Default: True) - Account status
  - `created_at` (DateTime, Auto) - Account creation timestamp
  - `updated_at` (DateTime, Auto) - Last update timestamp
  - `deleted_at` (DateTime, Optional) - Soft delete timestamp

#### BeekeeperProfile Model
- **Purpose**: Extended profile information for beekeepers
- **Database Table**: `beekeeper_profiles`
- **Fields**:
  - `id` (UUID, Primary Key) - Auto-generated
  - `user` (ForeignKey to User) - Associated user account
  - `latitude` (Decimal, Required) - Location latitude
  - `longitude` (Decimal, Required) - Location longitude
  - `address` (Text, Optional) - Physical address
  - `experience_level` (Choice, Required) - Beginner/Intermediate/Advanced/Expert
  - `established_date` (Date, Required) - When beekeeping operation started
  - `app_start_date` (Date, Auto) - When user started using the app
  - `certification_details` (Text, Optional) - Certification information
  - `profile_picture_url` (URL, Optional) - Profile picture URL
  - `notes` (Text, Optional) - Additional notes
  - `created_at` (DateTime, Auto) - Profile creation timestamp
  - `updated_at` (DateTime, Auto) - Last update timestamp

## Stage 2: Apiaries App (Current Implementation)

### Models

#### Apiaries Model
- **Purpose**: Manage beekeeping locations and apiary information
- **Database Table**: `apiaries`
- **Fields**:
  - `id` (UUID, Primary Key) - Auto-generated
  - `beekeeper` (ForeignKey to BeekeeperProfile) - Associated beekeeper profile
  - `name` (String, Required) - Apiary name
  - `latitude` (Decimal, Required) - Apiary latitude coordinates
  - `longitude` (Decimal, Required) - Apiary longitude coordinates
  - `address` (Text, Optional) - Physical address of the apiary
  - `description` (Text, Optional) - Description of the apiary
  - `created_at` (DateTime, Auto) - Apiary creation timestamp
  - `updated_at` (DateTime, Auto) - Last update timestamp
  - `deleted_at` (DateTime, Optional) - Soft delete timestamp

#### Hives Model
- **Purpose**: Track individual hives within apiaries
- **Database Table**: `hives`
- **Fields**:
  - `id` (UUID, Primary Key) - Auto-generated
  - `apiary` (ForeignKey to Apiaries) - Associated apiary
  - `name` (String, Required) - Hive name/identifier
  - `hive_type` (Choice, Required) - Langstroth/Top Bar/Warre/Flow Hive/Other
  - `installation_date` (Date, Required) - When hive was installed
  - `has_smart_device` (Boolean, Default: False) - Whether hive has smart monitoring
  - `is_active` (Boolean, Default: True) - Hive status
  - `created_at` (DateTime, Auto) - Hive creation timestamp
  - `updated_at` (DateTime, Auto) - Last update timestamp
  - `deleted_at` (DateTime, Optional) - Soft delete timestamp

## API Endpoints

### Authentication Endpoints

#### 1. User Registration
- **URL**: `POST /api/accounts/register/`
- **Purpose**: Register a new user account
- **Authentication**: Not required
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890", // Optional
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "phone_number": "+1234567890",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    },
    "tokens": {
      "refresh": "refresh_token_string",
      "access": "access_token_string"
    }
  }
  ```

#### 2. User Login
- **URL**: `POST /api/accounts/login/`
- **Purpose**: Authenticate user and get JWT tokens
- **Authentication**: Not required
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "phone_number": "+1234567890",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z",
      "beekeeper_profile": null // or profile object if exists
    },
    "tokens": {
      "refresh": "refresh_token_string",
      "access": "access_token_string"
    }
  }
  ```

#### 3. Token Refresh
- **URL**: `POST /api/accounts/token/refresh/`
- **Purpose**: Refresh access token using refresh token
- **Authentication**: Not required
- **Request Body**:
  ```json
  {
    "refresh": "refresh_token_string"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access": "new_access_token_string"
  }
  ```

#### 4. User Logout
- **URL**: `POST /api/accounts/logout/`
- **Purpose**: Logout user by blacklisting refresh token
- **Authentication**: Required (Bearer token)
- **Request Body**:
  ```json
  {
    "refresh": "refresh_token_string"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "message": "Logout successful"
  }
  ```

### User Profile Endpoints

#### 5. Get/Update User Profile
- **URL**: `GET/PATCH /api/accounts/profile/`
- **Purpose**: Retrieve or update current user's profile
- **Authentication**: Required (Bearer token)
- **GET Response (200 OK)**:
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone_number": "+1234567890",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "beekeeper_profile": {
      // BeekeeperProfile object or null
    }
  }
  ```
- **PATCH Request Body** (only include fields to update):
  ```json
  {
    "first_name": "Jane",
    "last_name": "Smith",
    "phone_number": "+0987654321"
  }
  ```

#### 6. Change Password
- **URL**: `POST /api/accounts/change-password/`
- **Purpose**: Change current user's password
- **Authentication**: Required (Bearer token)
- **Request Body**:
  ```json
  {
    "old_password": "currentpassword",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "message": "Password changed successfully"
  }
  ```

### Beekeeper Profile Endpoints

#### 7. List/Create Beekeeper Profiles
- **URL**: `GET/POST /api/accounts/beekeeper-profiles/`
- **Purpose**: List user's beekeeper profiles or create new one
- **Authentication**: Required (Bearer token)
- **GET Response (200 OK)**:
  ```json
  [
    {
      "id": "uuid",
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "phone_number": "+1234567890",
        "is_active": true,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
      },
      "latitude": "40.12345678",
      "longitude": "-74.12345678",
      "coordinates": [40.12345678, -74.12345678],
      "address": "123 Farm Road, City, State",
      "experience_level": "Intermediate",
      "established_date": "2020-01-01",
      "app_start_date": "2025-01-01",
      "certification_details": "Certified Beekeeper Level 2",
      "profile_picture_url": "https://example.com/profile.jpg",
      "notes": "Specializes in organic honey production",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
  ```
- **POST Request Body**:
  ```json
  {
    "latitude": "40.12345678",
    "longitude": "-74.12345678",
    "address": "123 Farm Road, City, State", // Optional
    "experience_level": "Intermediate", // Required: Beginner/Intermediate/Advanced/Expert
    "established_date": "2020-01-01", // Required: YYYY-MM-DD format
    "certification_details": "Certified Beekeeper Level 2", // Optional
    "profile_picture_url": "https://example.com/profile.jpg", // Optional
    "notes": "Specializes in organic honey production" // Optional
  }
  ```

#### 8. Get/Update/Delete Specific Beekeeper Profile
- **URL**: `GET/PATCH/DELETE /api/accounts/beekeeper-profiles/{profile_id}/`
- **Purpose**: Retrieve, update, or delete specific beekeeper profile
- **Authentication**: Required (Bearer token)
- **GET/PATCH Response**: Same as individual profile object above
- **PATCH Request Body**: Same as create, but all fields optional
- **DELETE Response (204 No Content)**: Empty response

### Apiaries Endpoints

#### 9. List/Create Apiaries
- **URL**: `GET/POST /api/apiaries/apiaries/`
- **Purpose**: List user's apiaries or create new apiary
- **Authentication**: Required (Bearer token)
- **Query Parameters** (GET):
  - `search` - Search in name, address, description
  - `ordering` - Order by: name, created_at, updated_at (add `-` for descending)
  - `beekeeper` - Filter by beekeeper profile ID
- **GET Response (200 OK)**:
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "uuid",
        "beekeeper": {
          "id": "uuid",
          "user": {
            "id": "uuid",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe"
          },
          "experience_level": "Intermediate"
        },
        "name": "North Field Apiary",
        "latitude": "40.12345678",
        "longitude": "-74.12345678",
        "coordinates": [40.12345678, -74.12345678],
        "address": "123 Farm Road, City, State",
        "description": "Main production apiary with 10 hives",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
      }
    ]
  }
  ```
- **POST Request Body**:
  ```json
  {
    "name": "North Field Apiary", // Required
    "latitude": "40.12345678", // Required
    "longitude": "-74.12345678", // Required
    "address": "123 Farm Road, City, State", // Optional
    "description": "Main production apiary with 10 hives" // Optional
  }
  ```

#### 10. Get/Update/Delete Specific Apiary
- **URL**: `GET/PATCH/DELETE /api/apiaries/apiaries/{apiary_id}/`
- **Purpose**: Retrieve, update, or delete specific apiary
- **Authentication**: Required (Bearer token)
- **GET Response (200 OK)**:
  ```json
  {
    "id": "uuid",
    "beekeeper": {
      "id": "uuid",
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe"
      },
      "experience_level": "Intermediate"
    },
    "name": "North Field Apiary",
    "latitude": "40.12345678",
    "longitude": "-74.12345678",
    "coordinates": [40.12345678, -74.12345678],
    "address": "123 Farm Road, City, State",
    "description": "Main production apiary with 10 hives",
    "hives": [
      {
        "id": "uuid",
        "name": "Hive 001",
        "hive_type": "Langstroth",
        "installation_date": "2024-05-01",
        "has_smart_device": true,
        "is_active": true,
        "created_at": "2024-05-01T00:00:00Z",
        "updated_at": "2024-05-01T00:00:00Z"
      }
    ],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
  ```
- **PATCH Request Body** (only include fields to update):
  ```json
  {
    "name": "Updated Apiary Name",
    "description": "Updated description"
  }
  ```
- **DELETE Response (204 No Content)**: Empty response (soft delete)

#### 11. Get Apiary Statistics
- **URL**: `GET /api/apiaries/apiaries/{apiary_id}/stats/`
- **Purpose**: Get statistics for specific apiary
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  {
    "total_hives": 10,
    "active_hives": 8,
    "inactive_hives": 2,
    "smart_hives": 5,
    "hive_types": {
      "Langstroth": 7,
      "Top Bar": 2,
      "Warre": 1
    }
  }
  ```

#### 12. Soft Delete Apiary
- **URL**: `POST /api/apiaries/apiaries/{apiary_id}/soft_delete/`
- **Purpose**: Soft delete an apiary (marks as deleted but keeps data)
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  {
    "message": "Apiary soft deleted successfully"
  }
  ```

### Hives Endpoints

#### 13. List/Create Hives
- **URL**: `GET/POST /api/apiaries/hives/`
- **Purpose**: List user's hives or create new hive
- **Authentication**: Required (Bearer token)
- **Query Parameters** (GET):
  - `search` - Search in name
  - `ordering` - Order by: name, installation_date, created_at, updated_at (add `-` for descending)
  - `apiary` - Filter by apiary ID
  - `hive_type` - Filter by hive type
  - `has_smart_device` - Filter by smart device presence (true/false)
  - `is_active` - Filter by active status (true/false)
- **GET Response (200 OK)**:
  ```json
  {
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "uuid",
        "apiary": {
          "id": "uuid",
          "name": "North Field Apiary",
          "latitude": "40.12345678",
          "longitude": "-74.12345678",
          "coordinates": [40.12345678, -74.12345678]
        },
        "name": "Hive 001",
        "hive_type": "Langstroth",
        "installation_date": "2024-05-01",
        "has_smart_device": true,
        "is_active": true,
        "created_at": "2024-05-01T00:00:00Z",
        "updated_at": "2024-05-01T00:00:00Z"
      }
    ]
  }
  ```
- **POST Request Body**:
  ```json
  {
    "apiary": "apiary_uuid", // Required: UUID of the apiary
    "name": "Hive 001", // Required
    "hive_type": "Langstroth", // Required: Langstroth/Top Bar/Warre/Flow Hive/Other
    "installation_date": "2024-05-01", // Required: YYYY-MM-DD format
    "has_smart_device": true, // Optional: default false
    "is_active": true // Optional: default true
  }
  ```

#### 14. Get/Update/Delete Specific Hive
- **URL**: `GET/PATCH/DELETE /api/apiaries/hives/{hive_id}/`
- **Purpose**: Retrieve, update, or delete specific hive
- **Authentication**: Required (Bearer token)
- **GET Response (200 OK)**:
  ```json
  {
    "id": "uuid",
    "apiary": {
      "id": "uuid",
      "name": "North Field Apiary",
      "latitude": "40.12345678",
      "longitude": "-74.12345678",
      "coordinates": [40.12345678, -74.12345678],
      "address": "123 Farm Road, City, State",
      "description": "Main production apiary"
    },
    "name": "Hive 001",
    "hive_type": "Langstroth",
    "installation_date": "2024-05-01",
    "has_smart_device": true,
    "is_active": true,
    "created_at": "2024-05-01T00:00:00Z",
    "updated_at": "2024-05-01T00:00:00Z"
  }
  ```
- **PATCH Request Body** (only include fields to update):
  ```json
  {
    "name": "Updated Hive Name",
    "hive_type": "Top Bar",
    "has_smart_device": false
  }
  ```
- **DELETE Response (204 No Content)**: Empty response (soft delete)

#### 15. Activate/Deactivate Hive
- **URL**: `POST /api/apiaries/hives/{hive_id}/activate/`
- **URL**: `POST /api/apiaries/hives/{hive_id}/deactivate/`
- **Purpose**: Activate or deactivate a hive
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  {
    "message": "Hive activated successfully"
  }
  ```
  ```json
  {
    "message": "Hive deactivated successfully"
  }
  ```

#### 16. Soft Delete Hive
- **URL**: `POST /api/apiaries/hives/{hive_id}/soft_delete/`
- **Purpose**: Soft delete a hive (marks as deleted but keeps data)
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  {
    "message": "Hive soft deleted successfully"
  }
  ```

#### 17. Get Hives by Type
- **URL**: `GET /api/apiaries/hives/by_type/`
- **Purpose**: Get hives grouped by hive type
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  {
    "Langstroth": [
      {
        "id": "uuid",
        "name": "Hive 001",
        "apiary": {
          "id": "uuid",
          "name": "North Field Apiary"
        },
        "installation_date": "2024-05-01",
        "has_smart_device": true,
        "is_active": true
      }
    ],
    "Top Bar": [
      {
        "id": "uuid",
        "name": "Hive 002",
        "apiary": {
          "id": "uuid",
          "name": "South Field Apiary"
        },
        "installation_date": "2024-06-01",
        "has_smart_device": false,
        "is_active": true
      }
    ]
  }
  ```

## Authentication

The API uses JWT (JSON Web Token) authentication:

### Headers Required for Authenticated Endpoints
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token Lifetime
- **Access Token**: 60 minutes
- **Refresh Token**: 1 day

### Error Responses

#### 400 Bad Request
```json
{
  "field_name": ["Error message for this field"],
  "non_field_errors": ["General error messages"]
}
```

#### 401 Unauthorized
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

#### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

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
