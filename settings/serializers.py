from rest_framework import serializers
from .models import (
    UserSettings, 
    AlertThresholds, 
    NotificationSettings, 
    DataSyncSettings, 
    PrivacySettings
)
from apiaries.models import Hives


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer for user settings"""
    
    class Meta:
        model = UserSettings
        fields = [
            'id', 'timezone', 'language', 'temperature_unit', 
            'weight_unit', 'date_format', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AlertThresholdsSerializer(serializers.ModelSerializer):
    """Serializer for alert thresholds"""
    
    hive_name = serializers.CharField(source='hive.name', read_only=True)
    is_global = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AlertThresholds
        fields = [
            'id', 'hive', 'hive_name', 'is_global',
            'temperature_min', 'temperature_max', 
            'humidity_min', 'humidity_max',
            'weight_change_threshold', 'sound_level_threshold',
            'battery_warning_level', 'inspection_reminder_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_hive(self, value):
        """Validate that the hive belongs to the current user"""
        if value and value.apiary.beekeeper.user != self.context['request'].user:
            raise serializers.ValidationError("You can only set thresholds for your own hives.")
        return value
    
    def validate(self, data):
        """Validate temperature and humidity ranges"""
        if data.get('temperature_min') and data.get('temperature_max'):
            if data['temperature_min'] >= data['temperature_max']:
                raise serializers.ValidationError(
                    "Temperature minimum must be less than maximum"
                )
        
        if data.get('humidity_min') and data.get('humidity_max'):
            if data['humidity_min'] >= data['humidity_max']:
                raise serializers.ValidationError(
                    "Humidity minimum must be less than maximum"
                )
        
        return data


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for notification settings"""
    
    class Meta:
        model = NotificationSettings
        fields = [
            'id', 'push_notifications', 'email_notifications', 
            'sms_notifications', 'alert_sound', 'quiet_hours_start',
            'quiet_hours_end', 'critical_alerts_override_quiet',
            'daily_summary_enabled', 'daily_summary_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DataSyncSettingsSerializer(serializers.ModelSerializer):
    """Serializer for data sync settings"""
    
    class Meta:
        model = DataSyncSettings
        fields = [
            'id', 'auto_sync_enabled', 'sync_frequency', 
            'wifi_only_sync', 'backup_enabled', 'backup_frequency',
            'data_retention_days', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PrivacySettingsSerializer(serializers.ModelSerializer):
    """Serializer for privacy settings"""
    
    class Meta:
        model = PrivacySettings
        fields = [
            'id', 'location_sharing', 'analytics_enabled', 
            'crash_reporting', 'data_sharing_research',
            'profile_visibility', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HiveListSerializer(serializers.ModelSerializer):
    """Simplified serializer for hive list in alert thresholds"""
    
    apiary_name = serializers.CharField(source='apiary.name', read_only=True)
    
    class Meta:
        model = Hives
        fields = ['id', 'name', 'apiary_name', 'is_active']
