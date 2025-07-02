import django_filters
from django_filters import rest_framework as filters
from datetime import date, timedelta
from django.db import models
from .models import InspectionSchedules, InspectionReports


class InspectionSchedulesFilter(filters.FilterSet):
    """Filter set for inspection schedules"""
    
    # Date filters
    scheduled_date = django_filters.DateFilter()
    scheduled_date_from = django_filters.DateFilter(
        field_name='scheduled_date', 
        lookup_expr='gte',
        label='Scheduled from date'
    )
    scheduled_date_to = django_filters.DateFilter(
        field_name='scheduled_date', 
        lookup_expr='lte',
        label='Scheduled to date'
    )
    
    # Status filters
    is_completed = django_filters.BooleanFilter()
    is_overdue = django_filters.BooleanFilter(
        method='filter_overdue',
        label='Is overdue'
    )
    is_upcoming = django_filters.BooleanFilter(
        method='filter_upcoming',
        label='Is upcoming (next 7 days)'
    )
    
    # Hive and apiary filters
    hive = django_filters.UUIDFilter(field_name='hive__id')
    hive_name = django_filters.CharFilter(
        field_name='hive__name', 
        lookup_expr='icontains'
    )
    apiary = django_filters.UUIDFilter(field_name='hive__apiary__id')
    apiary_name = django_filters.CharFilter(
        field_name='hive__apiary__name', 
        lookup_expr='icontains'
    )
    
    # Weather condition filter
    weather_conditions = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = InspectionSchedules
        fields = [
            'scheduled_date', 'scheduled_date_from', 'scheduled_date_to',
            'is_completed', 'is_overdue', 'is_upcoming',
            'hive', 'hive_name', 'apiary', 'apiary_name',
            'weather_conditions'
        ]
    
    def filter_overdue(self, queryset, name, value):
        """Filter for overdue inspections"""
        if value:
            return queryset.filter(
                scheduled_date__lt=date.today(),
                is_completed=False
            )
        return queryset
    
    def filter_upcoming(self, queryset, name, value):
        """Filter for upcoming inspections in the next 7 days"""
        if value:
            end_date = date.today() + timedelta(days=7)
            return queryset.filter(
                scheduled_date__gte=date.today(),
                scheduled_date__lte=end_date,
                is_completed=False
            )
        return queryset


class InspectionReportsFilter(filters.FilterSet):
    """Filter set for inspection reports"""
    
    # Date filters
    inspection_date = django_filters.DateFilter()
    inspection_date_from = django_filters.DateFilter(
        field_name='inspection_date', 
        lookup_expr='gte',
        label='Inspection from date'
    )
    inspection_date_to = django_filters.DateFilter(
        field_name='inspection_date', 
        lookup_expr='lte',
        label='Inspection to date'
    )
    
    # Inspector filters
    inspector = django_filters.UUIDFilter(field_name='inspector__id')
    inspector_name = django_filters.CharFilter(
        method='filter_inspector_name',
        label='Inspector name'
    )
    
    # Hive and apiary filters
    hive = django_filters.UUIDFilter(field_name='hive__id')
    hive_name = django_filters.CharFilter(
        field_name='hive__name', 
        lookup_expr='icontains'
    )
    apiary = django_filters.UUIDFilter(field_name='hive__apiary__id')
    apiary_name = django_filters.CharFilter(
        field_name='hive__apiary__name', 
        lookup_expr='icontains'
    )
    
    # Health and assessment filters
    queen_present = django_filters.BooleanFilter()
    honey_level = django_filters.ChoiceFilter(
        choices=InspectionReports.HoneyLevel.choices
    )
    colony_health = django_filters.ChoiceFilter(
        choices=InspectionReports.ColonyHealth.choices
    )
    brood_pattern = django_filters.ChoiceFilter(
        choices=InspectionReports.BroodPattern.choices
    )
    
    # Varroa mite count filters
    varroa_mite_count = django_filters.NumberFilter()
    varroa_mite_count_min = django_filters.NumberFilter(
        field_name='varroa_mite_count', 
        lookup_expr='gte'
    )
    varroa_mite_count_max = django_filters.NumberFilter(
        field_name='varroa_mite_count', 
        lookup_expr='lte'
    )
    
    # Recent reports filter
    is_recent = django_filters.BooleanFilter(
        method='filter_recent',
        label='Recent reports (last 30 days)'
    )
    
    # Schedule link filter
    has_schedule = django_filters.BooleanFilter(
        method='filter_has_schedule',
        label='Has linked schedule'
    )
    
    class Meta:
        model = InspectionReports
        fields = [
            'inspection_date', 'inspection_date_from', 'inspection_date_to',
            'inspector', 'inspector_name',
            'hive', 'hive_name', 'apiary', 'apiary_name',
            'queen_present', 'honey_level', 'colony_health', 'brood_pattern',
            'varroa_mite_count', 'varroa_mite_count_min', 'varroa_mite_count_max',
            'is_recent', 'has_schedule'
        ]
    
    def filter_inspector_name(self, queryset, name, value):
        """Filter by inspector's first or last name"""
        return queryset.filter(
            models.Q(inspector__first_name__icontains=value) |
            models.Q(inspector__last_name__icontains=value)
        )
    
    def filter_recent(self, queryset, name, value):
        """Filter for recent reports (last 30 days)"""
        if value:
            start_date = date.today() - timedelta(days=30)
            return queryset.filter(inspection_date__gte=start_date)
        return queryset
    
    def filter_has_schedule(self, queryset, name, value):
        """Filter reports that have or don't have linked schedules"""
        if value:
            return queryset.filter(schedule__isnull=False)
        else:
            return queryset.filter(schedule__isnull=True)
