from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Harvests, Alerts
from .serializers import (
    HarvestsSerializer,
    AlertsSerializer,
    HarvestsDetailSerializer,
    AlertsDetailSerializer,
    AlertResolveSerializer
)
from accounts.models import BeekeeperProfile
from .services.alert_checker import AlertChecker

# Optional Celery imports
try:
    from .tasks import check_alerts_task, check_hive_alerts_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False


class HarvestsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Harvests.
    Provides CRUD operations for harvests with filtering and search capabilities.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['hive', 'harvest_date', 'harvested_by']
    search_fields = ['hive__name', 'processing_method', 'quality_notes']
    ordering_fields = ['harvest_date', 'created_at', 'honey_kg', 'total_weight_kg']
    ordering = ['-harvest_date', '-created_at']
    
    def get_queryset(self):
        """Return harvests for the authenticated user's hives only"""
        return Harvests.objects.filter(
            hive__apiary__beekeeper__user=self.request.user
        ).select_related(
            'hive__apiary__beekeeper__user',
            'harvested_by'
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return HarvestsDetailSerializer
        return HarvestsSerializer
    
    def perform_create(self, serializer):
        """Automatically set the harvested_by to the current user"""
        serializer.save(harvested_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get harvest statistics for the user"""
        queryset = self.get_queryset()
        
        # Total harvest statistics
        total_stats = queryset.aggregate(
            total_honey=Sum('honey_kg'),
            total_wax=Sum('wax_kg'),
            total_pollen=Sum('pollen_kg'),
            total_harvests=Count('id')
        )
        
        # Current year statistics
        current_year = timezone.now().year
        year_stats = queryset.filter(
            harvest_date__year=current_year
        ).aggregate(
            yearly_honey=Sum('honey_kg'),
            yearly_wax=Sum('wax_kg'),
            yearly_pollen=Sum('pollen_kg'),
            yearly_harvests=Count('id')
        )
        
        # Top producing hives
        top_hives = queryset.values(
            'hive__id', 'hive__name'
        ).annotate(
            total_honey=Sum('honey_kg')
        ).order_by('-total_honey')[:5]
        
        return Response({
            'total_statistics': {
                'total_honey_kg': total_stats['total_honey'] or 0,
                'total_wax_kg': total_stats['total_wax'] or 0,
                'total_pollen_kg': total_stats['total_pollen'] or 0,
                'total_harvests': total_stats['total_harvests']
            },
            'current_year_statistics': {
                'yearly_honey_kg': year_stats['yearly_honey'] or 0,
                'yearly_wax_kg': year_stats['yearly_wax'] or 0,
                'yearly_pollen_kg': year_stats['yearly_pollen'] or 0,
                'yearly_harvests': year_stats['yearly_harvests']
            },
            'top_producing_hives': list(top_hives)
        })
    
    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """Get monthly harvest summary for current year"""
        current_year = timezone.now().year
        queryset = self.get_queryset().filter(
            harvest_date__year=current_year
        )
        
        monthly_data = []
        for month in range(1, 13):
            month_harvests = queryset.filter(harvest_date__month=month)
            month_stats = month_harvests.aggregate(
                honey=Sum('honey_kg'),
                wax=Sum('wax_kg'),
                pollen=Sum('pollen_kg'),
                count=Count('id')
            )
            
            monthly_data.append({
                'month': month,
                'honey_kg': month_stats['honey'] or 0,
                'wax_kg': month_stats['wax'] or 0,
                'pollen_kg': month_stats['pollen'] or 0,
                'harvest_count': month_stats['count']
            })
        
        return Response(monthly_data)


class AlertsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Alerts.
    Provides CRUD operations for alerts with filtering and search capabilities.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['hive', 'alert_type', 'severity', 'is_resolved']
    search_fields = ['message', 'resolution_notes', 'hive__name']
    ordering_fields = ['created_at', 'severity', 'resolved_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return alerts for the authenticated user's hives only"""
        return Alerts.objects.filter(
            hive__apiary__beekeeper__user=self.request.user
        ).select_related(
            'hive__apiary__beekeeper__user',
            'resolved_by'
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return AlertsDetailSerializer
        return AlertsSerializer
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark an alert as resolved"""
        alert = self.get_object()
        serializer = AlertResolveSerializer(data=request.data)
        
        if serializer.is_valid():
            resolution_notes = serializer.validated_data.get('resolution_notes', '')
            alert.resolve(user=request.user, notes=resolution_notes)
            
            # Return the updated alert
            response_serializer = AlertsDetailSerializer(alert, context={'request': request})
            return Response(
                {
                    'message': 'Alert resolved successfully',
                    'alert': response_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unresolve(self, request, pk=None):
        """Mark a resolved alert as unresolved"""
        alert = self.get_object()
        alert.is_resolved = False
        alert.resolved_at = None
        alert.resolved_by = None
        alert.resolution_notes = ''
        alert.save()
        
        response_serializer = AlertsDetailSerializer(alert, context={'request': request})
        return Response(
            {
                'message': 'Alert marked as unresolved',
                'alert': response_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active (unresolved) alerts"""
        queryset = self.get_queryset().filter(is_resolved=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_severity(self, request):
        """Get alerts grouped by severity"""
        queryset = self.get_queryset().filter(is_resolved=False)
        
        result = {}
        for severity_choice in Alerts.Severity.choices:
            severity = severity_choice[0]
            alerts = queryset.filter(severity=severity)
            result[severity] = {
                'count': alerts.count(),
                'display_name': severity_choice[1],
                'alerts': AlertsSerializer(alerts, many=True, context={'request': request}).data
            }
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get alert statistics"""
        queryset = self.get_queryset()
        
        # Overall statistics
        total_alerts = queryset.count()
        active_alerts = queryset.filter(is_resolved=False).count()
        resolved_alerts = queryset.filter(is_resolved=True).count()
        
        # Statistics by severity
        severity_stats = {}
        for severity_choice in Alerts.Severity.choices:
            severity = severity_choice[0]
            severity_stats[severity] = {
                'total': queryset.filter(severity=severity).count(),
                'active': queryset.filter(severity=severity, is_resolved=False).count(),
                'display_name': severity_choice[1]
            }
        
        # Statistics by alert type
        type_stats = {}
        for type_choice in Alerts.AlertType.choices:
            alert_type = type_choice[0]
            type_stats[alert_type] = {
                'total': queryset.filter(alert_type=alert_type).count(),
                'active': queryset.filter(alert_type=alert_type, is_resolved=False).count(),
                'display_name': type_choice[1]
            }
        
        return Response({
            'overview': {
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'resolved_alerts': resolved_alerts,
                'resolution_rate': round((resolved_alerts / total_alerts * 100), 2) if total_alerts > 0 else 0
            },
            'by_severity': severity_stats,
            'by_type': type_stats
        })
    
    @action(detail=False, methods=['post'])
    def check_all_alerts(self, request):
        """Manually trigger alert check for all user's hives"""
        try:
            # Use synchronous alert checking for immediate response
            alert_checker = AlertChecker()
            
            # Get only user's hives
            from apiaries.models import Hives
            user_hives = Hives.objects.filter(
                apiary__beekeeper__user=request.user,
                is_active=True,
                has_smart_device=True
            )
            
            if not user_hives.exists():
                return Response({
                    'message': 'No active hives with smart devices found',
                    'alerts_created': 0,
                    'hives_checked': 0
                }, status=status.HTTP_200_OK)
            
            total_alerts_created = 0
            hives_checked = 0
            
            for hive in user_hives:
                alerts_created = alert_checker.check_hive_alerts(hive)
                total_alerts_created += alerts_created
                hives_checked += 1
            
            return Response({
                'message': f'Alert check completed for {hives_checked} hives',
                'alerts_created': total_alerts_created,
                'hives_checked': hives_checked,
                'timestamp': timezone.now()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error during alert check: {str(e)}',
                'timestamp': timezone.now()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def check_hive_alerts(self, request):
        """Manually trigger alert check for a specific hive"""
        hive_id = request.data.get('hive_id')
        
        if not hive_id:
            return Response({
                'error': 'hive_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from apiaries.models import Hives
            hive = Hives.objects.get(
                id=hive_id,
                apiary__beekeeper__user=request.user
            )
            
            if not hive.is_active:
                return Response({
                    'error': 'Hive is not active',
                    'hive_id': hive_id
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not hive.has_smart_device:
                return Response({
                    'error': 'Hive does not have a smart device',
                    'hive_id': hive_id
                }, status=status.HTTP_400_BAD_REQUEST)
            
            alert_checker = AlertChecker()
            alerts_created = alert_checker.check_hive_alerts(hive)
            
            return Response({
                'message': f'Alert check completed for hive {hive.name}',
                'alerts_created': alerts_created,
                'hive_id': hive_id,
                'hive_name': hive.name,
                'timestamp': timezone.now()
            }, status=status.HTTP_200_OK)
            
        except Hives.DoesNotExist:
            return Response({
                'error': 'Hive not found or not owned by user',
                'hive_id': hive_id
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error during hive alert check: {str(e)}',
                'hive_id': hive_id,
                'timestamp': timezone.now()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def schedule_alert_check(self, request):
        """Schedule an asynchronous alert check using Celery"""
        if not CELERY_AVAILABLE:
            return Response({
                'error': 'Celery is not available. Use check_all_alerts or check_hive_alerts for synchronous execution.',
                'timestamp': timezone.now()
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        try:
            hive_id = request.data.get('hive_id')
            
            if hive_id:
                # Schedule check for specific hive
                from apiaries.models import Hives
                hive = Hives.objects.get(
                    id=hive_id,
                    apiary__beekeeper__user=request.user
                )
                
                task = check_hive_alerts_task.delay(hive_id)
                
                return Response({
                    'message': f'Alert check scheduled for hive {hive.name}',
                    'task_id': task.id,
                    'hive_id': hive_id,
                    'hive_name': hive.name,
                    'timestamp': timezone.now()
                }, status=status.HTTP_202_ACCEPTED)
            else:
                # Schedule check for all hives
                task = check_alerts_task.delay()
                
                return Response({
                    'message': 'Alert check scheduled for all hives',
                    'task_id': task.id,
                    'timestamp': timezone.now()
                }, status=status.HTTP_202_ACCEPTED)
                
        except Hives.DoesNotExist:
            return Response({
                'error': 'Hive not found or not owned by user',
                'hive_id': hive_id
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error scheduling alert check: {str(e)}',
                'timestamp': timezone.now()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def production_stats(request):
    """
    Get production statistics for the authenticated user.
    """
    # Get user's harvests
    harvests = Harvests.objects.filter(
        hive__apiary__beekeeper__user=request.user
    ).select_related(
        'hive__apiary__beekeeper__user',
        'harvested_by'
    )
    
    # Total harvest statistics
    total_stats = harvests.aggregate(
        total_honey=Sum('honey_kg'),
        total_wax=Sum('wax_kg'),
        total_pollen=Sum('pollen_kg'),
        total_harvests=Count('id')
    )
    
    # Current year statistics
    current_year = timezone.now().year
    year_stats = harvests.filter(
        harvest_date__year=current_year
    ).aggregate(
        yearly_honey=Sum('honey_kg'),
        yearly_wax=Sum('wax_kg'),
        yearly_pollen=Sum('pollen_kg'),
        yearly_harvests=Count('id')
    )
    
    # Top producing hives
    top_hives = harvests.values(
        'hive__id', 'hive__name'
    ).annotate(
        total_honey=Sum('honey_kg')
    ).order_by('-total_honey')[:5]
    
    return Response({
        'total_statistics': {
            'total_honey_kg': total_stats['total_honey'] or 0,
            'total_wax_kg': total_stats['total_wax'] or 0,
            'total_pollen_kg': total_stats['total_pollen'] or 0,
            'total_harvests': total_stats['total_harvests']
        },
        'current_year_statistics': {
            'yearly_honey_kg': year_stats['yearly_honey'] or 0,
            'yearly_wax_kg': year_stats['yearly_wax'] or 0,
            'yearly_pollen_kg': year_stats['yearly_pollen'] or 0,
            'yearly_harvests': year_stats['yearly_harvests']
        },
        'top_producing_hives': list(top_hives)
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def alert_stats(request):
    """
    Get alert statistics for the authenticated user.
    """
    # Get user's alerts
    alerts = Alerts.objects.filter(
        hive__apiary__beekeeper__user=request.user
    ).select_related(
        'hive__apiary__beekeeper__user',
        'resolved_by'
    )
    
    # Overall statistics
    total_alerts = alerts.count()
    active_alerts = alerts.filter(is_resolved=False).count()
    resolved_alerts = alerts.filter(is_resolved=True).count()
    
    # Statistics by severity
    severity_stats = {}
    for severity_choice in Alerts.Severity.choices:
        severity = severity_choice[0]
        severity_stats[severity] = {
            'total': alerts.filter(severity=severity).count(),
            'active': alerts.filter(severity=severity, is_resolved=False).count(),
            'display_name': severity_choice[1]
        }
    
    # Statistics by alert type
    type_stats = {}
    for type_choice in Alerts.AlertType.choices:
        alert_type = type_choice[0]
        type_stats[alert_type] = {
            'total': alerts.filter(alert_type=alert_type).count(),
            'active': alerts.filter(alert_type=alert_type, is_resolved=False).count(),
            'display_name': type_choice[1]
        }
    
    return Response({
        'overview': {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'resolved_alerts': resolved_alerts,
            'resolution_rate': round((resolved_alerts / total_alerts * 100), 2) if total_alerts > 0 else 0
        },
        'by_severity': severity_stats,
        'by_type': type_stats
    })
