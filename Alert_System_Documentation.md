# Smart Nyuki Alert System Documentation

## Overview

The Smart Nyuki Alert System is a comprehensive monitoring solution that automatically checks sensor readings from smart hives and creates alerts when threshold values are exceeded. The system is designed to run every 10 minutes to ensure timely detection of potential issues.

## Architecture

### Components

1. **AlertChecker Service** (`production/services/alert_checker.py`)
   - Core service that processes sensor readings
   - Compares readings against user-defined thresholds
   - Creates alerts when thresholds are exceeded
   - Implements intelligent severity calculation

2. **Django Management Command** (`production/management/commands/check_alerts.py`)
   - CLI command for manual alert checks
   - Supports checking all hives or specific hive
   - Provides verbose output for debugging

3. **Celery Tasks** (`production/tasks.py`)
   - Background task for periodic alert checking
   - Supports both system-wide and hive-specific checks
   - Includes automatic retry logic with exponential backoff

4. **API Endpoints** (`production/views.py`)
   - Manual alert check endpoints
   - Real-time alert statistics
   - Scheduled task management

## Alert Types

The system supports the following alert types:

### 1. Temperature Alerts
- **Monitors**: Hive internal temperature
- **Thresholds**: Min/Max temperature values (°C)
- **Severity Logic**: Based on deviation from threshold
  - Low: 1-2°C deviation
  - Medium: 3-4°C deviation  
  - High: 5-6°C deviation
  - Critical: >6°C deviation

### 2. Humidity Alerts
- **Monitors**: Hive internal humidity
- **Thresholds**: Min/Max humidity values (%)
- **Severity Logic**: Based on deviation from threshold
  - Low: 1-9% deviation
  - Medium: 10-14% deviation
  - High: 15-19% deviation
  - Critical: >20% deviation

### 3. Weight Change Alerts
- **Monitors**: Daily weight changes
- **Thresholds**: Maximum acceptable weight change (kg)
- **Severity Logic**: Based on multiple of threshold
  - Low: 1-1.5x threshold
  - Medium: 1.5-2x threshold
  - High: 2-3x threshold
  - Critical: >3x threshold

### 4. Sound Level Alerts
- **Monitors**: Hive sound levels
- **Thresholds**: Maximum acceptable sound level (dB)
- **Severity Logic**: Based on excess above threshold
  - Low: 1-9dB above threshold
  - Medium: 10-14dB above threshold
  - High: 15-19dB above threshold
  - Critical: >20dB above threshold

### 5. Battery Level Alerts
- **Monitors**: Smart device battery levels
- **Thresholds**: Minimum battery warning level (%)
- **Severity Logic**: Based on remaining battery
  - Low: Below threshold but >10%
  - Medium: 6-10% remaining
  - High: 3-5% remaining
  - Critical: ≤5% remaining

## Threshold System

### Global vs Hive-Specific Thresholds

The system supports two levels of threshold configuration:

1. **Global Thresholds**: Apply to all hives for a user
2. **Hive-Specific Thresholds**: Override global settings for specific hives

### Threshold Fallback Logic

```python
# Priority order:
1. Hive-specific thresholds (if exist)
2. Global thresholds (fallback)
3. System defaults (if no user thresholds)
```

### Default Threshold Values

```python
DEFAULTS = {
    'temperature_min': 32.0,  # °C
    'temperature_max': 38.0,  # °C
    'humidity_min': 40.0,     # %
    'humidity_max': 70.0,     # %
    'weight_change_threshold': 2.0,  # kg
    'sound_level_threshold': 85,     # dB
    'battery_warning_level': 20,     # %
    'inspection_reminder_days': 7    # days
}
```

## Alert Processing Logic

### 1. Data Collection
- Retrieves latest sensor readings from last 10 minutes
- Filters for active hives with smart devices
- Ensures data freshness and relevance

### 2. Threshold Comparison
- Compares sensor values against applicable thresholds
- Handles missing or null sensor values gracefully
- Implements type-specific comparison logic

### 3. Alert Creation
- Creates alerts only when thresholds are exceeded
- Prevents duplicate alerts (60-minute cooldown)
- Includes detailed trigger information in JSON format

### 4. Severity Calculation
- Dynamically calculates severity based on deviation magnitude
- Type-specific severity rules for appropriate scaling
- Ensures consistent severity across alert types

## API Endpoints

### 1. Manual Alert Checks

