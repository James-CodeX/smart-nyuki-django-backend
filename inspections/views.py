from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Case, When, IntegerField
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.db.models.functions import Extract

from .models import InspectionSchedules, InspectionReports
from .serializers import (
    InspectionSchedulesReadSerializer,
    InspectionSchedulesWriteSerializer,
    InspectionReportsReadSerializer,
    InspectionReportsWriteSerializer,
    InspectionScheduleCompletionSerializer,
    InspectionStatisticsSerializer
)
from .filters import InspectionSchedulesFilter, InspectionReportsFilter
from .permissions import IsOwnerOrReadOnly


class InspectionSchedulesViewSet(viewsets.ModelViewSet):
    """ViewSet for managing inspection schedules"""
    
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = InspectionSchedulesFilter
    search_fields = ['notes', 'hive__name', 'hive__apiary__name']
    ordering_fields = ['scheduled_date', 'created_at', 'updated_at']
    ordering = ['scheduled_date']
    
    def get_queryset(self):
        """Filter schedules to only those belonging to the current user"""
        user = self.request.user
        
        if not hasattr(user, 'beekeeper_profile'):
            return InspectionSchedules.objects.none()
        
        return InspectionSchedules.objects.filter(
            hive__apiary__beekeeper=user.beekeeper_profile
        ).select_related(
            'hive',
            'hive__apiary',
            'hive__apiary__beekeeper',
            'hive__apiary__beekeeper__user'
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return InspectionSchedulesWriteSerializer
        return InspectionSchedulesReadSerializer
    
    @action(detail=True, methods=['post'], url_path='complete')
    def complete_inspection(self, request, pk=None):
        """Mark an inspection schedule as completed"""
        schedule = self.get_object()
        serializer = InspectionScheduleCompletionSerializer(data=request.data)
        
        if serializer.is_valid():
            schedule.is_completed = serializer.validated_data['is_completed']
            if 'notes' in serializer.validated_data:
                schedule.notes = serializer.validated_data['notes']
            schedule.save()
            
            return Response({
                'message': f'Inspection schedule {"completed" if schedule.is_completed else "marked as incomplete"}',
                'is_completed': schedule.is_completed
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming_inspections(self, request):
        """Get upcoming inspections for the next 7 days"""
        end_date = date.today() + timedelta(days=7)
        
        queryset = self.get_queryset().filter(
            scheduled_date__gte=date.today(),
            scheduled_date__lte=end_date,
            is_completed=False
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue_inspections(self, request):
        """Get overdue inspections"""
        queryset = self.get_queryset().filter(
            scheduled_date__lt=date.today(),
            is_completed=False
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Get inspection schedule statistics"""
        queryset = self.get_queryset()
        
        total_schedules = queryset.count()
        completed_schedules = queryset.filter(is_completed=True).count()
        pending_schedules = queryset.filter(
            is_completed=False,
            scheduled_date__gte=date.today()
        ).count()
        overdue_schedules = queryset.filter(
            is_completed=False,
            scheduled_date__lt=date.today()
        ).count()
        
        stats = {
            'total_schedules': total_schedules,
            'completed_schedules': completed_schedules,
            'pending_schedules': pending_schedules,
            'overdue_schedules': overdue_schedules,
            'completion_rate': (completed_schedules / total_schedules * 100) if total_schedules > 0 else 0
        }
        
        return Response(stats)


class InspectionReportsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing inspection reports"""
    
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = InspectionReportsFilter
    search_fields = [
        'notes', 'pest_observations', 'actions_taken',
        'hive__name', 'hive__apiary__name', 'inspector__first_name',
        'inspector__last_name'
    ]
    ordering_fields = ['inspection_date', 'created_at', 'colony_health', 'honey_level']
    ordering = ['-inspection_date']
    
    def get_queryset(self):
        """Filter reports to only those belonging to the current user"""
        user = self.request.user
        
        if not hasattr(user, 'beekeeper_profile'):
            return InspectionReports.objects.none()
        
        return InspectionReports.objects.filter(
            hive__apiary__beekeeper=user.beekeeper_profile
        ).select_related(
            'schedule',
            'hive',
            'hive__apiary',
            'hive__apiary__beekeeper',
            'hive__apiary__beekeeper__user',
            'inspector'
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return InspectionReportsWriteSerializer
        return InspectionReportsReadSerializer
    
    @action(detail=False, methods=['get'], url_path='recent')
    def recent_reports(self, request):
        """Get recent inspection reports from the last 30 days"""
        start_date = date.today() - timedelta(days=30)
        
        queryset = self.get_queryset().filter(
            inspection_date__gte=start_date
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='by-hive/(?P<hive_id>[^/.]+)')
    def reports_by_hive(self, request, hive_id=None):
        """Get inspection reports for a specific hive"""
        queryset = self.get_queryset().filter(hive_id=hive_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Get inspection report statistics"""
        queryset = self.get_queryset()
        
        # Basic counts
        total_reports = queryset.count()
        current_month = datetime.now().month
        reports_this_month = queryset.filter(
            inspection_date__month=current_month
        ).count()
        
        # Health statistics
        health_stats = queryset.aggregate(
            excellent_count=Count(
                Case(When(colony_health='Excellent', then=1),
                     output_field=IntegerField())
            ),
            good_count=Count(
                Case(When(colony_health='Good', then=1),
                     output_field=IntegerField())
            ),
            fair_count=Count(
                Case(When(colony_health='Fair', then=1),
                     output_field=IntegerField())
            ),
            poor_count=Count(
                Case(When(colony_health='Poor', then=1),
                     output_field=IntegerField())
            )
        )
        
        # Calculate average health (numeric representation)
        health_weights = {
            'Poor': 1, 'Fair': 2, 'Good': 3, 'Excellent': 4
        }
        
        if total_reports > 0:
            total_weight = (
                health_stats['poor_count'] * 1 +
                health_stats['fair_count'] * 2 +
                health_stats['good_count'] * 3 +
                health_stats['excellent_count'] * 4
            )
            avg_health_numeric = total_weight / total_reports
            
            # Convert back to text
            if avg_health_numeric <= 1.5:
                average_colony_health = 'Poor'
            elif avg_health_numeric <= 2.5:
                average_colony_health = 'Fair'
            elif avg_health_numeric <= 3.5:
                average_colony_health = 'Good'
            else:
                average_colony_health = 'Excellent'
        else:
            average_colony_health = 'N/A'
        
        # Queen presence rate
        queen_reports = queryset.exclude(queen_present__isnull=True)
        queen_present_count = queen_reports.filter(queen_present=True).count()
        queen_presence_rate = (
            (queen_present_count / queen_reports.count() * 100)
            if queen_reports.count() > 0 else 0
        )
        
        stats = {
            'total_reports': total_reports,
            'reports_this_month': reports_this_month,
            'average_colony_health': average_colony_health,
            'queen_presence_rate': round(queen_presence_rate, 2),
            'health_distribution': health_stats
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'], url_path='health-trends')
    def health_trends(self, request):
        """Get colony health trends over time"""
        queryset = self.get_queryset()
        
        # Group by month and calculate health statistics
        monthly_stats = queryset.extra(
            select={'month': 'strftime("%%Y-%%m", inspection_date)'}
        ).values('month').annotate(
            total_reports=Count('id'),
            excellent_count=Count(
                Case(When(colony_health='Excellent', then=1),
                     output_field=IntegerField())
            ),
            good_count=Count(
                Case(When(colony_health='Good', then=1),
                     output_field=IntegerField())
            ),
            fair_count=Count(
                Case(When(colony_health='Fair', then=1),
                     output_field=IntegerField())
            ),
            poor_count=Count(
                Case(When(colony_health='Poor', then=1),
                     output_field=IntegerField())
            )
        ).order_by('month')
        
        return Response(list(monthly_stats))
