from django.db import models
import uuid
from django.core.validators import DecimalValidator
from accounts.models import User
from apiaries.models import Hives


class Harvests(models.Model):
    """Model representing honey and product harvests from hives"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hive = models.ForeignKey(
        Hives, 
        on_delete=models.CASCADE, 
        related_name='harvests'
    )
    harvest_date = models.DateField()
    honey_kg = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[DecimalValidator(max_digits=5, decimal_places=2)],
        help_text="Amount of honey harvested in kilograms"
    )
    wax_kg = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[DecimalValidator(max_digits=4, decimal_places=2)],
        blank=True,
        null=True,
        help_text="Amount of wax harvested in kilograms"
    )
    pollen_kg = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[DecimalValidator(max_digits=4, decimal_places=2)],
        blank=True,
        null=True,
        help_text="Amount of pollen harvested in kilograms"
    )
    processing_method = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Method used for processing the harvest"
    )
    harvested_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='harvests_conducted'
    )
    quality_notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Notes about the quality of the harvest"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Harvest"
        verbose_name_plural = "Harvests"
        ordering = ['-harvest_date', '-created_at']
    
    def __str__(self):
        return f"{self.hive.name} - {self.harvest_date} ({self.honey_kg}kg honey)"
    
    @property
    def total_weight_kg(self):
        """Calculate total weight of all harvested products"""
        total = self.honey_kg
        if self.wax_kg:
            total += self.wax_kg
        if self.pollen_kg:
            total += self.pollen_kg
        return total


class Alerts(models.Model):
    """Model representing alerts and notifications for hives"""
    
    class AlertType(models.TextChoices):
        TEMPERATURE = 'Temperature', 'Temperature'
        HUMIDITY = 'Humidity', 'Humidity'
        WEIGHT = 'Weight', 'Weight'
        SOUND = 'Sound', 'Sound'
        BATTERY = 'Battery', 'Battery'
        INSPECTION_DUE = 'Inspection_Due', 'Inspection Due'
        PEST_RISK = 'Pest_Risk', 'Pest Risk'
        SWARM_RISK = 'Swarm_Risk', 'Swarm Risk'
    
    class Severity(models.TextChoices):
        LOW = 'Low', 'Low'
        MEDIUM = 'Medium', 'Medium'
        HIGH = 'High', 'High'
        CRITICAL = 'Critical', 'Critical'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hive = models.ForeignKey(
        Hives, 
        on_delete=models.CASCADE, 
        related_name='alerts'
    )
    alert_type = models.CharField(
        max_length=20,
        choices=AlertType.choices
    )
    message = models.TextField(
        help_text="Descriptive message about the alert"
    )
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices
    )
    trigger_values = models.JSONField(
        blank=True,
        null=True,
        help_text="JSON data containing the values that triggered this alert"
    )
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(
        blank=True,
        null=True
    )
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='alerts_resolved',
        blank=True,
        null=True
    )
    resolution_notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Notes about how the alert was resolved"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"
        ordering = ['-created_at']
    
    def __str__(self):
        status = "Resolved" if self.is_resolved else "Active"
        return f"{self.hive.name} - {self.alert_type} ({self.severity}) - {status}"
    
    def resolve(self, user, notes=None):
        """Mark the alert as resolved"""
        from django.utils import timezone
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        if notes:
            self.resolution_notes = notes
        self.save()
