from django.contrib import admin
from .models import InspectionSchedules, InspectionReports


@admin.register(InspectionSchedules)
class InspectionSchedulesAdmin(admin.ModelAdmin):
    """Admin interface for inspection schedules"""
    
    list_display = [
        'id', 'hive', 'scheduled_date', 'is_completed', 
        'weather_conditions', 'created_at'
    ]
    list_filter = [
        'is_completed', 'scheduled_date', 'created_at',
        'hive__apiary__name', 'weather_conditions'
    ]
    search_fields = [
        'hive__name', 'hive__apiary__name', 'notes',
        'hive__apiary__beekeeper__user__first_name',
        'hive__apiary__beekeeper__user__last_name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Schedule Information', {
            'fields': ('hive', 'scheduled_date', 'is_completed')
        }),
        ('Details', {
            'fields': ('notes', 'weather_conditions')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'hive', 'hive__apiary', 'hive__apiary__beekeeper__user'
        )


@admin.register(InspectionReports)
class InspectionReportsAdmin(admin.ModelAdmin):
    """Admin interface for inspection reports"""
    
    list_display = [
        'id', 'hive', 'inspector', 'inspection_date',
        'colony_health', 'honey_level', 'queen_present', 'created_at'
    ]
    list_filter = [
        'inspection_date', 'colony_health', 'honey_level',
        'brood_pattern', 'queen_present', 'created_at',
        'hive__apiary__name'
    ]
    search_fields = [
        'hive__name', 'hive__apiary__name', 'notes',
        'inspector__first_name', 'inspector__last_name',
        'pest_observations', 'actions_taken'
    ]
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('schedule', 'hive', 'inspector', 'inspection_date')
        }),
        ('Assessment', {
            'fields': (
                'queen_present', 'honey_level', 'colony_health',
                'brood_pattern', 'varroa_mite_count'
            )
        }),
        ('Observations & Actions', {
            'fields': ('pest_observations', 'actions_taken', 'notes')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'schedule', 'hive', 'hive__apiary', 
            'hive__apiary__beekeeper__user', 'inspector'
        )
