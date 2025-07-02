from django.urls import path
from . import views

app_name = 'devices'

urlpatterns = [
    # Smart Devices URLs
    path('devices/', views.SmartDevicesListCreateView.as_view(), name='device-list-create'),
    path('devices/<uuid:pk>/', views.SmartDevicesDetailView.as_view(), name='device-detail'),
    path('devices/<uuid:device_id>/stats/', views.device_stats, name='device-stats'),
    
    # Sensor Readings URLs
    path('sensor-readings/', views.SensorReadingsListCreateView.as_view(), name='sensor-reading-list-create'),
    path('sensor-readings/<uuid:pk>/', views.SensorReadingsDetailView.as_view(), name='sensor-reading-detail'),
    
    # Audio Recordings URLs
    path('audio-recordings/', views.AudioRecordingsListCreateView.as_view(), name='audio-recording-list-create'),
    path('audio-recordings/<uuid:pk>/', views.AudioRecordingsDetailView.as_view(), name='audio-recording-detail'),
    
    # Device Images URLs
    path('device-images/', views.DeviceImagesListCreateView.as_view(), name='device-image-list-create'),
    path('device-images/<uuid:pk>/', views.DeviceImagesDetailView.as_view(), name='device-image-detail'),
]