#### Check All Hives
```http
POST /api/production/alerts/check_all_alerts/
```

**Response:**
```json
{
  "message": "Alert check completed for 5 hives",
  "alerts_created": 3,
  "hives_checked": 5,
  "timestamp": "2025-07-15T10:47:02Z"
}
```

#### Check Specific Hive
```http
POST /api/production/alerts/check_hive_alerts/
Content-Type: application/json

{
  "hive_id": "uuid-here"
}
```

**Response:**
```json
{
  "message": "Alert check completed for hive Hive-1",
  "alerts_created": 1,
  "hive_id": "uuid-here",
  "hive_name": "Hive-1",
  "timestamp": "2025-07-15T10:47:02Z"
}
```

### 2. Alert Statistics

#### Get Alert Statistics
```http
GET /api/production/alerts/stats/
```

**Response:**
```json
{
  "overview": {
    "total_alerts": 45,
    "active_alerts": 12,
    "resolved_alerts": 33,
    "resolution_rate": 73.33
  },
  "by_severity": {
    "Low": {"total": 20, "active": 5, "display_name": "Low"},
    "Medium": {"total": 15, "active": 4, "display_name": "Medium"},
    "High": {"total": 8, "active": 2, "display_name": "High"},
    "Critical": {"total": 2, "active": 1, "display_name": "Critical"}
  },
  "by_type": {
    "Temperature": {"total": 18, "active": 6, "display_name": "Temperature"},
    "Humidity": {"total": 12, "active": 3, "display_name": "Humidity"},
    "Weight": {"total": 8, "active": 2, "display_name": "Weight"},
    "Sound": {"total": 5, "active": 1, "display_name": "Sound"},
    "Battery": {"total": 2, "active": 0, "display_name": "Battery"}
  }
}
```

### 3. Alert Management

#### Get Active Alerts
```http
GET /api/production/alerts/active/
```

#### Get Alerts by Severity
```http
GET /api/production/alerts/by_severity/
```

#### Resolve Alert
```http
POST /api/production/alerts/{alert_id}/resolve/
Content-Type: application/json

{
  "resolution_notes": "Adjusted hive ventilation"
}
```

## Management Commands

### Check Alerts Command

#### Basic Usage
```bash
python manage.py check_alerts
```

#### Check Specific Hive
```bash
python manage.py check_alerts --hive-id uuid-here
```

#### Verbose Output
```bash
python manage.py check_alerts --verbose
```

### Command Output Example
```
Starting alert check at 2025-07-15 10:47:02+00:00
Checking alerts for hive: Hive-1
Created 1 alerts for hive Hive-1
Checking alerts for hive: Hive-2
Created 0 alerts for hive Hive-2
Alert check completed successfully. Created 1 alerts in 2.34 seconds
```

## Celery Integration

### Periodic Task Configuration

The system includes Celery configuration for automated alert checking:

```python
# celery_config.py
CELERY_BEAT_SCHEDULE = {
    'check-alerts-every-10-minutes': {
        'task': 'production.tasks.check_alerts_task',
        'schedule': crontab(minute='*/10'),
        'options': {'expires': 300}
    },
    'cleanup-old-alerts-daily': {
        'task': 'production.tasks.cleanup_old_alerts_task',
        'schedule': crontab(hour=2, minute=0),
        'options': {'expires': 3600}
    }
}
```

### Task Management

#### Schedule Alert Check
```http
POST /api/production/alerts/schedule_alert_check/
Content-Type: application/json

{
  "hive_id": "uuid-here"  // Optional: for specific hive
}
```

**Response:**
```json
{
  "message": "Alert check scheduled for hive Hive-1",
  "task_id": "task-uuid-here",
  "hive_id": "uuid-here",
  "hive_name": "Hive-1",
  "timestamp": "2025-07-15T10:47:02Z"
}
```

## Configuration

### Environment Variables

```env
# Alert system settings
ALERT_CHECK_INTERVAL_MINUTES=10
DUPLICATE_ALERT_THRESHOLD_MINUTES=60
ALERT_CLEANUP_DAYS=30

# Celery settings (optional)
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
```

