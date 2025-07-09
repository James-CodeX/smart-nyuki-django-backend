from rest_framework import serializers
from .models import Apiaries, Hives
from accounts.models import BeekeeperProfile


class ApiariesSerializer(serializers.ModelSerializer):
    """Serializer for Apiaries model"""
    beekeeper_name = serializers.CharField(source='beekeeper.user.full_name', read_only=True)
    hives_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Apiaries
        fields = [
            'id', 'beekeeper', 'beekeeper_name', 'name', 'latitude', 
            'longitude', 'address', 'description', 'created_at', 
            'deleted_at', 'hives_count'
        ]
        read_only_fields = ['id', 'beekeeper', 'created_at', 'beekeeper_name', 'hives_count']
    
    def get_hives_count(self, obj):
        return obj.hives.filter(is_active=True).count()
    
    def validate(self, data):
        # Validation is handled in the view's perform_create method
        # Since beekeeper is read-only, we don't need to validate it here
        return data


class HivesSerializer(serializers.ModelSerializer):
    """Serializer for Hives model"""
    apiary_name = serializers.CharField(source='apiary.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Hives
        fields = [
            'id', 'apiary', 'apiary_name', 'name', 'type', 'type_display',
            'installation_date', 'has_smart_device', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'apiary_name', 'type_display']
    
    def validate(self, data):
        # Ensure apiary belongs to the authenticated user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if data.get('apiary') and data['apiary'].beekeeper.user != request.user:
                raise serializers.ValidationError(
                    "You can only create hives for your own apiaries."
                )
        return data


class ApiariesDetailSerializer(ApiariesSerializer):
    """Detailed serializer for Apiaries with nested hives"""
    hives = HivesSerializer(many=True, read_only=True)
    
    class Meta(ApiariesSerializer.Meta):
        fields = ApiariesSerializer.Meta.fields + ['hives']


class HivesDetailSerializer(HivesSerializer):
    """Detailed serializer for Hives with apiary details"""
    apiary = ApiariesSerializer(read_only=True)
    smart_devices = serializers.SerializerMethodField()
    latest_sensor_reading = serializers.SerializerMethodField()
    
    class Meta(HivesSerializer.Meta):
        fields = HivesSerializer.Meta.fields + ['apiary', 'smart_devices', 'latest_sensor_reading']
    
    def get_smart_devices(self, obj):
        """Get active smart devices assigned to this hive"""
        devices = obj.smart_devices.filter(is_active=True)
        if devices.exists():
            # Import here to avoid circular imports
            from devices.serializers import SmartDevicesSerializer
            return SmartDevicesSerializer(devices, many=True, context=self.context).data
        return []
    
    def get_latest_sensor_reading(self, obj):
        """Get the latest sensor reading for this hive"""
        if not obj.has_smart_device:
            return None
            
        # Import here to avoid circular imports
        from devices.models import SensorReadings
        from devices.serializers import SensorReadingsSerializer
        
        latest_reading = SensorReadings.objects.filter(
            device__hive=obj,
            device__is_active=True
        ).select_related('device').order_by('-timestamp').first()
        
        if latest_reading:
            return SensorReadingsSerializer(latest_reading, context=self.context).data
        return None
