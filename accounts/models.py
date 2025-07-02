import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """Custom manager for User model"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password"""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model for Smart Nyuki application"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=20, 
        blank=True, 
        null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Override username field to use email
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class BeekeeperProfile(models.Model):
    """Extended profile information for beekeepers"""
    
    EXPERIENCE_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='beekeeper_profile'
    )
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=11, 
        decimal_places=8, 
        help_text="Longitude coordinate"
    )
    address = models.TextField(blank=True, null=True)
    experience_level = models.CharField(
        max_length=20, 
        choices=EXPERIENCE_CHOICES,
        default='Beginner'
    )
    established_date = models.DateField(
        help_text="Date when beekeeping operation was established"
    )
    app_start_date = models.DateField(
        auto_now_add=True,
        help_text="Date when user started using the app"
    )
    certification_details = models.TextField(
        blank=True, 
        null=True,
        help_text="Details about beekeeping certifications"
    )
    profile_picture_url = models.URLField(
        max_length=500, 
        blank=True, 
        null=True
    )
    notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional notes about the beekeeper"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'beekeeper_profiles'
        verbose_name = 'Beekeeper Profile'
        verbose_name_plural = 'Beekeeper Profiles'
    
    def __str__(self):
        return f"{self.user.full_name} - {self.experience_level}"
    
    @property
    def coordinates(self):
        return (float(self.latitude), float(self.longitude))
