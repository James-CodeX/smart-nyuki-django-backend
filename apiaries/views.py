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
