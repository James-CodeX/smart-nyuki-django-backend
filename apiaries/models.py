from django.db import models
import uuid
from django.core.validators import DecimalValidator
from accounts.models import BeekeeperProfile


class Apiaries(models.Model):
    """Model representing an apiary (bee yard)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    beekeeper = models.ForeignKey(
        BeekeeperProfile, 
        on_delete=models.CASCADE, 
        related_name='apiaries'
    )
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=8,
        validators=[DecimalValidator(max_digits=10, decimal_places=8)]
    )
    longitude = models.DecimalField(
        max_digits=11, 
        decimal_places=8,
        validators=[DecimalValidator(max_digits=11, decimal_places=8)]
    )
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Apiary"
        verbose_name_plural = "Apiaries"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.beekeeper.user.full_name}"


class Hives(models.Model):
    """Model representing a hive within an apiary"""
    
    class HiveType(models.TextChoices):
        LANGSTROTH = 'Langstroth', 'Langstroth'
        TOP_BAR = 'Top-Bar', 'Top-Bar'
        WARRE = 'Warre', 'Warre'
        OTHER = 'Other', 'Other'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    apiary = models.ForeignKey(
        Apiaries, 
        on_delete=models.CASCADE, 
        related_name='hives'
    )
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=20,
        choices=HiveType.choices,
        default=HiveType.LANGSTROTH
    )
    installation_date = models.DateField()
    has_smart_device = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Hive"
        verbose_name_plural = "Hives"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.apiary.name}"
