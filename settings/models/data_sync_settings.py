import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class DataSyncSettings(models.Model):
    """User data synchronization and backup preferences"""
    
    class SyncFrequency(models.TextChoices):
        REAL_TIME = 'Real-time', 'Real-time'
        HOURLY = 'Hourly', 'Hourly'
        DAILY = 'Daily', 'Daily'
    
    class BackupFrequency(models.TextChoices):
        DAILY = 'Daily', 'Daily'
        WEEKLY = 'Weekly', 'Weekly'
        MONTHLY = 'Monthly', 'Monthly'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='data_sync_settings'
    )
    
    # Sync settings
    auto_sync_enabled = models.BooleanField(
        default=True,
        help_text="Enable automatic data synchronization"
    )
    sync_frequency = models.CharField(
        max_length=20,
        choices=SyncFrequency.choices,
        default=SyncFrequency.HOURLY,
        help_text="How often to sync data"
    )
    wifi_only_sync = models.BooleanField(
        default=False,
        help_text="Only sync when connected to WiFi"
    )
    
    # Backup settings
    backup_enabled = models.BooleanField(
        default=True,
        help_text="Enable automatic data backup"
    )
    backup_frequency = models.CharField(
        max_length=20,
        choices=BackupFrequency.choices,
        default=BackupFrequency.WEEKLY,
        help_text="How often to backup data"
    )
    
    # Data retention
    data_retention_days = models.IntegerField(
        default=365,
        validators=[MinValueValidator(30), MaxValueValidator(3650)],
        help_text="How many days to keep sensor data (30-3650 days)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_sync_settings'
        verbose_name = 'Data Sync Settings'
        verbose_name_plural = 'Data Sync Settings'
    
    def __str__(self):
        return f"{self.user.email} - Data Sync Settings"
