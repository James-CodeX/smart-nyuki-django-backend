"""
Celery tasks for the production app.

This module contains background tasks for alert checking and monitoring.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .services.alert_checker import AlertChecker
from apiaries.models import Hives

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def check_alerts_task(self):
    """
    Periodic task to check sensor readings and create alerts.
    
    This task runs every 10 minutes to monitor sensor readings
    and create alerts when thresholds are exceeded.
    """
    try:
        start_time = timezone.now()
        logger.info(f"Starting periodic alert check at {start_time}")
        
        alert_checker = AlertChecker()
        alerts_created = alert_checker.check_all_hives()
        
        end_time = timezone.now()
        duration = end_time - start_time
        
        logger.info(
            f"Alert check completed successfully. "
            f"Created {alerts_created} alerts in {duration.total_seconds():.2f} seconds"
        )
        
        return {
            'status': 'success',
            'alerts_created': alerts_created,
            'duration_seconds': duration.total_seconds(),
            'timestamp': start_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error during periodic alert check: {str(e)}")
        
        # Retry the task with exponential backoff
        try:
            self.retry(countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for alert check task")
            
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task(bind=True, max_retries=3)
def check_hive_alerts_task(self, hive_id):
    """
    Task to check alerts for a specific hive.
    
    Args:
        hive_id: UUID of the hive to check
    """
    try:
        logger.info(f"Starting alert check for hive {hive_id}")
        
        hive = Hives.objects.get(id=hive_id)
        
        if not hive.is_active or not hive.has_smart_device:
            logger.warning(f"Hive {hive.name} is not active or has no smart device")
            return {
                'status': 'skipped',
                'reason': 'Hive not active or no smart device',
                'hive_id': hive_id,
                'timestamp': timezone.now().isoformat()
            }
        
        alert_checker = AlertChecker()
        alerts_created = alert_checker.check_hive_alerts(hive)
        
        logger.info(f"Created {alerts_created} alerts for hive {hive.name}")
        
        return {
            'status': 'success',
            'alerts_created': alerts_created,
            'hive_id': hive_id,
            'hive_name': hive.name,
            'timestamp': timezone.now().isoformat()
        }
        
    except Hives.DoesNotExist:
        logger.error(f"Hive with ID {hive_id} does not exist")
        return {
            'status': 'error',
            'error': f'Hive with ID {hive_id} does not exist',
            'hive_id': hive_id,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking alerts for hive {hive_id}: {str(e)}")
        
        # Retry the task
        try:
            self.retry(countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for hive {hive_id} alert check")
            
        return {
            'status': 'error',
            'error': str(e),
            'hive_id': hive_id,
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def cleanup_old_alerts_task():
    """
    Task to clean up old resolved alerts.
    
    This task removes resolved alerts older than 30 days
    to keep the database clean.
    """
    try:
        from .models import Alerts
        
        # Delete resolved alerts older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_count = Alerts.objects.filter(
            is_resolved=True,
            resolved_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old resolved alerts")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old alerts: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }
