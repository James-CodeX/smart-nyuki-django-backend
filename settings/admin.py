from django.contrib import admin
from .models import (
    UserSettings, 
    AlertThresholds, 
    NotificationSettings, 
    DataSyncSettings, 
    PrivacySettings
)


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'timezone', 'language', 'temperature_unit', 'weight_unit', 'date_format', 'updated_at']
    list_filter = ['timezone', 'language', 'temperature_unit', 'weight_unit', 'date_format']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(AlertThresholds)
class AlertThresholdsAdmin(admin.ModelAdmin):
    list_display = ['user', 'hive', 'is_global', 'temperature_min', 'temperature_max', 'humidity_min', 'humidity_max', 'updated_at']
    list_filter = ['temperature_min', 'temperature_max', 'humidity_min', 'humidity_max']
    search_fields = ['user__email', 'hive__name', 'hive__apiary__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'hive__apiary')
    
    def is_global(self, obj):
        return obj.hive is None
    is_global.boolean = True
    is_global.short_description = 'Global Setting'


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'push_notifications', 'email_notifications', 'sms_notifications', 'daily_summary_enabled', 'updated_at']
    list_filter = ['push_notifications', 'email_notifications', 'sms_notifications', 'daily_summary_enabled']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(DataSyncSettings)
class DataSyncSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'auto_sync_enabled', 'sync_frequency', 'backup_enabled', 'backup_frequency', 'data_retention_days', 'updated_at']
    list_filter = ['auto_sync_enabled', 'sync_frequency', 'backup_enabled', 'backup_frequency', 'wifi_only_sync']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PrivacySettings)
class PrivacySettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_visibility', 'location_sharing', 'analytics_enabled', 'crash_reporting', 'data_sharing_research', 'updated_at']
    list_filter = ['profile_visibility', 'location_sharing', 'analytics_enabled', 'crash_reporting', 'data_sharing_research']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
