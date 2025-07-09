from django.shortcuts import render
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Apiaries, Hives
from .serializers import (
    ApiariesSerializer, 
    HivesSerializer,
    ApiariesDetailSerializer,
    HivesDetailSerializer
)
from accounts.models import BeekeeperProfile


class ApiariesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Apiaries.
    Provides CRUD operations for apiaries with filtering and search capabilities.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['beekeeper', 'name']
    search_fields = ['name', 'address', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return apiaries for the authenticated user only"""
        return Apiaries.objects.filter(
            beekeeper__user=self.request.user,
            deleted_at__isnull=True
        ).select_related('beekeeper__user').prefetch_related('hives')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return ApiariesDetailSerializer
        return ApiariesSerializer
    
    def perform_create(self, serializer):
        """Automatically set the beekeeper to the current user's profile"""
        try:
            beekeeper_profile = BeekeeperProfile.objects.get(user=self.request.user)
            serializer.save(beekeeper=beekeeper_profile)
        except BeekeeperProfile.DoesNotExist:
            raise serializers.ValidationError(
                "You must have a beekeeper profile to create apiaries."
            )
    
    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        """Soft delete an apiary"""
        apiary = self.get_object()
        apiary.soft_delete()
        return Response(
            {'message': 'Apiary successfully deleted'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def hives(self, request, pk=None):
        """Get all hives for a specific apiary"""
        apiary = self.get_object()
        hives = apiary.hives.filter(is_active=True)
        serializer = HivesSerializer(hives, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def available_hives(self, request, pk=None):
        """Get available hives for smart device assignment in a specific apiary"""
        apiary = self.get_object()
        # Filter hives that do not have a smart device
        unassigned_hives = apiary.hives.filter(
            is_active=True,
            has_smart_device=False
        )
        
        # Create response with unassigned option and available hives
        response_data = {
            'apiary': {
                'id': str(apiary.id),
                'name': apiary.name
            },
            'available_options': [
                {
                    'id': None,
                    'name': 'Leave unassigned',
                    'type': 'unassigned',
                    'description': 'Device will not be assigned to any hive'
                }
            ]
        }
        
        # Add unassigned hives as options
        for hive in unassigned_hives:
            response_data['available_options'].append({
                'id': str(hive.id),
                'name': hive.name,
                'type': 'hive',
                'hive_type': hive.get_type_display(),
                'installation_date': hive.installation_date,
                'description': f'{hive.get_type_display()} hive installed on {hive.installation_date}'
            })
        
        return Response(response_data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a specific apiary"""
        apiary = self.get_object()
        hives = apiary.hives.all()
        
        # Count hives by different criteria
        total_hives = hives.count()
        active_hives = hives.filter(is_active=True).count()
        inactive_hives = total_hives - active_hives
        smart_hives = hives.filter(has_smart_device=True).count()
        
        # Group hives by type
        hive_types = {}
        for hive_type, display_name in Hives.HiveType.choices:
            count = hives.filter(type=hive_type).count()
            if count > 0:
                hive_types[display_name] = count
        
        return Response({
            'total_hives': total_hives,
            'active_hives': active_hives,
            'inactive_hives': inactive_hives,
            'smart_hives': smart_hives,
            'hive_types': hive_types
        })
    
    @action(detail=False, methods=['get'])
    def overall_stats(self, request):
        """Get overall statistics for user's apiaries"""
        queryset = self.get_queryset()
        total_apiaries = queryset.count()
        total_hives = sum(apiary.hives.filter(is_active=True).count() for apiary in queryset)
        
        return Response({
            'total_apiaries': total_apiaries,
            'total_hives': total_hives,
            'average_hives_per_apiary': round(total_hives / total_apiaries, 2) if total_apiaries > 0 else 0
        })


class HivesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Hives.
    Provides CRUD operations for hives with filtering and search capabilities.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['apiary', 'type', 'has_smart_device', 'is_active']
    search_fields = ['name']
    ordering_fields = ['created_at', 'name', 'installation_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return hives for the authenticated user only"""
        return Hives.objects.filter(
            apiary__beekeeper__user=self.request.user
        ).select_related('apiary__beekeeper__user')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return HivesDetailSerializer
        return HivesSerializer
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a hive"""
        hive = self.get_object()
        hive.is_active = False
        hive.save()
        return Response(
            {'message': 'Hive successfully deactivated'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a hive"""
        hive = self.get_object()
        hive.is_active = True
        hive.save()
        return Response(
            {'message': 'Hive successfully activated'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get hives grouped by type"""
        queryset = self.get_queryset().filter(is_active=True)
        
        result = {}
        for choice in Hives.HiveType.choices:
            hive_type = choice[0]
            count = queryset.filter(type=hive_type).count()
            result[hive_type] = {
                'count': count,
                'display_name': choice[1]
            }
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def sensor_readings(self, request, pk=None):
        """Get sensor readings for a specific hive"""
        hive = self.get_object()
        
        # Get all smart devices assigned to this hive
        from devices.models import SensorReadings
        from devices.serializers import SensorReadingsSerializer
        
        # Get query parameters
        limit = int(request.GET.get('limit', 10))
        ordering = request.GET.get('ordering', '-timestamp')
        
        # Get sensor readings from all devices assigned to this hive
        readings = SensorReadings.objects.filter(
            device__hive=hive,
            device__is_active=True
        ).select_related('device').order_by(ordering)[:limit]
        
        # Count total readings and devices
        total_readings = SensorReadings.objects.filter(
            device__hive=hive,
            device__is_active=True
        ).count()
        
        device_count = hive.smart_devices.filter(is_active=True).count()
        
        # Serialize the readings
        serializer = SensorReadingsSerializer(readings, many=True)
        
        return Response({
            'hive_id': str(hive.id),
            'hive_name': hive.name,
            'device_count': device_count,
            'total_readings': total_readings,
            'readings': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def latest_sensor_reading(self, request, pk=None):
        """Get the latest sensor reading for a specific hive"""
        hive = self.get_object()
        
        from devices.models import SensorReadings
        from devices.serializers import SensorReadingsSerializer
        
        # Get the most recent sensor reading from any device assigned to this hive
        latest_reading = SensorReadings.objects.filter(
            device__hive=hive,
            device__is_active=True
        ).select_related('device').order_by('-timestamp').first()
        
        # Serialize the reading if it exists
        latest_reading_data = None
        if latest_reading:
            latest_reading_data = SensorReadingsSerializer(latest_reading).data
        
        return Response({
            'hive_id': str(hive.id),
            'hive_name': hive.name,
            'has_smart_device': hive.has_smart_device,
            'latest_reading': latest_reading_data
        })
