from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'user-settings', views.UserSettingsViewSet, basename='user-settings')
router.register(r'alert-thresholds', views.AlertThresholdsViewSet, basename='alert-thresholds')
router.register(r'notification-settings', views.NotificationSettingsViewSet, basename='notification-settings')
router.register(r'data-sync-settings', views.DataSyncSettingsViewSet, basename='data-sync-settings')
router.register(r'privacy-settings', views.PrivacySettingsViewSet, basename='privacy-settings')

urlpatterns = [
    path('', include(router.urls)),
]
