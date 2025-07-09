from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.views import APIView

from .models import SmartDevices, SensorReadings, AudioRecordings, DeviceImages
from .serializers import (
    SmartDevicesSerializer,
    SmartDevicesDetailSerializer,
    SensorReadingsSerializer,
    SensorReadingsCreateSerializer,
    AudioRecordingsSerializer,
    DeviceImagesSerializer
)
from apiaries.models import Hives


class SmartDevicesListCreateView(generics.ListCreateAPIView):
    """List and create smart devices"""
    serializer_class = SmartDevicesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['device_type', 'is_active', 'hive']
    search_fields = ['serial_number', 'device_type']
    ordering_fields = ['created_at', 'last_sync_at', 'battery_level']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return devices for the current user"""
        user = self.request.user
        return SmartDevices.objects.for_user(user).select_related('beekeeper__user', 'hive__apiary')
    
    def perform_create(self, serializer):
        """Auto-assign the current user's beekeeper profile to the device"""
        from accounts.models import BeekeeperProfile
        try:
            beekeeper = BeekeeperProfile.objects.get(user=self.request.user)
            serializer.save(beekeeper=beekeeper)
        except BeekeeperProfile.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You must have a beekeeper profile to create devices.")
    
    @extend_schema(
        summary="List smart devices",
        description="Get list of smart devices for the current user's hives",
        responses={200: SmartDevicesSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create smart device",
        description="Create a new smart device",
        request=SmartDevicesSerializer,
        responses={
            201: SmartDevicesSerializer,
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SmartDevicesDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete smart devices"""
    serializer_class = SmartDevicesDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return devices for the current user"""
        user = self.request.user
        return SmartDevices.objects.for_user(user).select_related('beekeeper__user', 'hive__apiary').prefetch_related('sensor_readings')
    
    @extend_schema(
        summary="Get smart device details",
        description="Retrieve detailed information about a smart device including recent readings",
        responses={200: SmartDevicesDetailSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update smart device",
        description="Update a smart device",
        responses={
            200: SmartDevicesDetailSerializer,
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete smart device",
        description="Delete a smart device",
        responses={204: OpenApiResponse(description="Device deleted successfully")}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class SensorReadingsListCreateView(generics.ListCreateAPIView):
    """List and create sensor readings"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['device', 'device__serial_number']
    ordering_fields = ['timestamp', 'created_at', 'temperature', 'humidity', 'weight']
    ordering = ['-timestamp']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SensorReadingsCreateSerializer
        return SensorReadingsSerializer
    
    def get_queryset(self):
        """Return readings for the current user's devices"""
        user = self.request.user
        return SensorReadings.objects.filter(
            device__beekeeper__user=user
        ).select_related('device__beekeeper__user', 'device__hive')
    
    @extend_schema(
        summary="List sensor readings",
        description="Get list of sensor readings for the current user's devices",
        responses={200: SensorReadingsSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create sensor reading",
        description="Create a new sensor reading using device serial number",
        request=SensorReadingsCreateSerializer,
        responses={
            201: SensorReadingsSerializer,
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SensorReadingsDetailView(generics.RetrieveAPIView):
    """Retrieve sensor reading details"""
    serializer_class = SensorReadingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return readings for the current user's devices"""
        user = self.request.user
        return SensorReadings.objects.filter(
            device__beekeeper__user=user
        ).select_related('device__beekeeper__user', 'device__hive')
    
    @extend_schema(
        summary="Get sensor reading details",
        description="Retrieve detailed information about a sensor reading",
        responses={200: SensorReadingsSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AudioRecordingsListCreateView(generics.ListCreateAPIView):
    """List and create audio recordings"""
    serializer_class = AudioRecordingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['device', 'upload_status', 'analysis_status', 'is_analyzed']
    ordering_fields = ['recorded_at', 'created_at', 'duration', 'file_size']
    ordering = ['-recorded_at']
    
    def get_queryset(self):
        """Return recordings for the current user's devices"""
        user = self.request.user
        return AudioRecordings.objects.filter(
            device__beekeeper__user=user
        ).select_related('device__beekeeper__user', 'device__hive')
    
    @extend_schema(
        summary="List audio recordings",
        description="Get list of audio recordings for the current user's devices",
        responses={200: AudioRecordingsSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create audio recording",
        description="Create a new audio recording entry",
        request=AudioRecordingsSerializer,
        responses={
            201: AudioRecordingsSerializer,
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AudioRecordingsDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update audio recordings"""
    serializer_class = AudioRecordingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return recordings for the current user's devices"""
        user = self.request.user
        return AudioRecordings.objects.filter(
            device__beekeeper__user=user
        ).select_related('device__beekeeper__user', 'device__hive')
    
    @extend_schema(
        summary="Get audio recording details",
        description="Retrieve detailed information about an audio recording",
        responses={200: AudioRecordingsSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update audio recording",
        description="Update an audio recording (typically for status updates)",
        responses={
            200: AudioRecordingsSerializer,
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class DeviceImagesListCreateView(generics.ListCreateAPIView):
    """List and create device images"""
    serializer_class = DeviceImagesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['device', 'image_type', 'upload_status', 'analysis_status', 'is_analyzed']
    ordering_fields = ['captured_at', 'created_at']
    ordering = ['-captured_at']
    
    def get_queryset(self):
        """Return images for the current user's devices"""
        user = self.request.user
        return DeviceImages.objects.filter(
            device__beekeeper__user=user
        ).select_related('device__beekeeper__user', 'device__hive')
    
    @extend_schema(
        summary="List device images",
        description="Get list of images captured by the current user's devices",
        responses={200: DeviceImagesSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create device image",
        description="Create a new device image entry",
        request=DeviceImagesSerializer,
        responses={
            201: DeviceImagesSerializer,
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DeviceImagesDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update device images"""
    serializer_class = DeviceImagesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return images for the current user's devices"""
        user = self.request.user
        return DeviceImages.objects.filter(
            device__beekeeper__user=user
        ).select_related('device__beekeeper__user', 'device__hive')
    
    @extend_schema(
        summary="Get device image details",
        description="Retrieve detailed information about a device image",
        responses={200: DeviceImagesSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update device image",
        description="Update a device image (typically for status updates)",
        responses={
            200: DeviceImagesSerializer,
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(
    summary="Get device statistics",
    description="Get statistics for a specific device",
    responses={
        200: OpenApiResponse(
            description="Device statistics",
            response={
                'type': 'object',
                'properties': {
                    'total_readings': {'type': 'integer'},
                    'readings_last_24h': {'type': 'integer'},
                    'readings_last_week': {'type': 'integer'},
                    'audio_recordings': {'type': 'integer'},
                    'device_images': {'type': 'integer'},
                    'last_reading': {'type': 'object'},
                    'battery_status': {'type': 'string'}
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def device_stats(request, device_id):
    """Get statistics for a specific device"""
    from django.utils import timezone
    from datetime import timedelta
    
    device = get_object_or_404(
        SmartDevices,
        id=device_id,
        beekeeper__user=request.user
    )
    
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_week = now - timedelta(days=7)
    
    # Get statistics
    total_readings = device.sensor_readings.count()
    readings_last_24h = device.sensor_readings.filter(timestamp__gte=last_24h).count()
    readings_last_week = device.sensor_readings.filter(timestamp__gte=last_week).count()
    audio_recordings = device.audio_recordings.count()
    device_images = device.device_images.count()
    
    # Get last reading
    last_reading = device.sensor_readings.first()
    last_reading_data = None
    if last_reading:
        last_reading_data = SensorReadingsSerializer(last_reading).data
    
    # Determine battery status
    battery_status = "Unknown"
    if device.battery_level is not None:
        if device.battery_level > 50:
            battery_status = "Good"
        elif device.battery_level > 20:
            battery_status = "Medium"
        else:
            battery_status = "Low"
    
    return Response({
        'total_readings': total_readings,
        'readings_last_24h': readings_last_24h,
        'readings_last_week': readings_last_week,
        'audio_recordings': audio_recordings,
        'device_images': device_images,
        'last_reading': last_reading_data,
        'battery_status': battery_status
        }, status=status.HTTP_200_OK)


class SensorReadingsCreateUnauthenticatedView(APIView):
    """Create sensor readings without authentication - for IoT devices"""
    permission_classes = []  # No authentication required
    
    @extend_schema(
        summary="Create sensor reading (unauthenticated)",
        description="Create a new sensor reading using device serial number without authentication - intended for IoT devices",
        request=SensorReadingsCreateSerializer,
        responses={
            201: SensorReadingsSerializer,
            400: OpenApiResponse(description="Validation errors"),
            404: OpenApiResponse(description="Device not found")
        }
    )
    def post(self, request):
        """Create a sensor reading without authentication"""
        serializer = SensorReadingsCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Create the sensor reading
            sensor_reading = serializer.save()
            
            # Return the created reading using the regular serializer
            response_serializer = SensorReadingsSerializer(sensor_reading)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
