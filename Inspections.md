# Smart Nyuki Backend API - Stage 4: Inspections

This document provides comprehensive documentation for Stage 4 implementation of the Smart Nyuki Backend API, focusing on inspection management functionality.

## Overview

Stage 4 introduces inspection management capabilities that allow beekeepers to:
- Schedule hive inspections
- Create detailed inspection reports
- Track colony health over time
- Monitor inspection completion rates
- Analyze inspection trends and statistics

## Models

### InspectionSchedules
Manages scheduled hive inspections.

**Database Table**: `inspection_schedules`

**Fields**:
- `id` (UUID, Primary Key) - Auto-generated
- `hive` (ForeignKey to Hives) - Associated hive
- `scheduled_date` (Date, Required) - When inspection is scheduled
- `notes` (Text, Optional) - Notes or instructions for inspection
- `is_completed` (Boolean, Default: False) - Completion status
- `weather_conditions` (String, Optional) - Weather conditions for inspection
- `created_at` (DateTime, Auto) - Creation timestamp
- `updated_at` (DateTime, Auto) - Last update timestamp

### InspectionReports
Stores completed hive inspection reports.

**Database Table**: `inspection_reports`

**Fields**:
- `id` (UUID, Primary Key) - Auto-generated
- `schedule` (ForeignKey to InspectionSchedules, Optional) - Linked schedule
- `hive` (ForeignKey to Hives) - Associated hive
- `inspector` (ForeignKey to User) - User who conducted inspection
- `inspection_date` (Date, Required) - Date inspection was conducted
- `queen_present` (Boolean, Optional) - Whether queen was observed
- `honey_level` (Choice, Required) - Low/Medium/High
- `colony_health` (Choice, Required) - Poor/Fair/Good/Excellent
- `varroa_mite_count` (Integer, Optional) - Number of mites observed
- `brood_pattern` (Choice, Required) - Solid/Spotty/None
- `pest_observations` (Text, Optional) - Pest and disease observations
- `actions_taken` (Text, Optional) - Actions performed during inspection
- `notes` (Text, Optional) - Additional inspection notes
- `created_at` (DateTime, Auto) - Creation timestamp

## API Endpoints

### Inspection Schedules

#### 1. List/Create Inspection Schedules
- **URL**: `GET/POST /api/inspections/schedules/`
- **Purpose**: List user's inspection schedules or create new schedule
- **Authentication**: Required (Bearer token)
- **Query Parameters** (GET):
  - `scheduled_date` - Filter by exact date
  - `scheduled_date_from` - Filter from date
  - `scheduled_date_to` - Filter to date
  - `is_completed` - Filter by completion status (true/false)
  - `is_overdue` - Filter overdue schedules (true/false)
  - `is_upcoming` - Filter upcoming schedules in next 7 days (true/false)
  - `hive` - Filter by hive ID
  - `hive_name` - Filter by hive name (partial match)
  - `apiary` - Filter by apiary ID
  - `apiary_name` - Filter by apiary name (partial match)
  - `weather_conditions` - Filter by weather conditions (partial match)
  - `search` - Search in notes, hive name, apiary name
  - `ordering` - Order by: scheduled_date, created_at, updated_at (add `-` for descending)

- **GET Response (200 OK)**:
  ```json
  {
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "uuid",
        "hive": {
          "id": "uuid",
          "name": "Hive 001",
          "apiary": {
            "id": "uuid",
            "name": "North Field Apiary",
            "latitude": "40.12345678",
            "longitude": "-74.12345678"
          },
          "type": "Langstroth",
          "type_display": "Langstroth",
          "installation_date": "2024-05-01",
          "has_smart_device": true,
          "is_active": true
        },
        "scheduled_date": "2025-07-10",
        "notes": "Monthly routine inspection",
        "is_completed": false,
        "weather_conditions": "Sunny, 22°C",
        "created_at": "2025-07-01T10:00:00Z",
        "updated_at": "2025-07-01T10:00:00Z"
      }
    ]
  }
  ```

- **POST Request Body**:
  ```json
  {
    "hive": "hive_uuid", // Required: UUID of the hive
    "scheduled_date": "2025-07-10", // Required: YYYY-MM-DD format (cannot be in past)
    "notes": "Monthly routine inspection", // Optional
    "weather_conditions": "Sunny, 22°C" // Optional
  }
  ```

#### 2. Get/Update/Delete Specific Inspection Schedule
- **URL**: `GET/PATCH/DELETE /api/inspections/schedules/{schedule_id}/`
- **Purpose**: Retrieve, update, or delete specific inspection schedule
- **Authentication**: Required (Bearer token)
- **GET Response (200 OK)**: Same as individual schedule object above
- **PATCH Request Body** (only include fields to update):
  ```json
  {
    "scheduled_date": "2025-07-15",
    "notes": "Updated inspection notes",
    "weather_conditions": "Cloudy, 18°C"
  }
  ```
