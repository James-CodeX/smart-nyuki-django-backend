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
  - `timestamp` (DateTime, Optional, When reading was taken - auto-generated if not provided)
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
      "status_code": 1
    }
    ```
    **Note**: The `timestamp` field is optional. If not provided, it will be automatically set to the current time.

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

## Frontend Development Issues & Solutions

### Issue: Smart Devices Showing "Unknown Hive" and "Unknown Apiary"

**Problem**: When displaying smart devices in the frontend, some devices show "Unknown Hive" and "Unknown Apiary" even though they are properly assigned in the backend.

**Root Cause**: The frontend is not correctly reading the `hive_name` and `apiary_name` fields from the API response.

**Backend API Response Structure**:
The Smart Devices API returns the following structure:
```json
{
  "id": "device-uuid",
  "serial_number": "ACSITR123",
  "device_type": "v01",
  "hive": "hive-uuid",
  "hive_name": "Hive 1",
  "apiary_name": "Ruai Apiary",
  "beekeeper_name": "JAMES KARANJA",
  "battery_level": 100,
  "is_active": true,
  "created_at": "2025-07-03T09:57:01.873699Z"
}
```

**Frontend Solution**:
1. **Correct Field Mapping**: Ensure your frontend code reads `hive_name` and `apiary_name` from the API response:
   ```javascript
   // ✅ Correct way
   const hiveName = device.hive_name || 'Unassigned';
   const apiaryName = device.apiary_name || 'No Apiary';
   
   // ❌ Wrong way - don't use hardcoded values
   const hiveName = device.hive ? device.hive.name : 'Unknown Hive';
   ```

2. **Handle Null/Undefined Values**: When a device is not assigned to a hive:
   ```javascript
   const displayHive = device.hive_name || 'Unassigned';
   const displayApiary = device.apiary_name || 'No Apiary';
   ```

3. **API Field Reference**: Use these exact field names from the API response:
   - `hive_name` - Name of the assigned hive
   - `apiary_name` - Name of the apiary containing the hive
   - `beekeeper_name` - Full name of the device owner
   - `serial_number` - Device identifier
   - `device_type` - Device model/version
   - `battery_level` - Current battery percentage (0-100)
   - `is_active` - Device status (boolean)

4. **Error Handling**: Add proper error handling for API responses:
   ```javascript
   try {
     const response = await fetch('/api/devices/devices/', {
       headers: {
         'Authorization': `Bearer ${accessToken}`,
         'Content-Type': 'application/json'
       }
     });
     
     if (response.ok) {
       const data = await response.json();
       // Use data.results for paginated responses
       const devices = data.results || data;
       
       devices.forEach(device => {
         console.log(`Device: ${device.serial_number}`);
         console.log(`Hive: ${device.hive_name || 'Unassigned'}`);
         console.log(`Apiary: ${device.apiary_name || 'No Apiary'}`);
       });
     }
   } catch (error) {
     console.error('Failed to fetch devices:', error);
   }
   ```

### Device Assignment Best Practices

1. **When Creating Devices**: Always provide a `hive` UUID if you want to assign the device:
   ```json
   {
     "serial_number": "NEW_DEVICE_123",
     "device_type": "Temperature Sensor",
     "hive": "hive-uuid-here"
   }
   ```

2. **When Updating Device Assignment**: Use PATCH to update the hive assignment:
   ```json
   {
     "hive": "new-hive-uuid"
   }
   ```

3. **To Unassign a Device**: Set hive to null:
   ```json
   {
     "hive": null
   }
   ```

### Key Points for Frontend Implementation

1. **Always fetch available hives after apiary selection** - Don't assume all hives are available
2. **Handle the "Leave unassigned" option** - This is represented as `null` in the API
3. **Show hive information** - Display hive type and installation date to help users choose
4. **Provide loading states** - Show loading indicators while fetching available hives
5. **Handle edge cases** - What if no hives are available in the selected apiary?
6. **Validate on submit** - Ensure required fields are filled before submission

### API Integration Summary

- **GET apiaries**: `/api/apiaries/apiaries/` - Get user's apiaries for the dropdown
- **GET available hives**: `/api/apiaries/apiaries/{apiary_id}/available_hives/` - Get assignable hives
- **POST create device**: `/api/devices/devices/` - Create the device with optional hive assignment
- **GET devices**: `/api/devices/devices/` - Verify the created device shows correct hive/apiary names
