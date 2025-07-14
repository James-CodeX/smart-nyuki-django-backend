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
    
    @action(detail=True, methods=['get'])
    def smart_metrics(self, request, pk=None):
        """Get smart metrics for an apiary based on its smart hives"""
        from django.db.models import Avg, Sum, Count, Min, Max
        from devices.models import SensorReadings
        from django.utils import timezone
        from datetime import timedelta
        
        apiary = self.get_object()
        
        # Get active hives in this apiary
        active_hives = apiary.hives.filter(is_active=True)
        smart_hives = active_hives.filter(has_smart_device=True)
        
        # Determine apiary smart status
        total_hives = active_hives.count()
        smart_hives_count = smart_hives.count()
        
        if total_hives == 0:
            smart_status = 'no_hives'
        elif smart_hives_count == 0:
            smart_status = 'not_smart'
        elif smart_hives_count == total_hives:
            smart_status = 'fully_smart'
        else:
            smart_status = 'partially_smart'
        
        # Get time filters
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_week = now - timedelta(days=7)
        
        # Get sensor readings from all smart devices in this apiary
        readings_queryset = SensorReadings.objects.filter(
            device__hive__apiary=apiary,
            device__hive__is_active=True,
            device__is_active=True
        )
        
        # Calculate metrics - Get latest reading from each smart hive
        latest_readings = []
        for hive in smart_hives:
            latest_reading = SensorReadings.objects.filter(
                device__hive=hive,
                device__is_active=True
            ).order_by('-timestamp').first()
            if latest_reading:
                latest_readings.append(latest_reading)
        
        readings_last_24h = readings_queryset.filter(timestamp__gte=last_24h)
        readings_last_week = readings_queryset.filter(timestamp__gte=last_week)
        
        # Calculate current metrics (from latest readings of each hive)
        current_metrics = None
        if latest_readings:
            # Calculate averages and total weight from latest readings of each smart hive
            total_temperature, total_humidity, total_sound_level, total_weight = 0.0, 0.0, 0.0, 0.0
            temp_count_current, humidity_count_current, sound_count_current = 0, 0, 0
            
            # Collect all values for min/max calculations
            temperatures = []
            humidities = []
            weights = []
            
            for latest_reading in latest_readings:
                if latest_reading.temperature:
                    total_temperature += float(latest_reading.temperature)
                    temp_count_current += 1
                    temperatures.append(float(latest_reading.temperature))
                if latest_reading.humidity:
                    total_humidity += float(latest_reading.humidity)
                    humidity_count_current += 1
                    humidities.append(float(latest_reading.humidity))
                if latest_reading.sound_level:
                    total_sound_level += float(latest_reading.sound_level)
                    sound_count_current += 1
                if latest_reading.weight:
                    total_weight += float(latest_reading.weight)
                    weights.append(float(latest_reading.weight))
            
            avg_temperature = total_temperature / temp_count_current if temp_count_current > 0 else 0
            avg_humidity = total_humidity / humidity_count_current if humidity_count_current > 0 else 0
            avg_sound_level = total_sound_level / sound_count_current if sound_count_current > 0 else 0
            avg_weight = sum(weights) / len(weights) if weights else 0

            # Calculate min/max values from latest readings
            min_temperature = min(temperatures) if temperatures else 0
            max_temperature = max(temperatures) if temperatures else 0
            min_humidity = min(humidities) if humidities else 0
            max_humidity = max(humidities) if humidities else 0
            
            current_stats = {
                'avg_temperature': avg_temperature,
                'avg_humidity': avg_humidity,
                'avg_weight': avg_weight,
                'avg_sound_level': avg_sound_level,
                'min_temperature': min_temperature,
                'max_temperature': max_temperature,
                'min_humidity': min_humidity,
                'max_humidity': max_humidity,
                'total_weight': total_weight
            }
            
            current_metrics = {
                'average_temperature': round(float(current_stats['avg_temperature'] or 0), 2),
                'average_humidity': round(float(current_stats['avg_humidity'] or 0), 2),
                'total_weight': round(total_weight, 2),
                'average_weight': round(float(current_stats['avg_weight'] or 0), 2),
                'average_sound_level': round(float(current_stats['avg_sound_level'] or 0), 2),
                'temperature_range': {
                    'min': round(float(current_stats['min_temperature'] or 0), 2),
                    'max': round(float(current_stats['max_temperature'] or 0), 2)
                },
                'humidity_range': {
                    'min': round(float(current_stats['min_humidity'] or 0), 2),
                    'max': round(float(current_stats['max_humidity'] or 0), 2)
                }
            }
        
        # Calculate 24h metrics - Use ALL readings from last 24 hours
        metrics_24h = None
        if readings_last_24h.exists():
            # Calculate averages from ALL readings in the last 24 hours
            stats_24h = readings_last_24h.aggregate(
                avg_temperature=Avg('temperature'),
                avg_humidity=Avg('humidity'),
                avg_weight=Avg('weight'),
                avg_sound_level=Avg('sound_level'),
                total_weight=Sum('weight')
            )
            
            metrics_24h = {
                'average_temperature': round(float(stats_24h['avg_temperature'] or 0), 2),
                'average_humidity': round(float(stats_24h['avg_humidity'] or 0), 2),
                'total_weight': round(float(stats_24h['total_weight'] or 0), 2),
                'average_weight': round(float(stats_24h['avg_weight'] or 0), 2),
                'average_sound_level': round(float(stats_24h['avg_sound_level'] or 0), 2),
                'readings_count': readings_last_24h.count()
            }
        
        # Calculate weekly metrics - Use ALL readings from last 7 days
        metrics_week = None
        if readings_last_week.exists():
            # Calculate averages from ALL readings in the last 7 days
            stats_week = readings_last_week.aggregate(
                avg_temperature=Avg('temperature'),
                avg_humidity=Avg('humidity'),
                avg_weight=Avg('weight'),
                avg_sound_level=Avg('sound_level'),
                total_weight=Sum('weight')
            )
            
            metrics_week = {
                'average_temperature': round(float(stats_week['avg_temperature'] or 0), 2),
                'average_humidity': round(float(stats_week['avg_humidity'] or 0), 2),
                'total_weight': round(float(stats_week['total_weight'] or 0), 2),
                'average_weight': round(float(stats_week['avg_weight'] or 0), 2),
                'average_sound_level': round(float(stats_week['avg_sound_level'] or 0), 2),
                'readings_count': readings_last_week.count()
            }
        
        # Get latest reading from each smart hive
        hive_latest_readings = []
        for hive in smart_hives:
            latest_reading = SensorReadings.objects.filter(
                device__hive=hive,
                device__is_active=True
            ).order_by('-timestamp').first()
            
            if latest_reading:
                from devices.serializers import SensorReadingsSerializer
                hive_latest_readings.append({
                    'hive_id': str(hive.id),
                    'hive_name': hive.name,
                    'latest_reading': SensorReadingsSerializer(latest_reading).data
                })
        
        return Response({
            'apiary_id': str(apiary.id),
            'apiary_name': apiary.name,
            'smart_status': smart_status,
            'smart_status_display': {
                'no_hives': 'No Hives',
                'not_smart': 'Not Smart',
                'partially_smart': 'Partially Smart',
                'fully_smart': 'Fully Smart'
            }.get(smart_status, 'Unknown'),
            'hive_counts': {
                'total_hives': total_hives,
                'smart_hives': smart_hives_count,
                'non_smart_hives': total_hives - smart_hives_count,
                'smart_percentage': round((smart_hives_count / total_hives * 100), 2) if total_hives > 0 else 0
            },
            'current_metrics': current_metrics,
            'last_24h_metrics': metrics_24h,
            'last_week_metrics': metrics_week,
            'hive_latest_readings': hive_latest_readings,
            'total_readings': readings_queryset.count(),
            'last_updated': latest_readings[0].timestamp if latest_readings else None
        })
    
    @action(detail=False, methods=['get'])
    def smart_overview(self, request):
        """Get smart overview for all user's apiaries"""
        apiaries = self.get_queryset()
        
        overview_data = []
        totals = {
            'total_apiaries': 0,
            'fully_smart': 0,
            'partially_smart': 0,
            'not_smart': 0,
            'no_hives': 0,
            'total_hives': 0,
            'total_smart_hives': 0,
            'total_readings': 0
        }
        
        for apiary in apiaries:
            # Get hive counts
            active_hives = apiary.hives.filter(is_active=True)
            smart_hives = active_hives.filter(has_smart_device=True)
            
            total_hives = active_hives.count()
            smart_hives_count = smart_hives.count()
            
            # Determine smart status
            if total_hives == 0:
                smart_status = 'no_hives'
            elif smart_hives_count == 0:
                smart_status = 'not_smart'
            elif smart_hives_count == total_hives:
                smart_status = 'fully_smart'
            else:
                smart_status = 'partially_smart'
            
            # Get basic sensor data count
            from devices.models import SensorReadings
            readings_count = SensorReadings.objects.filter(
                device__hive__apiary=apiary,
                device__hive__is_active=True,
                device__is_active=True
            ).count()
            
            # Add to overview
            overview_data.append({
                'apiary_id': str(apiary.id),
                'apiary_name': apiary.name,
                'smart_status': smart_status,
                'smart_status_display': {
                    'no_hives': 'No Hives',
                    'not_smart': 'Not Smart',
                    'partially_smart': 'Partially Smart',
                    'fully_smart': 'Fully Smart'
                }.get(smart_status, 'Unknown'),
                'hive_counts': {
                    'total_hives': total_hives,
                    'smart_hives': smart_hives_count,
                    'non_smart_hives': total_hives - smart_hives_count,
                    'smart_percentage': round((smart_hives_count / total_hives * 100), 2) if total_hives > 0 else 0
                },
                'total_readings': readings_count,
                'has_metrics': smart_hives_count > 0
            })
            
            # Update totals
            totals['total_apiaries'] += 1
            totals[smart_status] += 1
            totals['total_hives'] += total_hives
            totals['total_smart_hives'] += smart_hives_count
            totals['total_readings'] += readings_count
        
        return Response({
            'apiaries': overview_data,
            'summary': {
                'total_apiaries': totals['total_apiaries'],
                'fully_smart_apiaries': totals['fully_smart'],
                'partially_smart_apiaries': totals['partially_smart'],
                'not_smart_apiaries': totals['not_smart'],
                'no_hives_apiaries': totals['no_hives'],
                'total_hives': totals['total_hives'],
                'total_smart_hives': totals['total_smart_hives'],
                'total_readings': totals['total_readings'],
                'smart_apiaries_percentage': round(
                    ((totals['fully_smart'] + totals['partially_smart']) / totals['total_apiaries'] * 100), 2
                ) if totals['total_apiaries'] > 0 else 0
            }
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
