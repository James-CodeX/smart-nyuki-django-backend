# Smart Nyuki Backend API - Stage 1: Accounts App

## Project Overview
The Smart Nyuki system is implemented in stages:
1. **Stage 1: Accounts (User Management)** ✅ IMPLEMENTED

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

### API Endpoints

#### Authentication Endpoints

##### 1. User Registration
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

##### 2. User Login
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

##### 3. Token Refresh
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

##### 4. User Logout
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

#### User Profile Endpoints

##### 5. Get/Update User Profile
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

##### 6. Change Password
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

#### Beekeeper Profile Endpoints

##### 7. List/Create Beekeeper Profiles
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

##### 8. Get/Update/Delete Specific Beekeeper Profile
- **URL**: `GET/PATCH/DELETE /api/accounts/beekeeper-profiles/{profile_id}/`
- **Purpose**: Retrieve, update, or delete specific beekeeper profile
- **Authentication**: Required (Bearer token)
- **GET/PATCH Response**: Same as individual profile object above
- **PATCH Request Body**: Same as create, but all fields optional
- **DELETE Response (204 No Content)**: Empty response

---