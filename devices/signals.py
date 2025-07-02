from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import SmartDevices
from apiaries.models import Hives


@receiver(post_save, sender=SmartDevices)
def update_hive_smart_device_status_on_save(sender, instance, created, **kwargs):
    """
    Update has_smart_device field when a device is saved.
    This handles both new device assignments and updates to existing devices.
    """
    # If the device has a hive assigned and is active, mark that hive as having a smart device
    if instance.hive and instance.is_active:
        instance.hive.has_smart_device = True
        instance.hive.save(update_fields=['has_smart_device'])
    
    # If device is being deactivated, check if hive should be updated
    if hasattr(instance, '_being_deactivated') and instance._being_deactivated and instance.hive:
        # Check if this hive still has other active smart devices
        remaining_devices = SmartDevices.objects.filter(
            hive=instance.hive, 
            is_active=True
        ).exclude(pk=instance.pk)
        
        # If no active devices remain, update the hive
        if not remaining_devices.exists():
            instance.hive.has_smart_device = False
            instance.hive.save(update_fields=['has_smart_device'])


@receiver(pre_save, sender=SmartDevices)
def handle_hive_change_before_save(sender, instance, **kwargs):
    """
    Handle hive changes before saving the device.
    This captures the old hive assignment to update it properly.
    """
    if instance.pk:  # Only for existing devices
        try:
            old_instance = SmartDevices.objects.get(pk=instance.pk)
            old_hive = old_instance.hive
            new_hive = instance.hive
            
            # Store the old hive in the instance for use in post_save
            instance._old_hive = old_hive
            
            # If hive is being changed and there was an old hive
            if old_hive != new_hive and old_hive:
                # Check if the old hive will still have smart devices after this change
                remaining_devices = SmartDevices.objects.filter(
                    hive=old_hive, 
                    is_active=True
                ).exclude(pk=instance.pk)
                
                # Store info about whether old hive should be updated
                instance._should_update_old_hive = not remaining_devices.exists()
            else:
                instance._should_update_old_hive = False
                
        except SmartDevices.DoesNotExist:
            instance._old_hive = None
            instance._should_update_old_hive = False
    else:
        instance._old_hive = None
        instance._should_update_old_hive = False


@receiver(post_save, sender=SmartDevices)
def update_old_hive_smart_device_status(sender, instance, created, **kwargs):
    """
    Update the old hive's has_smart_device status after device save.
    """
    if not created and hasattr(instance, '_should_update_old_hive') and instance._should_update_old_hive:
        if hasattr(instance, '_old_hive') and instance._old_hive:
            instance._old_hive.has_smart_device = False
            instance._old_hive.save(update_fields=['has_smart_device'])


@receiver(post_delete, sender=SmartDevices)
def update_hive_smart_device_status_on_delete(sender, instance, **kwargs):
    """
    Update has_smart_device field when a device is deleted.
    """
    if instance.hive:
        # Check if this hive still has other active smart devices
        remaining_devices = SmartDevices.objects.filter(
            hive=instance.hive, 
            is_active=True
        ).exclude(pk=instance.pk)
        
        # If no active devices remain, update the hive
        if not remaining_devices.exists():
            instance.hive.has_smart_device = False
            instance.hive.save(update_fields=['has_smart_device'])


def update_hive_smart_device_status(hive):
    """
    Utility function to manually update a hive's smart device status.
    Useful for maintenance or data correction.
    """
    if hive:
        has_devices = SmartDevices.objects.filter(
            hive=hive, 
            is_active=True
        ).exists()
        
        hive.has_smart_device = has_devices
        hive.save(update_fields=['has_smart_device'])
        return has_devices
    return False
