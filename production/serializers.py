from rest_framework import serializers
from .models import Harvests, Alerts
from accounts.serializers import UserSerializer
from apiaries.serializers import HivesSerializer
from apiaries.models import Hives


class HarvestsSerializer(serializers.ModelSerializer):
    """Serializer for Harvests model"""
    hive_name = serializers.CharField(source='hive.name', read_only=True)
    harvested_by_name = serializers.CharField(source='harvested_by.full_name', read_only=True)
    total_weight_kg = serializers.ReadOnlyField()
    
    class Meta:
        model = Harvests
        fields = [
            'id', 'hive', 'hive_name', 'harvest_date', 'honey_kg', 
            'wax_kg', 'pollen_kg', 'processing_method', 'harvested_by',
            'harvested_by_name', 'quality_notes', 'created_at', 'total_weight_kg'
        ]
        read_only_fields = ['id', 'harvested_by', 'created_at', 'hive_name', 'harvested_by_name', 'total_weight_kg']
    
    def validate(self, data):
        # Ensure hive belongs to the authenticated user's apiaries
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            hive = data.get('hive')
            if hive:
                # Check if user has a beekeeper profile and owns the hive's apiary
                try:
                    beekeeper_profile = request.user.beekeeper_profile
                    if hive.apiary.beekeeper != beekeeper_profile:
                        raise serializers.ValidationError(
                            "You can only create harvests for hives in your own apiaries."
                        )
                except AttributeError:
                    raise serializers.ValidationError(
                        "You must have a beekeeper profile to create harvests."
                    )
        return data
    
    def validate_honey_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Honey weight must be greater than 0.")
        return value
    
    def validate_wax_kg(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Wax weight must be greater than 0.")
        return value
    
    def validate_pollen_kg(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Pollen weight must be greater than 0.")
        return value


class AlertsSerializer(serializers.ModelSerializer):
    """Serializer for Alerts model"""
    hive_name = serializers.CharField(source='hive.name', read_only=True)
    apiary_name = serializers.CharField(source='hive.apiary.name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.full_name', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = Alerts
        fields = [
            'id', 'hive', 'hive_name', 'apiary_name', 'alert_type', 'alert_type_display',
            'message', 'severity', 'severity_display', 'trigger_values',
            'is_resolved', 'resolved_at', 'resolved_by', 'resolved_by_name',
            'resolution_notes', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'hive_name', 'resolved_by_name',
            'alert_type_display', 'severity_display'
        ]
    
    def validate(self, data):
        # Ensure hive belongs to the authenticated user's apiaries
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            hive = data.get('hive')
            if hive:
                # Check if user has a beekeeper profile and owns the hive's apiary
                try:
                    beekeeper_profile = request.user.beekeeper_profile
                    if hive.apiary.beekeeper != beekeeper_profile:
                        raise serializers.ValidationError(
                            "You can only create alerts for hives in your own apiaries."
                        )
                except AttributeError:
                    raise serializers.ValidationError(
                        "You must have a beekeeper profile to create alerts."
                    )
        return data


class HarvestsDetailSerializer(HarvestsSerializer):
    """Detailed serializer for Harvests with nested hive details"""
    hive = HivesSerializer(read_only=True)
    harvested_by = UserSerializer(read_only=True)
    
    class Meta(HarvestsSerializer.Meta):
        fields = HarvestsSerializer.Meta.fields + ['hive', 'harvested_by']


class AlertsDetailSerializer(AlertsSerializer):
    """Detailed serializer for Alerts with nested hive and user details"""
    hive = HivesSerializer(read_only=True)
    resolved_by = UserSerializer(read_only=True)
    
    class Meta(AlertsSerializer.Meta):
        fields = AlertsSerializer.Meta.fields + ['hive', 'resolved_by']


class AlertResolveSerializer(serializers.Serializer):
    """Serializer for resolving alerts"""
    resolution_notes = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Optional notes about how the alert was resolved"
    )
