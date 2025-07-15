import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSettings(models.Model):
    """User preferences for language, timezone, and units"""
    
    class TemperatureUnit(models.TextChoices):
        CELSIUS = 'Celsius', 'Celsius'
        FAHRENHEIT = 'Fahrenheit', 'Fahrenheit'
    
    class WeightUnit(models.TextChoices):
        KILOGRAMS = 'Kilograms', 'Kilograms'
        POUNDS = 'Pounds', 'Pounds'
    
    class DateFormat(models.TextChoices):
        DD_MM_YYYY = 'DD/MM/YYYY', 'DD/MM/YYYY'
        MM_DD_YYYY = 'MM/DD/YYYY', 'MM/DD/YYYY'
        YYYY_MM_DD = 'YYYY-MM-DD', 'YYYY-MM-DD'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_settings'
    )
    timezone = models.CharField(
        max_length=50, 
        default='UTC',
        help_text="User's timezone preference"
    )
    language = models.CharField(
        max_length=10, 
        default='en',
        help_text="User's language preference"
    )
    temperature_unit = models.CharField(
        max_length=20,
        choices=TemperatureUnit.choices,
        default=TemperatureUnit.CELSIUS,
        help_text="Preferred temperature unit"
    )
    weight_unit = models.CharField(
        max_length=20,
        choices=WeightUnit.choices,
        default=WeightUnit.KILOGRAMS,
        help_text="Preferred weight unit"
    )
    date_format = models.CharField(
        max_length=20,
        choices=DateFormat.choices,
        default=DateFormat.DD_MM_YYYY,
        help_text="Preferred date format"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_settings'
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'
    
    def __str__(self):
        return f"{self.user.email} - Settings"
