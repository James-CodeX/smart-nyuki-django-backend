from rest_framework import serializers
from .models import SmartDevices, SensorReadings, AudioRecordings, DeviceImages
from apiaries.models import Hives


class SmartDevicesSerializer(serializers.ModelSerializer):
    """Serializer for SmartDevices model"""
    hive_name = serializers.CharField(source='hive.name', read_only=True)
    apiary_name = serializers.CharField(source='hive.apiary.name', read_only=True)
    beekeeper_name = serializers.CharField(source='beekeeper.user.get_full_name', read_only=True)
    beekeeper_email = serializers.CharField(source='beekeeper.user.email', read_only=True)
    
    class Meta:
        model = SmartDevices
        fields = [
            'id', 'serial_number', 'beekeeper', 'beekeeper_name', 'beekeeper_email',
            'hive', 'hive_name', 'apiary_name', 'device_type', 'last_sync_at', 
            'battery_level', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'hive_name', 'apiary_name', 'beekeeper_name', 'beekeeper_email']
    
    def validate_hive(self, value):
        """Ensure hive belongs to the same beekeeper as the device"""
        if value and hasattr(self.context.get('request'), 'user'):
            request = self.context['request']
            # Get beekeeper from request user
            try:
                from accounts.models import BeekeeperProfile
                beekeeper = BeekeeperProfile.objects.get(user=request.user)
                if value.apiary.beekeeper != beekeeper:
                    raise serializers.ValidationError(
                        "You can only assign devices to your own hives."
                    )
            except BeekeeperProfile.DoesNotExist:
                raise serializers.ValidationError(
                    "You must have a beekeeper profile to manage devices."
                )
        return value


class SensorReadingsSerializer(serializers.ModelSerializer):
    """Serializer for SensorReadings model"""
    device_serial = serializers.CharField(source='device.serial_number', read_only=True)
    hive_name = serializers.CharField(source='device.hive.name', read_only=True)
    
    class Meta:
        model = SensorReadings
        fields = [
            'id', 'device', 'device_serial', 'hive_name', 'temperature', 
            'humidity', 'weight', 'sound_level', 'battery_level', 
            'status_code', 'timestamp', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'device_serial', 'hive_name']
    
    def validate_device(self, value):
        """Ensure device belongs to the authenticated user"""
        if value and hasattr(self.context.get('request'), 'user'):
            request = self.context['request']
            if value.beekeeper.user != request.user:
                raise serializers.ValidationError(
                    "You can only add readings to your own devices."
                )
        return value


class AudioRecordingsSerializer(serializers.ModelSerializer):
    """Serializer for AudioRecordings model"""
    device_serial = serializers.CharField(source='device.serial_number', read_only=True)
    hive_name = serializers.CharField(source='device.hive.name', read_only=True)
    upload_status_display = serializers.CharField(source='get_upload_status_display', read_only=True)
    analysis_status_display = serializers.CharField(source='get_analysis_status_display', read_only=True)
    
    class Meta:
        model = AudioRecordings
        fields = [
            'id', 'device', 'device_serial', 'hive_name', 'file_path', 
            'duration', 'file_size', 'recorded_at', 'upload_status', 
            'upload_status_display', 'analysis_status', 'analysis_status_display',
            'is_analyzed', 'analysis_results', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'device_serial', 'hive_name', 
            'upload_status_display', 'analysis_status_display'
        ]
    
    def validate_device(self, value):
        """Ensure device belongs to the authenticated user"""
        if value and hasattr(self.context.get('request'), 'user'):
            request = self.context['request']
            if value.beekeeper.user != request.user:
                raise serializers.ValidationError(
                    "You can only add recordings to your own devices."
                )
        return value


class DeviceImagesSerializer(serializers.ModelSerializer):
    """Serializer for DeviceImages model"""
    device_serial = serializers.CharField(source='device.serial_number', read_only=True)
    hive_name = serializers.CharField(source='device.hive.name', read_only=True)
    image_type_display = serializers.CharField(source='get_image_type_display', read_only=True)
    upload_status_display = serializers.CharField(source='get_upload_status_display', read_only=True)
    analysis_status_display = serializers.CharField(source='get_analysis_status_display', read_only=True)
    
    class Meta:
        model = DeviceImages
        fields = [
            'id', 'device', 'device_serial', 'hive_name', 'file_path', 
            'captured_at', 'image_type', 'image_type_display', 
            'upload_status', 'upload_status_display', 'analysis_status', 
            'analysis_status_display', 'is_analyzed', 'analysis_results', 
            'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'device_serial', 'hive_name', 
            'image_type_display', 'upload_status_display', 'analysis_status_display'
        ]
    
    def validate_device(self, value):
        """Ensure device belongs to the authenticated user"""
        if value and hasattr(self.context.get('request'), 'user'):
            request = self.context['request']
            if value.beekeeper.user != request.user:
                raise serializers.ValidationError(
                    "You can only add images to your own devices."
                )
        return value


class SmartDevicesDetailSerializer(SmartDevicesSerializer):
    """Detailed serializer for SmartDevices with related data"""
    recent_readings = serializers.SerializerMethodField()
    total_readings = serializers.SerializerMethodField()
    
    class Meta(SmartDevicesSerializer.Meta):
        fields = SmartDevicesSerializer.Meta.fields + ['recent_readings', 'total_readings']
    
    def get_recent_readings(self, obj):
        """Get the 5 most recent sensor readings"""
        recent = obj.sensor_readings.all()[:5]
        return SensorReadingsSerializer(recent, many=True).data
    
    def get_total_readings(self, obj):
        """Get total count of sensor readings"""
        return obj.sensor_readings.count()


class SensorReadingsCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sensor readings with device serial number"""
    device_serial = serializers.CharField(write_only=True)
    
    class Meta:
        model = SensorReadings
        fields = [
            'device_serial', 'temperature', 'humidity', 'weight', 
            'sound_level', 'battery_level', 'status_code', 'timestamp'
        ]
    
    def validate_device_serial(self, value):
        """Validate that device exists and is active"""
        try:
            device = SmartDevices.objects.get(serial_number=value, is_active=True)
            return device
        except SmartDevices.DoesNotExist:
            raise serializers.ValidationError("Device with this serial number not found or inactive.")
    
    def create(self, validated_data):
        """Create sensor reading with device from serial number"""
        device = validated_data.pop('device_serial')
        validated_data['device'] = device
        return super().create(validated_data)
