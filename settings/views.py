from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    UserSettings, 
    AlertThresholds, 
    NotificationSettings, 
    DataSyncSettings, 
    PrivacySettings
)
from .serializers import (
    UserSettingsSerializer,
    AlertThresholdsSerializer,
    NotificationSettingsSerializer,
    DataSyncSettingsSerializer,
    PrivacySettingsSerializer,
    HiveListSerializer
)
from apiaries.models import Hives


class UserSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for user settings"""
    
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserSettings.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get', 'post', 'patch'])
    def my_settings(self, request):
        """Get or create/update user settings"""
        try:
            settings = UserSettings.objects.get(user=request.user)
        except UserSettings.DoesNotExist:
            settings = None
        
        if request.method == 'GET':
            if settings:
                serializer = self.get_serializer(settings)
                return Response(serializer.data)
            else:
                # Return defaults if no settings exist
                return Response({
                    'timezone': 'UTC',
                    'language': 'en',
                    'temperature_unit': 'Celsius',
                    'weight_unit': 'Kilograms',
                    'date_format': 'DD/MM/YYYY'
                })
        
        elif request.method in ['POST', 'PATCH']:
            if settings:
                serializer = self.get_serializer(settings, data=request.data, partial=True)
            else:
                serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlertThresholdsViewSet(viewsets.ModelViewSet):
    """ViewSet for alert thresholds"""
    
    serializer_class = AlertThresholdsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['hive']
    search_fields = ['hive__name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return AlertThresholds.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def global_thresholds(self, request):
        """Get global alert thresholds"""
        try:
            thresholds = AlertThresholds.objects.get(user=request.user, hive__isnull=True)
            serializer = self.get_serializer(thresholds)
            return Response(serializer.data)
        except AlertThresholds.DoesNotExist:
            return Response(
                {'detail': 'Global thresholds not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post', 'patch'])
    def set_global_thresholds(self, request):
        """Set or update global alert thresholds"""
        try:
            thresholds = AlertThresholds.objects.get(user=request.user, hive__isnull=True)
            serializer = self.get_serializer(thresholds, data=request.data, partial=True)
        except AlertThresholds.DoesNotExist:
            data = request.data.copy()
            data['hive'] = None
            serializer = self.get_serializer(data=data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def hive_thresholds(self, request):
        """Get thresholds for a specific hive"""
        hive_id = request.query_params.get('hive_id')
        if not hive_id:
            return Response(
                {'detail': 'hive_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        hive = get_object_or_404(Hives, id=hive_id, apiary__beekeeper__user=request.user)
        
        try:
            thresholds = AlertThresholds.objects.get(user=request.user, hive=hive)
            serializer = self.get_serializer(thresholds)
            return Response(serializer.data)
        except AlertThresholds.DoesNotExist:
            # Return global thresholds if hive-specific don't exist
            try:
                global_thresholds = AlertThresholds.objects.get(user=request.user, hive__isnull=True)
                serializer = self.get_serializer(global_thresholds)
                data = serializer.data
                data['hive'] = hive_id
                data['hive_name'] = hive.name
                data['is_global'] = True
                return Response(data)
            except AlertThresholds.DoesNotExist:
                return Response(
                    {'detail': 'No thresholds found for this hive or globally'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
    
    @action(detail=False, methods=['get'])
    def available_hives(self, request):
        """Get list of user's hives for threshold setting"""
        hives = Hives.objects.filter(
            apiary__beekeeper__user=request.user,
            is_active=True
        )
        serializer = HiveListSerializer(hives, many=True)
        return Response(serializer.data)


class NotificationSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for notification settings"""
    
    serializer_class = NotificationSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NotificationSettings.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get', 'post', 'patch'])
    def my_settings(self, request):
        """Get or create/update notification settings"""
        try:
            settings = NotificationSettings.objects.get(user=request.user)
        except NotificationSettings.DoesNotExist:
            settings = None
        
        if request.method == 'GET':
            if settings:
                serializer = self.get_serializer(settings)
                return Response(serializer.data)
            else:
                # Return defaults if no settings exist
                return Response({
                    'push_notifications': True,
                    'email_notifications': True,
                    'sms_notifications': False,
                    'alert_sound': True,
                    'quiet_hours_start': '22:00',
                    'quiet_hours_end': '06:00',
                    'critical_alerts_override_quiet': True,
                    'daily_summary_enabled': True,
                    'daily_summary_time': '08:00'
                })
        
        elif request.method in ['POST', 'PATCH']:
            if settings:
                serializer = self.get_serializer(settings, data=request.data, partial=True)
            else:
                serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DataSyncSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for data sync settings"""
    
    serializer_class = DataSyncSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DataSyncSettings.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get', 'post', 'patch'])
    def my_settings(self, request):
        """Get or create/update data sync settings"""
        try:
            settings = DataSyncSettings.objects.get(user=request.user)
        except DataSyncSettings.DoesNotExist:
            settings = None
        
        if request.method == 'GET':
            if settings:
                serializer = self.get_serializer(settings)
                return Response(serializer.data)
            else:
                # Return defaults if no settings exist
                return Response({
                    'auto_sync_enabled': True,
                    'sync_frequency': 'Hourly',
                    'wifi_only_sync': False,
                    'backup_enabled': True,
                    'backup_frequency': 'Weekly',
                    'data_retention_days': 365
                })
        
        elif request.method in ['POST', 'PATCH']:
            if settings:
                serializer = self.get_serializer(settings, data=request.data, partial=True)
            else:
                serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrivacySettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for privacy settings"""
    
    serializer_class = PrivacySettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PrivacySettings.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get', 'post', 'patch'])
    def my_settings(self, request):
        """Get or create/update privacy settings"""
        try:
            settings = PrivacySettings.objects.get(user=request.user)
        except PrivacySettings.DoesNotExist:
            settings = None
        
        if request.method == 'GET':
            if settings:
                serializer = self.get_serializer(settings)
                return Response(serializer.data)
            else:
                # Return defaults if no settings exist
                return Response({
                    'location_sharing': False,
                    'analytics_enabled': True,
                    'crash_reporting': True,
                    'data_sharing_research': False,
                    'profile_visibility': 'Private'
                })
        
        elif request.method in ['POST', 'PATCH']:
            if settings:
                serializer = self.get_serializer(settings, data=request.data, partial=True)
            else:
                serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
