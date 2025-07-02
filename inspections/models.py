import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from apiaries.models import Hives


class InspectionSchedules(models.Model):
    """Model representing scheduled hive inspections"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hive = models.ForeignKey(
        Hives,
        on_delete=models.CASCADE,
        related_name='inspection_schedules'
    )
    scheduled_date = models.DateField(
        help_text="Date when the inspection is scheduled"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes or instructions for the inspection"
    )
    is_completed = models.BooleanField(
        default=False,
        help_text="Whether the inspection has been completed"
    )
    weather_conditions = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Weather conditions for the scheduled inspection"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inspection_schedules'
        verbose_name = 'Inspection Schedule'
        verbose_name_plural = 'Inspection Schedules'
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"Inspection for {self.hive.name} on {self.scheduled_date}"


class InspectionReports(models.Model):
    """Model representing completed hive inspection reports"""
    
    class HoneyLevel(models.TextChoices):
        LOW = 'Low', 'Low'
        MEDIUM = 'Medium', 'Medium'
        HIGH = 'High', 'High'
    
    class ColonyHealth(models.TextChoices):
        POOR = 'Poor', 'Poor'
        FAIR = 'Fair', 'Fair'
        GOOD = 'Good', 'Good'
        EXCELLENT = 'Excellent', 'Excellent'
    
    class BroodPattern(models.TextChoices):
        SOLID = 'Solid', 'Solid'
        SPOTTY = 'Spotty', 'Spotty'
        NONE = 'None', 'None'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey(
        InspectionSchedules,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
        help_text="Associated inspection schedule (optional)"
    )
    hive = models.ForeignKey(
        Hives,
        on_delete=models.CASCADE,
        related_name='inspection_reports'
    )
    inspector = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inspection_reports'
    )
    inspection_date = models.DateField(
        help_text="Date when the inspection was conducted"
    )
    queen_present = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether the queen was observed during inspection"
    )
    honey_level = models.CharField(
        max_length=10,
        choices=HoneyLevel.choices,
        help_text="Level of honey stores in the hive"
    )
    colony_health = models.CharField(
        max_length=10,
        choices=ColonyHealth.choices,
        help_text="Overall health assessment of the colony"
    )
    varroa_mite_count = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Number of varroa mites observed"
    )
    brood_pattern = models.CharField(
        max_length=10,
        choices=BroodPattern.choices,
        help_text="Pattern of brood development"
    )
    pest_observations = models.TextField(
        blank=True,
        null=True,
        help_text="Observations about pests or diseases"
    )
    actions_taken = models.TextField(
        blank=True,
        null=True,
        help_text="Actions taken during the inspection"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the inspection"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inspection_reports'
        verbose_name = 'Inspection Report'
        verbose_name_plural = 'Inspection Reports'
        ordering = ['-inspection_date']
    
    def __str__(self):
        return f"Inspection of {self.hive.name} on {self.inspection_date} by {self.inspector.full_name}"
