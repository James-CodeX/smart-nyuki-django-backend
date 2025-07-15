import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import DecimalValidator, MinValueValidator, MaxValueValidator

User = get_user_model()


class AlertThresholds(models.Model):
    """Alert thresholds for sensor values - can be global or hive-specific"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='alert_thresholds'
    )
    hive = models.ForeignKey(
        'apiaries.Hives', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='alert_thresholds',
        help_text="Null means global setting for all hives"
    )
    
    # Temperature thresholds
    temperature_min = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=32.0,
        validators=[DecimalValidator(max_digits=5, decimal_places=2)],
        help_text="Minimum temperature alert threshold in °C"
    )
    temperature_max = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=38.0,
        validators=[DecimalValidator(max_digits=5, decimal_places=2)],
        help_text="Maximum temperature alert threshold in °C"
    )
    
    # Humidity thresholds
    humidity_min = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=40.0,
        validators=[
            DecimalValidator(max_digits=5, decimal_places=2),
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ],
        help_text="Minimum humidity alert threshold in %"
    )
    humidity_max = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=70.0,
        validators=[
            DecimalValidator(max_digits=5, decimal_places=2),
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ],
        help_text="Maximum humidity alert threshold in %"
    )
    
    # Weight change threshold
    weight_change_threshold = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=2.0,
        validators=[DecimalValidator(max_digits=6, decimal_places=2)],
        help_text="Daily weight change alert threshold in kg"
    )
    
    # Sound level threshold
    sound_level_threshold = models.IntegerField(
        default=85,
        validators=[MinValueValidator(0), MaxValueValidator(150)],
        help_text="Sound level alert threshold in dB"
    )
    
    # Battery warning level
    battery_warning_level = models.IntegerField(
        default=20,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Battery warning level in %"
    )
    
    # Inspection reminder
    inspection_reminder_days = models.IntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        help_text="Days before inspection due to send reminder"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alert_thresholds'
        verbose_name = 'Alert Threshold'
        verbose_name_plural = 'Alert Thresholds'
        unique_together = ['user', 'hive']  # Ensure one threshold setting per user-hive combination
    
    def __str__(self):
        hive_name = f" - {self.hive.name}" if self.hive else " - Global"
        return f"{self.user.email}{hive_name} - Alert Thresholds"
    
    @property
    def is_global(self):
        """Check if this is a global threshold setting"""
        return self.hive is None
