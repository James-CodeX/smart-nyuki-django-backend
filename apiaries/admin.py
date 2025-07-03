from django.contrib import admin
from .models import Apiaries, Hives


@admin.register(Apiaries)
class ApiariesAdmin(admin.ModelAdmin):
    """Admin configuration for Apiaries model"""
    
    list_display = [
        'name', 'beekeeper', 'address', 'created_at'
    ]
    list_filter = [
        'created_at', 'beekeeper__experience_level'
    ]
    search_fields = [
        'name', 'address', 'description', 
        'beekeeper__user__first_name', 'beekeeper__user__last_name',
        'beekeeper__user__email'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Apiary Information', {
            'fields': ('beekeeper', 'name', 'description')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'beekeeper__user'
        ).filter(deleted_at__isnull=True)
    
    def beekeeper(self, obj):
        return f"{obj.beekeeper.user.full_name} ({obj.beekeeper.user.email})"
    beekeeper.short_description = 'Beekeeper'


@admin.register(Hives)
class HivesAdmin(admin.ModelAdmin):
    """Admin configuration for Hives model"""
    
    list_display = [
        'name', 'apiary', 'type', 'installation_date', 
        'has_smart_device', 'is_active', 'created_at'
    ]
    list_filter = [
        'type', 'has_smart_device', 'is_active', 
        'installation_date', 'created_at', 'apiary__name'
    ]
    search_fields = [
        'name', 'apiary__name', 'apiary__beekeeper__user__first_name',
        'apiary__beekeeper__user__last_name', 'apiary__address'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Hive Information', {
            'fields': ('apiary', 'name', 'type')
        }),
        ('Configuration', {
            'fields': ('installation_date', 'has_smart_device', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'apiary__beekeeper__user'
        )
    
    actions = ['mark_as_active', 'mark_as_inactive', 'add_smart_device', 'remove_smart_device']
    
    def mark_as_active(self, request, queryset):
        """Mark selected hives as active"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} hive(s) were successfully marked as active.'
        )
    mark_as_active.short_description = 'Mark selected hives as active'
    
    def mark_as_inactive(self, request, queryset):
        """Mark selected hives as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} hive(s) were successfully marked as inactive.'
        )
    mark_as_inactive.short_description = 'Mark selected hives as inactive'
    
    def add_smart_device(self, request, queryset):
        """Mark selected hives as having smart devices"""
        updated = queryset.update(has_smart_device=True)
        self.message_user(
            request,
            f'{updated} hive(s) were successfully marked as having smart devices.'
        )
    add_smart_device.short_description = 'Mark selected hives as having smart devices'
    
    def remove_smart_device(self, request, queryset):
        """Mark selected hives as not having smart devices"""
        updated = queryset.update(has_smart_device=False)
        self.message_user(
            request,
            f'{updated} hive(s) were successfully marked as not having smart devices.'
        )
    remove_smart_device.short_description = 'Mark selected hives as not having smart devices'
