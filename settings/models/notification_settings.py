import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationSettings(models.Model):
    """User notification preferences"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='notification_settings'
    )
    
    # Notification channels
    push_notifications = models.BooleanField(
        default=True,
        help_text="Enable push notifications"
    )
    email_notifications = models.BooleanField(
        default=True,
        help_text="Enable email notifications"
    )
    sms_notifications = models.BooleanField(
        default=False,
        help_text="Enable SMS notifications"
    )
    
    # Sound settings
    alert_sound = models.BooleanField(
        default=True,
        help_text="Enable sound alerts"
    )
    
    # Quiet hours
    quiet_hours_start = models.TimeField(
        default='22:00',
        help_text="Start time for quiet hours"
    )
    quiet_hours_end = models.TimeField(
        default='06:00',
        help_text="End time for quiet hours"
    )
    critical_alerts_override_quiet = models.BooleanField(
        default=True,
        help_text="Allow critical alerts during quiet hours"
    )
    
    # Daily summary
    daily_summary_enabled = models.BooleanField(
        default=True,
        help_text="Enable daily summary notifications"
    )
    daily_summary_time = models.TimeField(
        default='08:00',
        help_text="Time to send daily summary"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_settings'
        verbose_name = 'Notification Settings'
        verbose_name_plural = 'Notification Settings'
    
    def __str__(self):
        return f"{self.user.email} - Notification Settings"
    
    def is_quiet_time(self, current_time):
        """Check if current time is within quiet hours"""
        if self.quiet_hours_start <= self.quiet_hours_end:
            # Same day quiet hours (e.g., 22:00 to 23:00)
            return self.quiet_hours_start <= current_time <= self.quiet_hours_end
        else:
            # Overnight quiet hours (e.g., 22:00 to 06:00)
            return current_time >= self.quiet_hours_start or current_time <= self.quiet_hours_end