### Django Settings

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'production',
    'settings',
    'devices',
    'apiaries',
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'alerts.log',
        },
    },
    'loggers': {
        'production.services.alert_checker': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Database Schema

### Alert Model Fields

```python
class Alerts(models.Model):
    id = models.UUIDField(primary_key=True)
    hive = models.ForeignKey(Hives, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=AlertType.choices)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=Severity.choices)
    trigger_values = models.JSONField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Trigger Values Structure

```json
{
  "temperature": 41.5,
  "threshold_min": 32.0,
  "threshold_max": 38.0,
  "reading_id": "sensor-reading-uuid",
  "deviation": 3.5,
  "timestamp": "2025-07-15T10:47:02Z"
}
```

## Monitoring and Maintenance

### Log Monitoring

The system logs all important events:

```python
# Example log entries
INFO: Starting alert check for all hives...
INFO: Created alert: Hive-1 - Temperature (High) - Active
DEBUG: No sensor readings found for hive: Hive-3
ERROR: Error checking alerts for hive abc123: Database connection failed
```

### Performance Considerations

1. **Database Optimization**
   - Indexes on frequently queried fields
   - Efficient query patterns with select_related()
   - Bulk operations for large datasets

2. **Memory Management**
   - Process hives in batches for large systems
   - Limit sensor reading lookback window
   - Clean up old resolved alerts periodically

3. **Error Handling**
   - Graceful degradation when services are unavailable
   - Comprehensive error logging
   - Automatic retry mechanisms

### Maintenance Tasks

#### Clean Up Old Alerts
```bash
python manage.py shell -c "
from production.models import Alerts
from django.utils import timezone
from datetime import timedelta

# Delete resolved alerts older than 30 days
cutoff = timezone.now() - timedelta(days=30)
count = Alerts.objects.filter(is_resolved=True, resolved_at__lt=cutoff).delete()[0]
print(f'Deleted {count} old alerts')
"
```

#### Monitor Alert Frequency
```bash
python manage.py shell -c "
from production.models import Alerts
from django.utils import timezone
from datetime import timedelta

# Get alert statistics for last 24 hours
since = timezone.now() - timedelta(hours=24)
alerts = Alerts.objects.filter(created_at__gte=since)
print(f'Alerts in last 24h: {alerts.count()}')
print(f'By severity: {dict(alerts.values_list(\"severity\").annotate(count=Count(\"id\")))}')
"
```

## Troubleshooting

### Common Issues

1. **No Alerts Being Created**
   - Check if hives have `has_smart_device=True`
   - Verify sensor readings exist within last 10 minutes
   - Ensure alert thresholds are configured
   - Check log files for error messages

2. **Duplicate Alerts**
   - Verify 60-minute cooldown is working
   - Check if multiple alert checker instances are running
   - Review database transaction handling

3. **Performance Issues**
   - Monitor database query performance
   - Check for large numbers of unresolved alerts
   - Verify Celery worker health if using async tasks

### Debug Commands

```bash
# Check alert thresholds for user
python manage.py shell -c "
from settings.models import AlertThresholds
from accounts.models import User
user = User.objects.get(email='user@example.com')
thresholds = AlertThresholds.objects.filter(user=user)
for t in thresholds:
    print(f'{t.hive or \"Global\"}: temp={t.temperature_min}-{t.temperature_max}')
"

# Check recent sensor readings
python manage.py shell -c "
from devices.models import SensorReadings
from django.utils import timezone
from datetime import timedelta
recent = SensorReadings.objects.filter(
    timestamp__gte=timezone.now() - timedelta(minutes=10)
).order_by('-timestamp')[:5]
for r in recent:
    print(f'{r.device.hive.name}: {r.temperature}°C, {r.humidity}%, {r.timestamp}')
"
```

## Future Enhancements

### Planned Features

1. **Smart Learning**
   - Adaptive thresholds based on historical data
   - Seasonal adjustment of alert parameters
   - Pattern recognition for predictive alerts

2. **Advanced Notifications**
   - Email/SMS notification integration
   - Webhook support for external systems
   - Mobile push notifications

3. **Analytics Dashboard**
   - Real-time alert monitoring
   - Trend analysis and reporting
   - Performance metrics and insights

4. **Integration Enhancements**
   - Weather data correlation
   - Calendar-based threshold adjustments
   - Integration with inspection schedules

### Contributing

To contribute to the alert system:

1. Follow the existing code patterns
2. Add comprehensive tests for new features
3. Update documentation for any changes
4. Ensure backward compatibility

---

*This documentation covers the complete Smart Nyuki Alert System as implemented in the Django backend. For additional support, refer to the API documentation or contact the development team.*
