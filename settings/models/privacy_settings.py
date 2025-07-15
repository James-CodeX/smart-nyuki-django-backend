import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PrivacySettings(models.Model):
    """User privacy and data sharing preferences"""
    
    class ProfileVisibility(models.TextChoices):
        PRIVATE = 'Private', 'Private'
        PUBLIC = 'Public', 'Public'
        COMMUNITY = 'Community', 'Community'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='privacy_settings'
    )
    
    # Location and data sharing
    location_sharing = models.BooleanField(
        default=False,
        help_text="Allow sharing location data"
    )
    analytics_enabled = models.BooleanField(
        default=True,
        help_text="Enable analytics and usage tracking"
    )
    crash_reporting = models.BooleanField(
        default=True,
        help_text="Enable crash reporting for app improvement"
    )
    data_sharing_research = models.BooleanField(
        default=False,
        help_text="Allow anonymized data sharing for research"
    )
    
    # Profile visibility
    profile_visibility = models.CharField(
        max_length=20,
        choices=ProfileVisibility.choices,
        default=ProfileVisibility.PRIVATE,
        help_text="Who can see your profile"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'privacy_settings'
        verbose_name = 'Privacy Settings'
        verbose_name_plural = 'Privacy Settings'
    
    def __str__(self):
        return f"{self.user.email} - Privacy Settings"
