from django.contrib import admin
from .models import Harvests, Alerts


@admin.register(Harvests)
class HarvestsAdmin(admin.ModelAdmin):
    """Admin configuration for Harvests model"""
    
    list_display = [
        'hive', 'harvest_date', 'honey_kg', 'wax_kg', 'pollen_kg', 
        'harvested_by', 'total_weight_kg', 'created_at'
    ]
    list_filter = [
        'harvest_date', 'harvested_by', 'hive__apiary', 
        'processing_method', 'created_at'
    ]
    search_fields = [
        'hive__name', 'hive__apiary__name', 'harvested_by__email',
        'harvested_by__first_name', 'harvested_by__last_name',
        'processing_method', 'quality_notes'
    ]
    ordering = ['-harvest_date', '-created_at']
    date_hierarchy = 'harvest_date'
    
    fieldsets = (
        ('Harvest Information', {
            'fields': ('hive', 'harvest_date', 'harvested_by')
        }),
        ('Quantities', {
            'fields': ('honey_kg', 'wax_kg', 'pollen_kg')
        }),
        ('Details', {
            'fields': ('processing_method', 'quality_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    readonly_fields = ['created_at', 'total_weight_kg']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'hive__apiary__beekeeper__user',
            'harvested_by'
        )
    
    def total_weight_kg(self, obj):
        return obj.total_weight_kg
    total_weight_kg.short_description = 'Total Weight (kg)'


@admin.register(Alerts)
class AlertsAdmin(admin.ModelAdmin):
    """Admin configuration for Alerts model"""
    
    list_display = [
        'hive', 'alert_type', 'severity', 'is_resolved', 
        'created_at', 'resolved_at', 'resolved_by'
    ]
    list_filter = [
        'alert_type', 'severity', 'is_resolved', 'created_at',
        'resolved_at', 'hive__apiary'
    ]
    search_fields = [
        'hive__name', 'hive__apiary__name', 'message',
        'resolution_notes', 'resolved_by__email',
        'resolved_by__first_name', 'resolved_by__last_name'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('hive', 'alert_type', 'severity', 'message')
        }),
        ('Trigger Data', {
            'fields': ('trigger_values',),
            'classes': ('collapse',)
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_at', 'resolved_by', 'resolution_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'hive__apiary__beekeeper__user',
            'resolved_by'
        )
    
    actions = ['mark_as_resolved', 'mark_as_unresolved']
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected alerts as resolved"""
        from django.utils import timezone
        updated = queryset.update(
            is_resolved=True,
            resolved_at=timezone.now(),
            resolved_by=request.user
        )
        self.message_user(
            request,
            f'{updated} alert(s) were successfully marked as resolved.'
        )
    mark_as_resolved.short_description = 'Mark selected alerts as resolved'
    
    def mark_as_unresolved(self, request, queryset):
        """Mark selected alerts as unresolved"""
        updated = queryset.update(
            is_resolved=False,
            resolved_at=None,
            resolved_by=None,
            resolution_notes=''
        )
        self.message_user(
            request,
            f'{updated} alert(s) were successfully marked as unresolved.'
        )
    mark_as_unresolved.short_description = 'Mark selected alerts as unresolved'
