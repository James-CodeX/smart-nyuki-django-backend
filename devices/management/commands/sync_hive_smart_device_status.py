from django.core.management.base import BaseCommand
from django.db import transaction
from apiaries.models import Hives
from devices.models import SmartDevices
from devices.signals import update_hive_smart_device_status


class Command(BaseCommand):
    help = 'Synchronize has_smart_device field for all hives based on actual device assignments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--hive-id',
            type=str,
            help='Update only a specific hive by ID',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        hive_id = options.get('hive_id')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Get hives to process
        if hive_id:
            try:
                hives = Hives.objects.filter(id=hive_id)
                if not hives.exists():
                    self.stdout.write(
                        self.style.ERROR(f'Hive with ID {hive_id} not found')
                    )
                    return
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f'Invalid hive ID format: {hive_id}')
                )
                return
        else:
            hives = Hives.objects.all()
        
        updated_count = 0
        total_count = hives.count()
        
        self.stdout.write(f'Processing {total_count} hive(s)...')
        
        with transaction.atomic():
            for hive in hives:
                # Check if hive has active smart devices
                has_active_devices = SmartDevices.objects.filter(
                    hive=hive, 
                    is_active=True
                ).exists()
                
                # Check if update is needed
                needs_update = hive.has_smart_device != has_active_devices
                
                if needs_update:
                    self.stdout.write(
                        f'Hive "{hive.name}" (ID: {hive.id}): '
                        f'{hive.has_smart_device} -> {has_active_devices}'
                    )
                    
                    if not dry_run:
                        hive.has_smart_device = has_active_devices
                        hive.save(update_fields=['has_smart_device'])
                    
                    updated_count += 1
                else:
                    # Show current status for verbose output
                    device_count = SmartDevices.objects.filter(
                        hive=hive, 
                        is_active=True
                    ).count()
                    
                    self.stdout.write(
                        f'Hive "{hive.name}" (ID: {hive.id}): '
                        f'Already correct - has_smart_device={has_active_devices} '
                        f'({device_count} active device(s))'
                    )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY RUN: Would update {updated_count} out of {total_count} hive(s)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} out of {total_count} hive(s)'
                )
            )
        
        # Show summary statistics
        self.show_summary()
    
    def show_summary(self):
        """Show summary statistics of current state"""
        self.stdout.write('\n--- Summary ---')
        
        total_hives = Hives.objects.count()
        hives_with_flag = Hives.objects.filter(has_smart_device=True).count()
        hives_with_devices = Hives.objects.filter(
            smart_devices__is_active=True
        ).distinct().count()
        
        self.stdout.write(f'Total hives: {total_hives}')
        self.stdout.write(f'Hives with has_smart_device=True: {hives_with_flag}')
        self.stdout.write(f'Hives with active devices: {hives_with_devices}')
        
        if hives_with_flag == hives_with_devices:
            self.stdout.write(
                self.style.SUCCESS('✓ All hive statuses are synchronized!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠ Mismatch detected: {abs(hives_with_flag - hives_with_devices)} '
                    'hive(s) need synchronization'
                )
            )