- **DELETE Response (204 No Content)**: Empty response

#### 3. Mark Schedule as Complete
- **URL**: `POST /api/inspections/schedules/{schedule_id}/complete/`
- **Purpose**: Mark an inspection schedule as completed or incomplete
- **Authentication**: Required (Bearer token)
- **Request Body**:
  ```json
  {
    "is_completed": true, // Required: true or false
    "notes": "Inspection completed successfully" // Optional: update notes
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "message": "Inspection schedule completed",
    "is_completed": true
  }
  ```

#### 4. Get Upcoming Inspections
- **URL**: `GET /api/inspections/schedules/upcoming/`
- **Purpose**: Get upcoming inspections for the next 7 days
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  {
    "count": 3,
    "results": [
      // Array of schedule objects
    ]
  }
  ```

#### 5. Get Overdue Inspections
- **URL**: `GET /api/inspections/schedules/overdue/`
- **Purpose**: Get overdue inspections (past due and not completed)
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  {
    "count": 2,
    "results": [
      // Array of schedule objects
    ]
  }
  ```

#### 6. Get Schedule Statistics
- **URL**: `GET /api/inspections/schedules/statistics/`
- **Purpose**: Get inspection schedule statistics
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  {
    "total_schedules": 20,
    "completed_schedules": 15,
    "pending_schedules": 3,
    "overdue_schedules": 2,
    "completion_rate": 75.0
  }
  ```

### Inspection Reports

#### 7. List/Create Inspection Reports
- **URL**: `GET/POST /api/inspections/reports/`
- **Purpose**: List user's inspection reports or create new report
- **Authentication**: Required (Bearer token)
- **Query Parameters** (GET):
  - `inspection_date` - Filter by exact date
  - `inspection_date_from` - Filter from date
  - `inspection_date_to` - Filter to date
  - `inspector` - Filter by inspector user ID
  - `inspector_name` - Filter by inspector name (partial match)
  - `hive` - Filter by hive ID
  - `hive_name` - Filter by hive name (partial match)
  - `apiary` - Filter by apiary ID
  - `apiary_name` - Filter by apiary name (partial match)
  - `queen_present` - Filter by queen presence (true/false)
  - `honey_level` - Filter by honey level (Low/Medium/High)
  - `colony_health` - Filter by colony health (Poor/Fair/Good/Excellent)
  - `brood_pattern` - Filter by brood pattern (Solid/Spotty/None)
  - `varroa_mite_count` - Filter by exact mite count
  - `varroa_mite_count_min` - Filter by minimum mite count
  - `varroa_mite_count_max` - Filter by maximum mite count
  - `is_recent` - Filter recent reports (last 30 days) (true/false)
  - `has_schedule` - Filter reports with/without linked schedules (true/false)
  - `search` - Search in notes, pest observations, actions taken, hive/apiary names
  - `ordering` - Order by: inspection_date, created_at, colony_health, honey_level (add `-` for descending)

- **GET Response (200 OK)**:
  ```json
  {
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "uuid",
        "schedule": {
          "id": "uuid",
          "scheduled_date": "2025-07-10",
          "is_completed": true
        },
        "hive": {
          "id": "uuid",
          "name": "Hive 001",
          "apiary": {
            "id": "uuid",
            "name": "North Field Apiary"
          }
        },
        "inspector": {
          "id": "uuid",
          "email": "inspector@example.com",
          "first_name": "John",
          "last_name": "Doe",
          "full_name": "John Doe"
        },
        "inspection_date": "2025-07-10",
        "queen_present": true,
        "honey_level": "High",
        "honey_level_display": "High",
        "colony_health": "Good",
        "colony_health_display": "Good",
        "varroa_mite_count": 2,
        "brood_pattern": "Solid",
        "brood_pattern_display": "Solid",
        "pest_observations": "No significant pest issues observed",
        "actions_taken": "Added honey super",
        "notes": "Colony is thriving, good brood pattern",
        "created_at": "2025-07-10T15:30:00Z"
      }
    ]
  }
  ```

- **POST Request Body**:
  ```json
  {
    "schedule": "schedule_uuid", // Optional: Link to existing schedule
    "hive": "hive_uuid", // Required: UUID of the hive
    "inspection_date": "2025-07-10", // Required: YYYY-MM-DD format (cannot be future)
    "queen_present": true, // Optional: true/false/null
    "honey_level": "High", // Required: Low/Medium/High
    "colony_health": "Good", // Required: Poor/Fair/Good/Excellent
    "varroa_mite_count": 2, // Optional: Integer >= 0
    "brood_pattern": "Solid", // Required: Solid/Spotty/None
    "pest_observations": "No significant pest issues", // Optional
    "actions_taken": "Added honey super", // Optional
    "notes": "Colony is thriving" // Optional
  }
  ```

#### 8. Get/Update/Delete Specific Inspection Report
- **URL**: `GET/PATCH/DELETE /api/inspections/reports/{report_id}/`
- **Purpose**: Retrieve, update, or delete specific inspection report
- **Authentication**: Required (Bearer token)
- **GET Response (200 OK)**: Same as individual report object above
- **PATCH Request Body** (only include fields to update):
  ```json
  {
    "honey_level": "Medium",
    "colony_health": "Excellent",
    "notes": "Updated assessment after second look"
  }
  ```
- **DELETE Response (204 No Content)**: Empty response

#### 9. Get Recent Reports
- **URL**: `GET /api/inspections/reports/recent/`
- **Purpose**: Get recent inspection reports from the last 30 days
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  {
    "count": 8,
    "results": [
      // Array of report objects
    ]
  }
  ```

