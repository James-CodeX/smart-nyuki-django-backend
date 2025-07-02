from django.contrib import admin
from .models import SmartDevices, SensorReadings, AudioRecordings, DeviceImages


@admin.register(SmartDevices)
class SmartDevicesAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'device_type', 'beekeeper_name', 'hive', 'battery_level', 'is_active', 'last_sync_at', 'created_at']
    list_filter = ['device_type', 'is_active', 'created_at', 'beekeeper']
    search_fields = ['serial_number', 'device_type', 'beekeeper__user__first_name', 'beekeeper__user__last_name', 'hive__name']
    readonly_fields = ['id', 'created_at']
    list_per_page = 25
    ordering = ['-created_at']
    
    def beekeeper_name(self, obj):
        """Display beekeeper's full name"""
        return obj.beekeeper.user.get_full_name() if obj.beekeeper else 'N/A'
    beekeeper_name.short_description = 'Beekeeper'
    
    fieldsets = (
        ('Ownership', {
            'fields': ('beekeeper',)
        }),
        ('Device Information', {
            'fields': ('serial_number', 'device_type', 'hive')
        }),
        ('Status', {
            'fields': ('is_active', 'battery_level', 'last_sync_at')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(SensorReadings)
class SensorReadingsAdmin(admin.ModelAdmin):
    list_display = ['device', 'timestamp', 'temperature', 'humidity', 'weight', 'battery_level', 'created_at']
    list_filter = ['timestamp', 'created_at', 'device__device_type']
    search_fields = ['device__serial_number']
    readonly_fields = ['id', 'created_at']
    list_per_page = 50
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Reading Information', {
            'fields': ('device', 'timestamp')
        }),
        ('Sensor Data', {
            'fields': ('temperature', 'humidity', 'weight', 'sound_level')
        }),
        ('Device Status', {
            'fields': ('battery_level', 'status_code')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(AudioRecordings)
class AudioRecordingsAdmin(admin.ModelAdmin):
    list_display = ['device', 'recorded_at', 'duration', 'file_size', 'upload_status', 'analysis_status', 'is_analyzed']
    list_filter = ['upload_status', 'analysis_status', 'is_analyzed', 'recorded_at', 'created_at']
    search_fields = ['device__serial_number', 'file_path']
    readonly_fields = ['id', 'created_at']
    list_per_page = 25
    ordering = ['-recorded_at']
    
    fieldsets = (
        ('Recording Information', {
            'fields': ('device', 'file_path', 'recorded_at')
        }),
        ('File Details', {
            'fields': ('duration', 'file_size')
        }),
        ('Status', {
            'fields': ('upload_status', 'analysis_status', 'is_analyzed')
        }),
        ('Analysis', {
            'fields': ('analysis_results',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(DeviceImages)
class DeviceImagesAdmin(admin.ModelAdmin):
    list_display = ['device', 'captured_at', 'image_type', 'upload_status', 'analysis_status', 'is_analyzed']
    list_filter = ['image_type', 'upload_status', 'analysis_status', 'is_analyzed', 'captured_at', 'created_at']
    search_fields = ['device__serial_number', 'file_path']
    readonly_fields = ['id', 'created_at']
    list_per_page = 25
    ordering = ['-captured_at']
    
    fieldsets = (
        ('Image Information', {
            'fields': ('device', 'file_path', 'captured_at', 'image_type')
        }),
        ('Status', {
            'fields': ('upload_status', 'analysis_status', 'is_analyzed')
        }),
        ('Analysis', {
            'fields': ('analysis_results',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
