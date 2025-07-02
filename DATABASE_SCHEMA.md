Smart-Nyuki App - Complete Database Design (List Format)
Version 2.0 - Enhanced Structure

App Structure:

1. accounts (User Management)
   Users model
   BeekeeperProfile model
   Authentication, registration, profile management
   User-related views and APIs
2. apiaries (Beekeeping Structure)
   Apiaries model
   Hives model
   Core beekeeping structure management
   Hive and apiary CRUD operations
3. devices (Smart Device Management)
   SmartDevices model
   SensorReadings model
   AudioRecordings model
   DeviceImages model
   Device data collection and management
4. inspections (Inspection Management)
   InspectionSchedules model
   InspectionReports model
   Inspection scheduling and reporting functionality
5. production (Production & Monitoring)
   Harvests model
   Alerts model
   Harvest tracking and alert management

MODELS

1. User Management
   Users
   id (UUID, PK)

email (VARCHAR(255), UNIQUE)

password_hash (TEXT)

first_name (VARCHAR(100))

last_name (VARCHAR(100))

phone_number (VARCHAR(20), optional)

is_active (BOOLEAN)

created_at (TIMESTAMP)

updated_at (TIMESTAMP)

deleted_at (TIMESTAMP, NULL)

BeekeeperProfile
id (UUID, PK)

user_id (UUID, FK → Users)

latitude (DECIMAL(10, 8))

longitude (DECIMAL(11, 8))

address (TEXT, optional)

experience_level (ENUM: Beginner/Intermediate/Advanced/Expert)

established_date (DATE)

app_start_date (DATE)

certification_details (TEXT, optional)

profile_picture_url (TEXT, optional)

notes (TEXT, optional)

created_at (TIMESTAMP)

updated_at (TIMESTAMP)

2. Beekeeping Structure
   Apiaries
   id (UUID, PK)

beekeeper_id (UUID, FK → BeekeeperProfile)

name (VARCHAR(100))

latitude (DECIMAL(10, 8))

longitude (DECIMAL(11, 8))

address (TEXT, optional)

description (TEXT, optional)

created_at (TIMESTAMP)

deleted_at (TIMESTAMP, NULL)

Hives
id (UUID, PK)

apiary_id (UUID, FK → Apiaries)

name (VARCHAR(100))

hive_type (ENUM: Langstroth/Top-Bar/Warre/Other)

installation_date (DATE)

has_smart_device (BOOLEAN)

is_active (BOOLEAN)

created_at (TIMESTAMP)

deleted_at (TIMESTAMP, NULL)

3. Smart Device Management
   SmartDevices
   id (UUID, PK)

serial_number (VARCHAR(100), UNIQUE)

hive_id (UUID, FK → Hives, NULL)

device_type (VARCHAR(50))

last_sync_at (TIMESTAMP, NULL)

battery_level (INT, NULL)

is_active (BOOLEAN)

created_at (TIMESTAMP)

SensorReadings
id (UUID, PK)

device_id (UUID, FK → SmartDevices)

temperature (DECIMAL(5,2))

humidity (DECIMAL(5,2))

weight (DECIMAL(6,2))

sound_level (INT, optional)

battery_level (INT, NULL)

status_code (INT, NULL)

timestamp (TIMESTAMP)

created_at (TIMESTAMP)

AudioRecordings
id (UUID, PK)

device_id (UUID, FK → SmartDevices)

file_path (TEXT)

duration (INT)

file_size (INT)

recorded_at (TIMESTAMP)

upload_status (ENUM: Pending/Uploaded/Failed)

analysis_status (ENUM: Pending/Processing/Completed/Failed)

is_analyzed (BOOLEAN)

analysis_results (JSON, NULL)

created_at (TIMESTAMP)

DeviceImages
id (UUID, PK)

device_id (UUID, FK → SmartDevices)

file_path (TEXT)

captured_at (TIMESTAMP)

image_type (ENUM: Routine/Alert-Triggered/Manual)

upload_status (ENUM: Pending/Uploaded/Failed)

analysis_status (ENUM: Pending/Processing/Completed/Failed)

is_analyzed (BOOLEAN)

analysis_results (JSON, NULL)

created_at (TIMESTAMP)

4. Inspections
   InspectionSchedules
   id (UUID, PK)

hive_id (UUID, FK → Hives)

scheduled_date (DATE)

notes (TEXT, optional)

is_completed (BOOLEAN)

weather_conditions (VARCHAR(100), optional)

created_at (TIMESTAMP)

updated_at (TIMESTAMP, NULL)

InspectionReports
id (UUID, PK)

schedule_id (UUID, FK → InspectionSchedules, NULL)

hive_id (UUID, FK → Hives)

inspector_id (UUID, FK → Users)

inspection_date (DATE)

queen_present (BOOLEAN, NULL)

honey_level (ENUM: Low/Medium/High)

colony_health (ENUM: Poor/Fair/Good/Excellent)

varroa_mite_count (INT, NULL)

brood_pattern (ENUM: Solid/Spotty/None)

pest_observations (TEXT, optional)

actions_taken (TEXT, optional)

notes (TEXT, optional)

created_at (TIMESTAMP)

5. Production
   Harvests
   id (UUID, PK)

hive_id (UUID, FK → Hives)

harvest_date (DATE)

honey_kg (DECIMAL(5,2))

wax_kg (DECIMAL(4,2), optional)

pollen_kg (DECIMAL(4,2), optional)

processing_method (VARCHAR(100), optional)

harvested_by (UUID, FK → Users)

quality_notes (TEXT, optional)

created_at (TIMESTAMP)

6. Alerts & Notifications
   Alerts
   id (UUID, PK)

hive_id (UUID, FK → Hives)

alert_type (ENUM: Temperature/Humidity/Weight/Inspection_Due/Pest_Risk/Swarm_Risk)

message (TEXT)

severity (ENUM: Low/Medium/High/Critical)

trigger_values (JSON, NULL)

is_resolved (BOOLEAN)

resolved_at (TIMESTAMP, NULL)

resolved_by (UUID, FK → Users, NULL)

resolution_notes (TEXT, optional)

created_at (TIMESTAMP)
