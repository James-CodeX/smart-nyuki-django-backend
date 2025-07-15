"""
Django management command to check sensor readings and create alerts.

This command is designed to be run periodically (every 10 minutes) via cron
or a task scheduler to monitor sensor readings and create alerts when thresholds
are exceeded.

Usage:
    python manage.py check_alerts
    python manage.py check_alerts --verbose
    python manage.py check_alerts --hive-id <hive_uuid>
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
import logging

from production.services.alert_checker import AlertChecker
from apiaries.models import Hives

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check sensor readings and create alerts when thresholds are exceeded'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hive-id',
            type=str,
            help='Check alerts for a specific hive only (UUID)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )

    def handle(self, *args, **options):
        start_time = timezone.now()
        
        # Configure logging level
        if options['verbose']:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting alert check at {start_time}')
        )
        
        try:
            alert_checker = AlertChecker()
            
            if options['hive_id']:
                # Check alerts for a specific hive
                alerts_created = self.check_single_hive(alert_checker, options['hive_id'])
            else:
                # Check alerts for all hives
                alerts_created = alert_checker.check_all_hives()
            
            end_time = timezone.now()
            duration = end_time - start_time
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Alert check completed successfully. '
                    f'Created {alerts_created} alerts in {duration.total_seconds():.2f} seconds'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during alert check: {str(e)}')
            )
            raise CommandError(f'Alert check failed: {str(e)}')

    def check_single_hive(self, alert_checker, hive_id):
        """Check alerts for a single hive."""
        try:
            hive = Hives.objects.get(id=hive_id)
            
            if not hive.is_active:
                self.stdout.write(
                    self.style.WARNING(f'Hive {hive.name} is not active')
                )
                return 0
            
            if not hive.has_smart_device:
                self.stdout.write(
                    self.style.WARNING(f'Hive {hive.name} does not have a smart device')
                )
                return 0
            
            self.stdout.write(f'Checking alerts for hive: {hive.name}')
            alerts_created = alert_checker.check_hive_alerts(hive)
            
            self.stdout.write(
                self.style.SUCCESS(f'Created {alerts_created} alerts for hive {hive.name}')
            )
            
            return alerts_created
            
        except Hives.DoesNotExist:
            raise CommandError(f'Hive with ID {hive_id} does not exist')
        except Exception as e:
            raise CommandError(f'Error checking hive {hive_id}: {str(e)}')
