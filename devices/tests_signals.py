from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import BeekeeperProfile
from apiaries.models import Apiaries, Hives
from devices.models import SmartDevices
from datetime import date
from decimal import Decimal

User = get_user_model()


class DeviceHiveLinkingSignalsTestCase(TestCase):
    """Test automatic updating of has_smart_device field when devices are linked/unlinked"""
    
    def setUp(self):
        """Set up test data"""
        # Create user and beekeeper profile
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.beekeeper = BeekeeperProfile.objects.create(
            user=self.user,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            experience_level='Beginner',
            established_date=date.today(),
            app_start_date=date.today()
        )
        
        # Create apiary
        self.apiary = Apiaries.objects.create(
            beekeeper=self.beekeeper,
            name='Test Apiary',
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060')
        )
        
        # Create hives
        self.hive1 = Hives.objects.create(
            apiary=self.apiary,
            name='Hive 1',
            installation_date=date.today(),
            has_smart_device=False  # Initially no smart device
        )
        
        self.hive2 = Hives.objects.create(
            apiary=self.apiary,
            name='Hive 2',
            installation_date=date.today(),
            has_smart_device=False  # Initially no smart device
        )
    
    def test_device_creation_with_hive_assignment(self):
        """Test that creating a device with hive assignment updates has_smart_device"""
        # Verify initial state
        self.assertFalse(self.hive1.has_smart_device)
        
        # Create device assigned to hive
        device = SmartDevices.objects.create(
            serial_number='DEV001',
            device_type='Temperature Sensor',
            beekeeper=self.beekeeper,
            hive=self.hive1,
            is_active=True
        )
        
        # Refresh hive from database
        self.hive1.refresh_from_db()
        
        # Verify hive now has smart device flag set
        self.assertTrue(self.hive1.has_smart_device)
    
    def test_device_creation_without_hive_assignment(self):
        """Test that creating a device without hive assignment doesn't affect hives"""
        # Verify initial state
        self.assertFalse(self.hive1.has_smart_device)
        
        # Create device without hive assignment
        device = SmartDevices.objects.create(
            serial_number='DEV002',
            device_type='Temperature Sensor',
            beekeeper=self.beekeeper,
            hive=None,
            is_active=True
        )
        
        # Refresh hive from database
        self.hive1.refresh_from_db()
        
        # Verify hive still doesn't have smart device flag set
        self.assertFalse(self.hive1.has_smart_device)
    
    def test_device_hive_assignment_change(self):
        """Test that changing device hive assignment updates both hives"""
        # Create device assigned to hive1
        device = SmartDevices.objects.create(
            serial_number='DEV003',
            device_type='Temperature Sensor',
            beekeeper=self.beekeeper,
            hive=self.hive1,
            is_active=True
        )
        
        # Verify initial state
        self.hive1.refresh_from_db()
        self.hive2.refresh_from_db()
        self.assertTrue(self.hive1.has_smart_device)
        self.assertFalse(self.hive2.has_smart_device)
        
        # Move device to hive2
        device.hive = self.hive2
        device.save()
        
        # Refresh hives from database
        self.hive1.refresh_from_db()
        self.hive2.refresh_from_db()
        
        # Verify hive1 no longer has smart device, hive2 now does
        self.assertFalse(self.hive1.has_smart_device)
        self.assertTrue(self.hive2.has_smart_device)
    
    def test_device_unassignment(self):
        """Test that removing device from hive updates has_smart_device"""
        # Create device assigned to hive
        device = SmartDevices.objects.create(
            serial_number='DEV004',
            device_type='Temperature Sensor',
            beekeeper=self.beekeeper,
            hive=self.hive1,
            is_active=True
        )
        
        # Verify initial state
        self.hive1.refresh_from_db()
        self.assertTrue(self.hive1.has_smart_device)
        
        # Unassign device from hive
        device.hive = None
        device.save()
        
        # Refresh hive from database
        self.hive1.refresh_from_db()
        
        # Verify hive no longer has smart device flag set
        self.assertFalse(self.hive1.has_smart_device)
    
    def test_device_deactivation(self):
        """Test that deactivating a device updates has_smart_device"""
        # Create device assigned to hive
        device = SmartDevices.objects.create(
            serial_number='DEV005',
            device_type='Temperature Sensor',
            beekeeper=self.beekeeper,
            hive=self.hive1,
            is_active=True
        )
        
        # Verify initial state
        self.hive1.refresh_from_db()
        self.assertTrue(self.hive1.has_smart_device)
        
        # Deactivate device
        device.is_active = False
        device.save()
        
        # Refresh hive from database
        self.hive1.refresh_from_db()
        
        # Verify hive no longer has smart device flag set
        self.assertFalse(self.hive1.has_smart_device)
    
    def test_device_deletion(self):
        """Test that deleting a device updates has_smart_device"""
        # Create device assigned to hive
        device = SmartDevices.objects.create(
            serial_number='DEV006',
            device_type='Temperature Sensor',
            beekeeper=self.beekeeper,
            hive=self.hive1,
            is_active=True
        )
        
        # Verify initial state
        self.hive1.refresh_from_db()
        self.assertTrue(self.hive1.has_smart_device)
        
        # Delete device
        device.delete()
        
        # Refresh hive from database
        self.hive1.refresh_from_db()
        
        # Verify hive no longer has smart device flag set
        self.assertFalse(self.hive1.has_smart_device)
    
    def test_multiple_devices_same_hive(self):
        """Test that hive keeps smart device flag when it has multiple devices"""
        # Create two devices assigned to same hive
        device1 = SmartDevices.objects.create(
            serial_number='DEV007',
            device_type='Temperature Sensor',
            beekeeper=self.beekeeper,
            hive=self.hive1,
            is_active=True
        )
        
        device2 = SmartDevices.objects.create(
            serial_number='DEV008',
            device_type='Humidity Sensor',
            beekeeper=self.beekeeper,
            hive=self.hive1,
            is_active=True
        )
        
        # Verify hive has smart device flag set
        self.hive1.refresh_from_db()
        self.assertTrue(self.hive1.has_smart_device)
        
        # Remove one device
        device1.delete()
        
        # Verify hive still has smart device flag set (device2 still exists)
        self.hive1.refresh_from_db()
        self.assertTrue(self.hive1.has_smart_device)
        
        # Remove second device
        device2.delete()
        
        # Now hive should not have smart device flag set
        self.hive1.refresh_from_db()
        self.assertFalse(self.hive1.has_smart_device)
    
    def test_inactive_device_doesnt_count(self):
        """Test that inactive devices don't count for has_smart_device"""
        # Create active device
        device1 = SmartDevices.objects.create(
            serial_number='DEV009',
            device_type='Temperature Sensor',
            beekeeper=self.beekeeper,
            hive=self.hive1,
            is_active=True
        )
        
        # Create inactive device
        device2 = SmartDevices.objects.create(
            serial_number='DEV010',
            device_type='Humidity Sensor',
            beekeeper=self.beekeeper,
            hive=self.hive1,
            is_active=False
        )
        
        # Verify hive has smart device flag set (due to active device)
        self.hive1.refresh_from_db()
        self.assertTrue(self.hive1.has_smart_device)
        
        # Deactivate the active device
        device1.is_active = False
        device1.save()
        
        # Now hive should not have smart device flag set (only inactive devices remain)
        self.hive1.refresh_from_db()
        self.assertFalse(self.hive1.has_smart_device)
