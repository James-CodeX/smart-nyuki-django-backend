"""
Alert Checker Service

This service monitors sensor readings and creates alerts when thresholds are exceeded.
It runs every 10 minutes to check the latest sensor readings against alert thresholds.
"""

from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging

from ..models import Alerts
from devices.models import SensorReadings
from settings.models import AlertThresholds
from apiaries.models import Hives

logger = logging.getLogger(__name__)


class AlertChecker:
    """Service for checking sensor readings against alert thresholds and creating alerts."""
    
    def __init__(self):
        self.alert_duration_minutes = 10  # Check readings from last 10 minutes
        self.duplicate_alert_threshold_minutes = 60  # Prevent duplicate alerts within 1 hour
    
    def check_all_hives(self):
        """Check all active hives with smart devices for alerts."""
        logger.info("Starting alert check for all hives...")
        
        # Get all active hives with smart devices
        hives = Hives.objects.filter(
            is_active=True,
            has_smart_device=True,
            smart_devices__is_active=True
        ).distinct()
        
        total_alerts_created = 0
        
        for hive in hives:
            try:
                alerts_created = self.check_hive_alerts(hive)
                total_alerts_created += alerts_created
            except Exception as e:
                logger.error(f"Error checking alerts for hive {hive.id}: {str(e)}")
        
        logger.info(f"Alert check completed. Created {total_alerts_created} new alerts.")
        return total_alerts_created
    
    def check_hive_alerts(self, hive):
        """Check alerts for a specific hive."""
        logger.debug(f"Checking alerts for hive: {hive.name}")
        
        # Get the latest sensor reading for this hive
        latest_reading = self.get_latest_sensor_reading(hive)
        if not latest_reading:
            logger.debug(f"No sensor readings found for hive: {hive.name}")
            return 0
        
        # Get alert thresholds for this hive (hive-specific or global)
        thresholds = self.get_alert_thresholds(hive)
        if not thresholds:
            logger.debug(f"No alert thresholds found for hive: {hive.name}")
            return 0
        
        alerts_created = 0
        
        # Check each threshold type
        alerts_created += self.check_temperature_alerts(hive, latest_reading, thresholds)
        alerts_created += self.check_humidity_alerts(hive, latest_reading, thresholds)
        alerts_created += self.check_weight_alerts(hive, latest_reading, thresholds)
        alerts_created += self.check_sound_alerts(hive, latest_reading, thresholds)
        alerts_created += self.check_battery_alerts(hive, latest_reading, thresholds)
        
        return alerts_created
    
    def get_latest_sensor_reading(self, hive):
        """Get the latest sensor reading for a hive."""
        now = timezone.now()
        time_threshold = now - timedelta(minutes=self.alert_duration_minutes)
        
        return SensorReadings.objects.filter(
            device__hive=hive,
            device__is_active=True,
            timestamp__gte=time_threshold
        ).order_by('-timestamp').first()
    
    def get_alert_thresholds(self, hive):
        """Get alert thresholds for a hive (hive-specific or global fallback)."""
        user = hive.apiary.beekeeper.user
        
        # First try to get hive-specific thresholds
        hive_thresholds = AlertThresholds.objects.filter(
            user=user,
            hive=hive
        ).first()
        
        if hive_thresholds:
            return hive_thresholds
        
        # Fall back to global thresholds
        global_thresholds = AlertThresholds.objects.filter(
            user=user,
            hive__isnull=True
        ).first()
        
        return global_thresholds
    
    def check_temperature_alerts(self, hive, reading, thresholds):
        """Check temperature-related alerts."""
        if not reading.temperature:
            return 0
        
        temperature = float(reading.temperature)
        alerts_created = 0
        
        # Check minimum temperature
        if temperature < float(thresholds.temperature_min):
            alert_created = self.create_alert(
                hive=hive,
                alert_type=Alerts.AlertType.TEMPERATURE,
                severity=self.get_temperature_severity(temperature, thresholds),
                message=f"Temperature too low: {temperature}°C (minimum: {thresholds.temperature_min}°C)",
                trigger_values={
                    'temperature': temperature,
                    'threshold_min': float(thresholds.temperature_min),
                    'threshold_max': float(thresholds.temperature_max),
                    'reading_id': str(reading.id)
                }
            )
            if alert_created:
                alerts_created += 1
        
        # Check maximum temperature
        elif temperature > float(thresholds.temperature_max):
            alert_created = self.create_alert(
                hive=hive,
                alert_type=Alerts.AlertType.TEMPERATURE,
                severity=self.get_temperature_severity(temperature, thresholds),
                message=f"Temperature too high: {temperature}°C (maximum: {thresholds.temperature_max}°C)",
                trigger_values={
                    'temperature': temperature,
                    'threshold_min': float(thresholds.temperature_min),
                    'threshold_max': float(thresholds.temperature_max),
                    'reading_id': str(reading.id)
                }
            )
            if alert_created:
                alerts_created += 1
        
        return alerts_created
    
    def check_humidity_alerts(self, hive, reading, thresholds):
        """Check humidity-related alerts."""
        if not reading.humidity:
            return 0
        
        humidity = float(reading.humidity)
        alerts_created = 0
        
        # Check minimum humidity
        if humidity < float(thresholds.humidity_min):
            alert_created = self.create_alert(
                hive=hive,
                alert_type=Alerts.AlertType.HUMIDITY,
                severity=self.get_humidity_severity(humidity, thresholds),
                message=f"Humidity too low: {humidity}% (minimum: {thresholds.humidity_min}%)",
                trigger_values={
                    'humidity': humidity,
                    'threshold_min': float(thresholds.humidity_min),
                    'threshold_max': float(thresholds.humidity_max),
                    'reading_id': str(reading.id)
                }
            )
            if alert_created:
                alerts_created += 1
        
        # Check maximum humidity
        elif humidity > float(thresholds.humidity_max):
            alert_created = self.create_alert(
                hive=hive,
                alert_type=Alerts.AlertType.HUMIDITY,
                severity=self.get_humidity_severity(humidity, thresholds),
                message=f"Humidity too high: {humidity}% (maximum: {thresholds.humidity_max}%)",
                trigger_values={
                    'humidity': humidity,
                    'threshold_min': float(thresholds.humidity_min),
                    'threshold_max': float(thresholds.humidity_max),
                    'reading_id': str(reading.id)
                }
            )
            if alert_created:
                alerts_created += 1
        
        return alerts_created
    
    def check_weight_alerts(self, hive, reading, thresholds):
        """Check weight change alerts."""
        if not reading.weight:
            return 0
        
        current_weight = float(reading.weight)
        alerts_created = 0
        
        # Get previous weight reading from 24 hours ago
        yesterday = timezone.now() - timedelta(days=1)
        previous_reading = SensorReadings.objects.filter(
            device__hive=hive,
            device__is_active=True,
            timestamp__date=yesterday.date()
        ).order_by('-timestamp').first()
        
        if previous_reading and previous_reading.weight:
            previous_weight = float(previous_reading.weight)
            weight_change = abs(current_weight - previous_weight)
            
            if weight_change > float(thresholds.weight_change_threshold):
                alert_created = self.create_alert(
                    hive=hive,
                    alert_type=Alerts.AlertType.WEIGHT,
                    severity=self.get_weight_severity(weight_change, thresholds),
                    message=f"Significant weight change: {weight_change:.2f}kg in 24h (threshold: {thresholds.weight_change_threshold}kg)",
                    trigger_values={
                        'current_weight': current_weight,
                        'previous_weight': previous_weight,
                        'weight_change': weight_change,
                        'threshold': float(thresholds.weight_change_threshold),
                        'reading_id': str(reading.id)
                    }
                )
                if alert_created:
                    alerts_created += 1
        
        return alerts_created
    
    def check_sound_alerts(self, hive, reading, thresholds):
        """Check sound level alerts."""
        if not reading.sound_level:
            return 0
        
        sound_level = reading.sound_level
        alerts_created = 0
        
        if sound_level > thresholds.sound_level_threshold:
            alert_created = self.create_alert(
                hive=hive,
                alert_type=Alerts.AlertType.SOUND,
                severity=self.get_sound_severity(sound_level, thresholds),
                message=f"High sound level detected: {sound_level}dB (threshold: {thresholds.sound_level_threshold}dB)",
                trigger_values={
                    'sound_level': sound_level,
                    'threshold': thresholds.sound_level_threshold,
                    'reading_id': str(reading.id)
                }
            )
            if alert_created:
                alerts_created += 1
        
        return alerts_created
    
    def check_battery_alerts(self, hive, reading, thresholds):
        """Check battery level alerts."""
        if not reading.battery_level:
            return 0
        
        battery_level = reading.battery_level
        alerts_created = 0
        
        if battery_level <= thresholds.battery_warning_level:
            alert_created = self.create_alert(
                hive=hive,
                alert_type=Alerts.AlertType.BATTERY,
                severity=self.get_battery_severity(battery_level, thresholds),
                message=f"Low battery level: {battery_level}% (warning level: {thresholds.battery_warning_level}%)",
                trigger_values={
                    'battery_level': battery_level,
                    'threshold': thresholds.battery_warning_level,
                    'reading_id': str(reading.id)
                }
            )
            if alert_created:
                alerts_created += 1
        
        return alerts_created
    
    def create_alert(self, hive, alert_type, severity, message, trigger_values):
        """Create an alert if it doesn't already exist."""
        # Check if a similar alert already exists within the threshold time
        time_threshold = timezone.now() - timedelta(minutes=self.duplicate_alert_threshold_minutes)
        
        existing_alert = Alerts.objects.filter(
            hive=hive,
            alert_type=alert_type,
            is_resolved=False,
            created_at__gte=time_threshold
        ).first()
        
        if existing_alert:
            logger.debug(f"Similar alert already exists for hive {hive.name}, type {alert_type}")
            return False
        
        try:
            with transaction.atomic():
                alert = Alerts.objects.create(
                    hive=hive,
                    alert_type=alert_type,
                    severity=severity,
                    message=message,
                    trigger_values=trigger_values
                )
                logger.info(f"Created alert: {alert}")
                return True
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            return False
    
    def get_temperature_severity(self, temperature, thresholds):
        """Determine severity based on temperature deviation."""
        min_temp = float(thresholds.temperature_min)
        max_temp = float(thresholds.temperature_max)
        
        if temperature < min_temp:
            deviation = min_temp - temperature
        else:
            deviation = temperature - max_temp
        
        if deviation >= 5:
            return Alerts.Severity.CRITICAL
        elif deviation >= 3:
            return Alerts.Severity.HIGH
        elif deviation >= 1:
            return Alerts.Severity.MEDIUM
        else:
            return Alerts.Severity.LOW
    
    def get_humidity_severity(self, humidity, thresholds):
        """Determine severity based on humidity deviation."""
        min_hum = float(thresholds.humidity_min)
        max_hum = float(thresholds.humidity_max)
        
        if humidity < min_hum:
            deviation = min_hum - humidity
        else:
            deviation = humidity - max_hum
        
        if deviation >= 20:
            return Alerts.Severity.CRITICAL
        elif deviation >= 15:
            return Alerts.Severity.HIGH
        elif deviation >= 10:
            return Alerts.Severity.MEDIUM
        else:
            return Alerts.Severity.LOW
    
    def get_weight_severity(self, weight_change, thresholds):
        """Determine severity based on weight change."""
        threshold = float(thresholds.weight_change_threshold)
        
        if weight_change >= threshold * 3:
            return Alerts.Severity.CRITICAL
        elif weight_change >= threshold * 2:
            return Alerts.Severity.HIGH
        elif weight_change >= threshold * 1.5:
            return Alerts.Severity.MEDIUM
        else:
            return Alerts.Severity.LOW
    
    def get_sound_severity(self, sound_level, thresholds):
        """Determine severity based on sound level."""
        threshold = thresholds.sound_level_threshold
        
        if sound_level >= threshold + 20:
            return Alerts.Severity.CRITICAL
        elif sound_level >= threshold + 15:
            return Alerts.Severity.HIGH
        elif sound_level >= threshold + 10:
            return Alerts.Severity.MEDIUM
        else:
            return Alerts.Severity.LOW
    
    def get_battery_severity(self, battery_level, thresholds):
        """Determine severity based on battery level."""
        threshold = thresholds.battery_warning_level
        
        if battery_level <= 5:
            return Alerts.Severity.CRITICAL
        elif battery_level <= 10:
            return Alerts.Severity.HIGH
        elif battery_level <= threshold:
            return Alerts.Severity.MEDIUM
        else:
            return Alerts.Severity.LOW
