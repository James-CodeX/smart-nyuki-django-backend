from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, BeekeeperProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model"""
    
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_staff', 'created_at']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at', 'deleted_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BeekeeperProfile)
class BeekeeperProfileAdmin(admin.ModelAdmin):
    """Admin configuration for BeekeeperProfile model"""
    
    list_display = ['user', 'experience_level', 'established_date', 'app_start_date', 'created_at']
    list_filter = ['experience_level', 'established_date', 'app_start_date', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'address']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Location', {'fields': ('latitude', 'longitude', 'address')}),
        ('Beekeeping Details', {
            'fields': ('experience_level', 'established_date', 'certification_details')
        }),
        ('Profile', {'fields': ('profile_picture_url', 'notes')}),
        ('Timestamps', {'fields': ('app_start_date', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ['app_start_date', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