#### 10. Get Reports by Hive
- **URL**: `GET /api/inspections/reports/by-hive/{hive_id}/`
- **Purpose**: Get all inspection reports for a specific hive
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**: Paginated list of report objects for the hive

#### 11. Get Report Statistics
- **URL**: `GET /api/inspections/reports/statistics/`
- **Purpose**: Get inspection report statistics
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  {
    "total_reports": 50,
    "reports_this_month": 12,
    "average_colony_health": "Good",
    "queen_presence_rate": 92.5,
    "health_distribution": {
      "excellent_count": 15,
      "good_count": 20,
      "fair_count": 12,
      "poor_count": 3
    }
  }
  ```

#### 12. Get Health Trends
- **URL**: `GET /api/inspections/reports/health-trends/`
- **Purpose**: Get colony health trends over time grouped by month
- **Authentication**: Required (Bearer token)
- **Response (200 OK)**:
  ```json
  [
    {
      "month": "2025-06",
      "total_reports": 10,
      "excellent_count": 3,
      "good_count": 5,
      "fair_count": 2,
      "poor_count": 0
    },
    {
      "month": "2025-07",
      "total_reports": 8,
      "excellent_count": 4,
      "good_count": 3,
      "fair_count": 1,
      "poor_count": 0
    }
  ]
  ```

## Required Fields Summary

### Creating Inspection Schedule
**Required Fields**:
- `hive` (UUID) - Must be a hive owned by the current user
- `scheduled_date` (Date) - Cannot be in the past

**Optional Fields**:
- `notes` (Text)
- `weather_conditions` (String)

### Creating Inspection Report
**Required Fields**:
- `hive` (UUID) - Must be a hive owned by the current user
- `inspection_date` (Date) - Cannot be in the future
- `honey_level` (Choice) - Low/Medium/High
- `colony_health` (Choice) - Poor/Fair/Good/Excellent
- `brood_pattern` (Choice) - Solid/Spotty/None

**Optional Fields**:
- `schedule` (UUID) - Link to existing schedule
- `queen_present` (Boolean)
- `varroa_mite_count` (Integer) - Must be >= 0 if provided
- `pest_observations` (Text)
- `actions_taken` (Text)
- `notes` (Text)

## Validation Rules

### Inspection Schedules
1. User must have a beekeeper profile
2. Scheduled date cannot be in the past
3. User can only schedule inspections for their own hives
4. Hive must belong to user's apiaries

### Inspection Reports
1. User must have a beekeeper profile
2. Inspection date cannot be in the future
3. User can only create reports for their own hives
4. If schedule is linked, it must be for the same hive
5. Varroa mite count must be non-negative if provided
6. Inspector is automatically set to current user
7. Linked schedule is automatically marked as completed when report is created

## Permissions

- All endpoints require authentication
- Users can only access schedules and reports for their own hives
- Inspection reports can be accessed by either the inspector who created them or the hive owner
- Users must have a beekeeper profile to create schedules or reports

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message for this field"],
  "non_field_errors": ["General error messages"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Given token not valid for any token type"
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Frontend Integration Notes

### State Management Recommendations
- Cache inspection schedules and reports locally
- Implement real-time updates for schedule completion
- Store filter preferences for reports and schedules
- Handle offline mode for field inspections

### Form Validation
- Validate dates on client side before API calls
- Provide dropdown selections for choice fields
- Show validation errors inline with form fields
- Auto-complete for hive selection based on user's apiaries

### User Experience Features
- Calendar view for inspection schedules
- Push notifications for upcoming/overdue inspections
- Quick actions for marking schedules complete
- Batch operations for multiple schedules
- Photo upload capability for inspection reports
- Export functionality for reports

### Mobile Considerations
- Optimize forms for mobile input
- Enable offline inspection data entry
- GPS integration for location verification
- Voice-to-text for inspection notes
- Barcode/QR code scanning for hive identification

This completes the Stage 4 implementation of the Smart Nyuki Backend API with full inspection management capabilities.
