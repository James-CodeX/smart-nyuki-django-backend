from rest_framework import serializers
from django.utils import timezone
from datetime import date
from .models import InspectionSchedules, InspectionReports
from apiaries.serializers import HivesDetailSerializer
from accounts.serializers import UserSerializer


class InspectionSchedulesReadSerializer(serializers.ModelSerializer):
    """Serializer for reading inspection schedules"""
    hive = HivesDetailSerializer(read_only=True)
    
    class Meta:
        model = InspectionSchedules
        fields = [
            'id', 'hive', 'scheduled_date', 'notes', 'is_completed',
            'weather_conditions', 'created_at', 'updated_at'
        ]


class InspectionSchedulesWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating inspection schedules"""
    
    class Meta:
        model = InspectionSchedules
        fields = [
            'hive', 'scheduled_date', 'notes', 'weather_conditions'
        ]
    
    def validate_scheduled_date(self, value):
        """Validate that scheduled date is not in the past"""
        if value < date.today():
            raise serializers.ValidationError(
                "Scheduled date cannot be in the past."
            )
        return value
    
    def validate_hive(self, value):
        """Validate that user has access to the hive"""
        user = self.context['request'].user
        
        # Check if user has beekeeper profile
        if not hasattr(user, 'beekeeper_profile'):
            raise serializers.ValidationError(
                "You must have a beekeeper profile to schedule inspections."
            )
        
        # Check if hive belongs to user's apiaries
        user_apiaries = user.beekeeper_profile.apiaries.all()
        if value.apiary not in user_apiaries:
            raise serializers.ValidationError(
                "You can only schedule inspections for your own hives."
            )
        
        return value


class InspectionReportsReadSerializer(serializers.ModelSerializer):
    """Serializer for reading inspection reports"""
    schedule = InspectionSchedulesReadSerializer(read_only=True)
    hive = HivesDetailSerializer(read_only=True)
    inspector = UserSerializer(read_only=True)
    honey_level_display = serializers.CharField(source='get_honey_level_display', read_only=True)
    colony_health_display = serializers.CharField(source='get_colony_health_display', read_only=True)
    brood_pattern_display = serializers.CharField(source='get_brood_pattern_display', read_only=True)
    
    class Meta:
        model = InspectionReports
        fields = [
            'id', 'schedule', 'hive', 'inspector', 'inspection_date',
            'queen_present', 'honey_level', 'honey_level_display',
            'colony_health', 'colony_health_display', 'varroa_mite_count',
            'brood_pattern', 'brood_pattern_display', 'pest_observations',
            'actions_taken', 'notes', 'created_at'
        ]


class InspectionReportsWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating inspection reports"""
    
    class Meta:
        model = InspectionReports
        fields = [
            'schedule', 'hive', 'inspection_date', 'queen_present',
            'honey_level', 'colony_health', 'varroa_mite_count',
            'brood_pattern', 'pest_observations', 'actions_taken', 'notes'
        ]
    
    def validate_inspection_date(self, value):
        """Validate that inspection date is not in the future"""
        if value > date.today():
            raise serializers.ValidationError(
                "Inspection date cannot be in the future."
            )
        return value
    
    def validate_hive(self, value):
        """Validate that user has access to the hive"""
        user = self.context['request'].user
        
        # Check if user has beekeeper profile
        if not hasattr(user, 'beekeeper_profile'):
            raise serializers.ValidationError(
                "You must have a beekeeper profile to create inspection reports."
            )
        
        # Check if hive belongs to user's apiaries
        user_apiaries = user.beekeeper_profile.apiaries.all()
        if value.apiary not in user_apiaries:
            raise serializers.ValidationError(
                "You can only create inspection reports for your own hives."
            )
        
        return value
    
    def validate_schedule(self, value):
        """Validate schedule if provided"""
        if value:
            user = self.context['request'].user
            
            # Check if user has beekeeper profile
            if not hasattr(user, 'beekeeper_profile'):
                raise serializers.ValidationError(
                    "You must have a beekeeper profile to link to schedules."
                )
            
            # Check if schedule belongs to user's hives
            user_apiaries = user.beekeeper_profile.apiaries.all()
            if value.hive.apiary not in user_apiaries:
                raise serializers.ValidationError(
                    "You can only link to schedules for your own hives."
                )
        
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        schedule = attrs.get('schedule')
        hive = attrs.get('hive')
        
        # If schedule is provided, ensure it matches the hive
        if schedule and hive and schedule.hive != hive:
            raise serializers.ValidationError(
                "The selected schedule must be for the same hive as the report."
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create inspection report and mark schedule as completed if linked"""
        # Set inspector to current user
        validated_data['inspector'] = self.context['request'].user
        
        report = super().create(validated_data)
        
        # Mark associated schedule as completed if it exists
        if report.schedule:
            report.schedule.is_completed = True
            report.schedule.save()
        
        return report


class InspectionScheduleCompletionSerializer(serializers.Serializer):
    """Serializer for marking inspection schedules as completed"""
    is_completed = serializers.BooleanField()
    notes = serializers.CharField(required=False, allow_blank=True)


class InspectionStatisticsSerializer(serializers.Serializer):
    """Serializer for inspection statistics"""
    total_schedules = serializers.IntegerField()
    completed_schedules = serializers.IntegerField()
    pending_schedules = serializers.IntegerField()
    overdue_schedules = serializers.IntegerField()
    total_reports = serializers.IntegerField()
    reports_this_month = serializers.IntegerField()
    average_colony_health = serializers.CharField()
    queen_presence_rate = serializers.FloatField()
