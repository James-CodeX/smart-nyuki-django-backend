from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, BeekeeperProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone_number', 
            'password', 'password_confirm'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile information"""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']


class BeekeeperProfileSerializer(serializers.ModelSerializer):
    """Serializer for beekeeper profile information"""
    
    user = UserSerializer(read_only=True)
    coordinates = serializers.ReadOnlyField()
    
    class Meta:
        model = BeekeeperProfile
        fields = [
            'id', 'user', 'latitude', 'longitude', 'coordinates',
            'address', 'experience_level', 'established_date',
            'app_start_date', 'certification_details', 'profile_picture_url',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'app_start_date', 'created_at', 'updated_at']


class BeekeeperProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating beekeeper profile"""
    
    class Meta:
        model = BeekeeperProfile
        fields = [
            'latitude', 'longitude', 'address', 'experience_level',
            'established_date', 'certification_details', 'profile_picture_url',
            'notes'
        ]
    
    def create(self, validated_data):
        # Get the user from the request context
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password": "New password fields didn't match."}
            )
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """Complete user profile serializer including beekeeper profile"""
    
    beekeeper_profile = BeekeeperProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'is_active', 'created_at', 'updated_at',
            'beekeeper_profile'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']
