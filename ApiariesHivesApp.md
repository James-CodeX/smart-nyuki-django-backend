# Smart Nyuki Backend API - Stage 2: Apiaries App

## Project Overview
The Smart Nyuki system is implemented in stages:
1. **Stage 2: Apiaries (Beekeeping Structure)** ✅ IMPLEMENTED

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

### API Endpoints

#### Apiaries Endpoints

##### 9. List/Create Apiaries
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
        "hives_count": 8,
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

##### 10. Get/Update/Delete Specific Apiary
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
    "hives_count": 8,
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

##### 11. Get Apiary Statistics
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

##### 12. Soft Delete Apiary
- **URL**: `POST /api/apiaries/apiaries/{apiary_id}/soft_delete/`
- **Purpose**: Soft delete an apiary (marks as deleted but keeps data)
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  {
    "message": "Apiary soft deleted successfully"
  }
  ```

#### Hives Endpoints

##### 13. List/Create Hives
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

##### 14. Get/Update/Delete Specific Hive
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

##### 15. Activate/Deactivate Hive
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

##### 16. Soft Delete Hive
- **URL**: `POST /api/apiaries/hives/{hive_id}/soft_delete/`
- **Purpose**: Soft delete a hive (marks as deleted but keeps data)
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  {
    "message": "Hive soft deleted successfully"
  }
  ```

##### 17. Get Hives by Type
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