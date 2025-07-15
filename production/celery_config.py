"""
Celery configuration for the production app.

This module contains the Celery Beat schedule configuration for periodic tasks.
"""

from celery.schedules import crontab

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'check-alerts-every-10-minutes': {
        'task': 'production.tasks.check_alerts_task',
        'schedule': crontab(minute='*/10'),  # Run every 10 minutes
        'options': {
            'expires': 300,  # Task expires after 5 minutes if not executed
        }
    },
    'cleanup-old-alerts-daily': {
        'task': 'production.tasks.cleanup_old_alerts_task',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2:00 AM
        'options': {
            'expires': 3600,  # Task expires after 1 hour if not executed
        }
    },
}
