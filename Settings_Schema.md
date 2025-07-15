# Smart-Nyuki App - Settings Schema

Version 1.0

## 7. Settings Management

### UserSettings

```
id (UUID, PK)
user_id (UUID, FK → Users)
timezone (VARCHAR(50), default: 'UTC')
language (VARCHAR(10), default: 'en')
temperature_unit (ENUM: Celsius/Fahrenheit, default: 'Celsius')
weight_unit (ENUM: Kilograms/Pounds, default: 'Kilograms')
date_format (ENUM: DD/MM/YYYY/MM/DD/YYYY/YYYY-MM-DD, default: 'DD/MM/YYYY')
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### AlertThresholds

```
id (UUID, PK)
user_id (UUID, FK → Users)
hive_id (UUID, FK → Hives, NULL) # NULL means global setting for all hives
temperature_min (DECIMAL(5,2), default: 32.0)
temperature_max (DECIMAL(5,2), default: 38.0)
humidity_min (DECIMAL(5,2), default: 40.0)
humidity_max (DECIMAL(5,2), default: 70.0)
weight_change_threshold (DECIMAL(6,2), default: 2.0) # Daily weight change alert
sound_level_threshold (INT, default: 85)
battery_warning_level (INT, default: 20) # Battery percentage
inspection_reminder_days (INT, default: 7) # Days before inspection due
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### NotificationSettings

```
id (UUID, PK)
user_id (UUID, FK → Users)
push_notifications (BOOLEAN, default: TRUE)
email_notifications (BOOLEAN, default: TRUE)
sms_notifications (BOOLEAN, default: FALSE)
alert_sound (BOOLEAN, default: TRUE)
quiet_hours_start (TIME, default: '22:00')
quiet_hours_end (TIME, default: '06:00')
critical_alerts_override_quiet (BOOLEAN, default: TRUE)
daily_summary_enabled (BOOLEAN, default: TRUE)
daily_summary_time (TIME, default: '08:00')
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### DataSyncSettings

```
id (UUID, PK)
user_id (UUID, FK → Users)
auto_sync_enabled (BOOLEAN, default: TRUE)
sync_frequency (ENUM: Real-time/Hourly/Daily, default: 'Hourly')
wifi_only_sync (BOOLEAN, default: FALSE)
backup_enabled (BOOLEAN, default: TRUE)
backup_frequency (ENUM: Daily/Weekly/Monthly, default: 'Weekly')
data_retention_days (INT, default: 365) # How long to keep sensor data
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### PrivacySettings

```
id (UUID, PK)
user_id (UUID, FK → Users)
location_sharing (BOOLEAN, default: FALSE)
analytics_enabled (BOOLEAN, default: TRUE)
crash_reporting (BOOLEAN, default: TRUE)
data_sharing_research (BOOLEAN, default: FALSE)
profile_visibility (ENUM: Private/Public/Community, default: 'Private')
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

## Key Features:

1. **Alert Thresholds**: Customizable sensor value ranges for temperature, humidity, weight changes, and sound levels
2. **Notification Preferences**: Control how and when users receive alerts (push, email, SMS, quiet hours)
3. **Data & Sync**: Configure automatic syncing, backup preferences, and data retention
4. **Units & Display**: Language, timezone, measurement units, and date formats
5. **Privacy Controls**: Location sharing, analytics, and profile visibility settings

## Implementation Notes:

- AlertThresholds can be set globally (hive_id = NULL) or per-hive
- Users can override global thresholds for specific hives
- Quiet hours prevent non-critical notifications during specified times
- Data retention settings help manage storage and performance
- All settings have sensible defaults for new users
