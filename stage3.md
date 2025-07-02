# Stage 3: Devices (Smart Device Management) - Frontend Integration Guide

## Overview

Stage 3 focuses on integrating smart device management within the Smart Nyuki system. This includes managing smart devices, sensor readings, audio recordings, and device images from hive monitoring devices.

## Table of Contents

- [Models](#models)
- [API Endpoints](#api-endpoints)
- [Required Fields Summary](#required-fields-summary)
- [Choice Field Options](#choice-field-options)
- [Error Handling](#error-handling)
- [Frontend Implementation Guidelines](#frontend-implementation-guidelines)
- [Sample API Responses](#sample-api-responses)

## Models

### SmartDevices

- **Purpose**: Manage IoT devices that monitor hives
- **Database Table**: `smart_devices`
- **Key Features**: Device registration, battery monitoring, hive association, beekeeper ownership
- **Fields**:
  - `id` (UUID, Primary Key, Auto-generated)
  - `serial_number` (String, Required, Unique, Max: 100 chars)
  - `beekeeper` (ForeignKey to BeekeeperProfile, Required, Device owner)
  - `hive` (ForeignKey to Hives, Optional, Can be null for unassigned devices)
  - `device_type` (String, like version 1 or even model, etc )
  - `last_sync_at` (DateTime, Optional, When device last synced data)
  - `battery_level` (Integer, Optional, Range: 0-100, Battery percentage)
  - `is_active` (Boolean, Default: True, Device operational status)
  - `created_at` (DateTime, Auto-generated)

### SensorReadings

- **Purpose**: Store real-time sensor data from smart devices
- **Database Table**: `sensor_readings`
- **Key Features**: Environmental monitoring, historical data tracking
- **Fields**:
  - `id` (UUID, Primary Key, Auto-generated)
  - `device` (ForeignKey to SmartDevices, Required)
  - `temperature` (Decimal, Required, Max digits: 5, Decimal places: 2, in Celsius)
  - `humidity` (Decimal, Required, Max digits: 5, Decimal places: 2, percentage)
  - `weight` (Decimal, Required, Max digits: 6, Decimal places: 2, in kg)
  - `sound_level` (Integer, Optional, in decibels)
  - `battery_level` (Integer, Optional, Range: 0-100, Device battery at time of reading)
  - `status_code` (Integer, Optional, Device status code)
  - `timestamp` (DateTime, Required, When reading was taken)
  - `created_at` (DateTime, Auto-generated)

### AudioRecordings

- **Purpose**: Manage audio files captured by smart devices for bee activity analysis
- **Database Table**: `audio_recordings`
- **Key Features**: Audio file tracking, analysis status, automated processing
- **Fields**:
  - `id` (UUID, Primary Key, Auto-generated)
  - `device` (ForeignKey to SmartDevices, Required)
  - `file_path` (Text, Required, Path to audio file)
  - `duration` (Integer, Required, Duration in seconds)
  - `file_size` (Integer, Required, File size in bytes)
  - `recorded_at` (DateTime, Required, When audio was recorded)
  - `upload_status` (Choice, Required, Default: "Pending")
  - `analysis_status` (Choice, Required, Default: "Pending")
  - `is_analyzed` (Boolean, Default: False, Whether analysis is complete)
  - `analysis_results` (JSON, Optional, Analysis output data)
  - `created_at` (DateTime, Auto-generated)

### DeviceImages

- **Purpose**: Manage images captured by smart devices for visual hive monitoring
- **Database Table**: `device_images`
- **Key Features**: Image categorization, analysis tracking, automated capture types
- **Fields**:
  - `id` (UUID, Primary Key, Auto-generated)
  - `device` (ForeignKey to SmartDevices, Required)
  - `file_path` (Text, Required, Path to image file)
  - `captured_at` (DateTime, Required, When image was captured)
  - `image_type` (Choice, Required, Default: "Routine")
  - `upload_status` (Choice, Required, Default: "Pending")
  - `analysis_status` (Choice, Required, Default: "Pending")
  - `is_analyzed` (Boolean, Default: False, Whether analysis is complete)
  - `analysis_results` (JSON, Optional, Analysis output data)
  - `created_at` (DateTime, Auto-generated)

## Endpoints

### Smart Devices

- **List/Create**

  - **URL**: `GET/POST /api/devices/devices/`
  - **Authentication**: Required (Bearer token)
  - **GET Response**: List devices
  - **POST Request Body**:
    ```json
    {
      "serial_number": "ABC123",
      "device_type": "Temperature Sensor",
      "hive": "hive_uuid"
    }
    ```

- **Detail/Update/Delete**

  - **URL**: `GET/PATCH/DELETE /api/devices/devices/{device_id}/`
  - **GET Response**: Device details
  - **PATCH Request Body**: Partial update

- **Statistics**
  - **URL**: `GET /api/devices/devices/{device_id}/stats/`
  - **Response**: Device statistics

### Sensor Readings

- **List/Create**

  - **URL**: `GET/POST /api/devices/sensor-readings/`
  - **POST Request Body**:
    ```json
    {
      "device_serial": "ABC123",
      "temperature": 35.5,
      "humidity": 60.0,
      "weight": 15.2,
      "sound_level": 70,
      "battery_level": 80,
      "status_code": 1,
      "timestamp": "2025-07-02T14:34:56Z"
    }
    ```

- **Detail**
  - **URL**: `GET /api/devices/sensor-readings/{reading_id}/`

### Audio Recordings

- **List/Create**

  - **URL**: `GET/POST /api/devices/audio-recordings/`
  - **POST Request Body**:
    ```json
    {
      "device": "device_uuid",
      "file_path": "path/to/audio/file.mp3",
      "duration": 120,
      "file_size": 1048576,
      "recorded_at": "2025-07-02T14:30:00Z",
      "upload_status": "Pending",
      "analysis_status": "Pending",
      "is_analyzed": false
    }
    ```

- **Detail/Update**
  - **URL**: `GET/PATCH /api/devices/audio-recordings/{recording_id}/`

### Device Images

- **List/Create**

  - **URL**: `GET/POST /api/devices/device-images/`
  - **POST Request Body**:
    ```json
    {
      "device": "device_uuid",
      "file_path": "path/to/image.jpg",
      "captured_at": "2025-07-02T14:40:00Z",
      "image_type": "Routine",
      "upload_status": "Uploaded",
      "analysis_status": "Completed",
      "is_analyzed": true
    }
    ```

- **Detail/Update**
  - **URL**: `GET/PATCH /api/devices/device-images/{image_id}/`

## Integration Guidelines

- Ensure the frontend captures required fields accurately.
- Use authentication tokens for accessing endpoints.
- Validate responses and handle errors effectively.
