# Device-Hive Synchronization

This document explains the automatic synchronization of the `has_smart_device` field on Hives when SmartDevices are linked or unlinked.

## Overview

The Smart Nyuki system automatically maintains the `has_smart_device` boolean field on each Hive to reflect whether the hive currently has any active smart devices assigned to it. This synchronization happens automatically through Django signals.

**Device Ownership**: As of this implementation, each device has a direct `beekeeper` field that establishes ownership. This allows beekeepers to register devices they own even if they haven't assigned them to a hive yet. Devices can be in one of two states:
- **Unassigned**: Device is owned by a beekeeper but not yet assigned to any hive
- **Assigned**: Device is owned by a beekeeper and assigned to one of their hives

## How It Works

### Django Signals

The system uses Django's signal framework to automatically update the `has_smart_device` field whenever:

1. **Device Created with Hive Assignment**: When a new device is created and assigned to a hive
2. **Device Hive Assignment Changed**: When a device is moved from one hive to another
3. **Device Unassigned from Hive**: When a device's hive assignment is removed
4. **Device Deactivated**: When a device's `is_active` field is set to `False`
5. **Device Deleted**: When a device is permanently deleted

### Signal Handlers

The following signal handlers are implemented in `devices/signals.py`:

- **`update_hive_smart_device_status_on_save`**: Handles device creation and updates
- **`handle_hive_change_before_save`**: Captures old hive assignments before changes
- **`update_old_hive_smart_device_status`**: Updates old hives after device reassignment
- **`update_hive_smart_device_status_on_delete`**: Handles device deletion

### Logic Rules

1. **Active Devices Only**: Only devices with `is_active=True` count toward the `has_smart_device` flag
2. **Multiple Devices**: A hive can have multiple devices; the flag remains `True` as long as at least one active device is assigned
3. **Immediate Updates**: Changes are applied immediately when device assignments change
4. **Batch Safety**: Multiple devices can be assigned/unassigned in transactions safely

## Example Scenarios

### Scenario 1: New Device Assignment
```python
# Initial state: hive.has_smart_device = False
device = SmartDevices.objects.create(
    serial_number='DEV001',
    hive=hive,
    is_active=True
)
# Result: hive.has_smart_device = True (automatically updated)
```

### Scenario 2: Device Reassignment
```python
# Initial state: hive1.has_smart_device = True, hive2.has_smart_device = False
device.hive = hive2
device.save()
# Result: hive1.has_smart_device = False, hive2.has_smart_device = True
```

### Scenario 3: Device Deactivation
```python
# Initial state: hive.has_smart_device = True (has 1 active device)
device.is_active = False
device.save()
# Result: hive.has_smart_device = False (no active devices remain)
```

### Scenario 4: Multiple Devices
```python
# hive has 2 active devices
device1.delete()
# Result: hive.has_smart_device = True (device2 still active)

device2.delete()
# Result: hive.has_smart_device = False (no active devices remain)
```

## Manual Synchronization

### Management Command

For data maintenance or one-time synchronization of existing data:

```bash
# Check what would be updated (dry run)
python manage.py sync_hive_smart_device_status --dry-run

# Update all hives
python manage.py sync_hive_smart_device_status

# Update specific hive
python manage.py sync_hive_smart_device_status --hive-id=<hive_uuid>
```

### Utility Function

For programmatic synchronization:

```python
from devices.signals import update_hive_smart_device_status

# Manually update a specific hive
has_devices = update_hive_smart_device_status(hive)
```

## Testing

Comprehensive tests are available in `devices/tests_signals.py` that verify:

- Device creation with/without hive assignment
- Device hive assignment changes
- Device unassignment
- Device deactivation
- Device deletion
- Multiple devices per hive
- Inactive device handling

Run the tests with:
```bash
python manage.py test devices.tests_signals
```

## Performance Considerations

1. **Efficiency**: Signal handlers use `update_fields` to minimize database writes
2. **Consistency**: All updates happen within the same transaction as the triggering change
3. **Scalability**: Queries are optimized to check device existence without loading full objects

## Troubleshooting

### Common Issues

1. **Signals Not Working**: Ensure `devices.signals` is imported in `devices/apps.py`
2. **Inconsistent State**: Run the management command to resynchronize
3. **Performance Issues**: Check for recursive signal calls or missing `update_fields`

### Debugging

To debug signal execution, add logging to the signal handlers:

```python
import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=SmartDevices)
def update_hive_smart_device_status_on_save(sender, instance, created, **kwargs):
    logger.info(f"Device {instance.serial_number} saved, updating hive status")
    # ... rest of signal handler
```

## Implementation Notes

- Signals are automatically connected when Django starts via `devices/apps.py`
- The implementation is safe for concurrent operations
- Database integrity is maintained through proper transaction handling
- The system gracefully handles edge cases like device reassignment and deletion
