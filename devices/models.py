from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from apiaries.models import Hives
from accounts.models import BeekeeperProfile


class SmartDevicesManager(models.Manager):
    """Custom manager for SmartDevices with beekeeper-specific methods"""
    
    def for_beekeeper(self, beekeeper):
        """Get all devices belonging to a specific beekeeper"""
        return self.filter(
            beekeeper=beekeeper
        ).select_related('beekeeper__user')
    
    def for_user(self, user):
        """Get all devices belonging to a specific user"""
        return self.filter(
            beekeeper__user=user
        ).select_related('beekeeper__user')
    
    def active_for_beekeeper(self, beekeeper):
        """Get all active devices belonging to a specific beekeeper"""
        return self.for_beekeeper(beekeeper).filter(is_active=True)
    
    def active_for_user(self, user):
        """Get all active devices belonging to a specific user"""
        return self.for_user(user).filter(is_active=True)
    
    def unassigned(self):
        """Get all unassigned devices (not linked to any hive)"""
        return self.filter(hive__isnull=True)
    
    def assigned(self):
        """Get all assigned devices (linked to a hive)"""
        return self.filter(hive__isnull=False)
    
    def unassigned_for_beekeeper(self, beekeeper):
        """Get all unassigned devices for a specific beekeeper"""
        return self.for_beekeeper(beekeeper).filter(hive__isnull=True)
    
    def assigned_for_beekeeper(self, beekeeper):
        """Get all assigned devices for a specific beekeeper"""
        return self.for_beekeeper(beekeeper).filter(hive__isnull=False)


class SmartDevices(models.Model):
    """Model representing smart devices for hive monitoring"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serial_number = models.CharField(max_length=100, unique=True)
    beekeeper = models.ForeignKey(
        BeekeeperProfile,
        on_delete=models.CASCADE,
        related_name='devices',
        help_text="The beekeeper who owns this device"
    )
    hive = models.ForeignKey(
        Hives, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='smart_devices'
    )
    device_type = models.CharField(max_length=50)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    battery_level = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Custom manager
    objects = SmartDevicesManager()
    
    class Meta:
        verbose_name = "Smart Device"
        verbose_name_plural = "Smart Devices"
        ordering = ['-created_at']
    
    def __str__(self):
        hive_name = self.hive.name if self.hive else "Unassigned"
        return f"{self.serial_number} - {hive_name}"
    
    @property
    def beekeeper_user(self):
        """Get the user who owns this device"""
        return self.beekeeper.user if self.beekeeper else None
    
    def clean(self):
        """Validate that hive belongs to the same beekeeper if assigned"""
        super().clean()
        if self.hive and self.beekeeper:
            if self.hive.apiary.beekeeper != self.beekeeper:
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    "Device can only be assigned to hives owned by the same beekeeper."
                )
    
    def save(self, *args, **kwargs):
        """Override save to handle is_active changes"""
        # Check if this is an update and if is_active has changed
        if self.pk:
            try:
                old_instance = SmartDevices.objects.get(pk=self.pk)
                if old_instance.is_active and not self.is_active:
                    # Device is being deactivated, store this info for signal
                    self._being_deactivated = True
                else:
                    self._being_deactivated = False
            except SmartDevices.DoesNotExist:
                self._being_deactivated = False
        else:
            self._being_deactivated = False
            
        super().save(*args, **kwargs)


class SensorReadings(models.Model):
    """Model representing sensor readings from smart devices"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        SmartDevices, 
        on_delete=models.CASCADE, 
        related_name='sensor_readings'
    )
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    sound_level = models.IntegerField(null=True, blank=True)
    battery_level = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    status_code = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Sensor Reading"
        verbose_name_plural = "Sensor Readings"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.device.serial_number} - {self.timestamp}"


class AudioRecordings(models.Model):
    """Model representing audio recordings from smart devices"""
    
    class UploadStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        UPLOADED = 'Uploaded', 'Uploaded'
        FAILED = 'Failed', 'Failed'
    
    class AnalysisStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        PROCESSING = 'Processing', 'Processing'
        COMPLETED = 'Completed', 'Completed'
        FAILED = 'Failed', 'Failed'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        SmartDevices, 
        on_delete=models.CASCADE, 
        related_name='audio_recordings'
    )
    file_path = models.TextField()
    duration = models.IntegerField(help_text="Duration in seconds")
    file_size = models.IntegerField(help_text="File size in bytes")
    recorded_at = models.DateTimeField()
    upload_status = models.CharField(
        max_length=20,
        choices=UploadStatus.choices,
        default=UploadStatus.PENDING
    )
    analysis_status = models.CharField(
        max_length=20,
        choices=AnalysisStatus.choices,
        default=AnalysisStatus.PENDING
    )
    is_analyzed = models.BooleanField(default=False)
    analysis_results = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Audio Recording"
        verbose_name_plural = "Audio Recordings"
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.device.serial_number} - Audio {self.recorded_at}"


class DeviceImages(models.Model):
    """Model representing images captured by smart devices"""
    
    class ImageType(models.TextChoices):
        ROUTINE = 'Routine', 'Routine'
        ALERT_TRIGGERED = 'Alert-Triggered', 'Alert-Triggered'
        MANUAL = 'Manual', 'Manual'
    
    class UploadStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        UPLOADED = 'Uploaded', 'Uploaded'
        FAILED = 'Failed', 'Failed'
    
    class AnalysisStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        PROCESSING = 'Processing', 'Processing'
        COMPLETED = 'Completed', 'Completed'
        FAILED = 'Failed', 'Failed'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        SmartDevices, 
        on_delete=models.CASCADE, 
        related_name='device_images'
    )
    file_path = models.TextField()
    captured_at = models.DateTimeField()
    image_type = models.CharField(
        max_length=20,
        choices=ImageType.choices,
        default=ImageType.ROUTINE
    )
    upload_status = models.CharField(
        max_length=20,
        choices=UploadStatus.choices,
        default=UploadStatus.PENDING
    )
    analysis_status = models.CharField(
        max_length=20,
        choices=AnalysisStatus.choices,
        default=AnalysisStatus.PENDING
    )
    is_analyzed = models.BooleanField(default=False)
    analysis_results = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Device Image"
        verbose_name_plural = "Device Images"
        ordering = ['-captured_at']
    
    def __str__(self):
        return f"{self.device.serial_number} - Image {self.captured_at}"
