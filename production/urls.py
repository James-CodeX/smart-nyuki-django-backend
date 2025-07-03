from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HarvestsViewSet, AlertsViewSet, production_stats, alert_stats

app_name = 'production'

router = DefaultRouter()
router.register(r'harvests', HarvestsViewSet, basename='harvests')
router.register(r'alerts', AlertsViewSet, basename='alerts')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', production_stats, name='production-stats'),
    path('alert-stats/', alert_stats, name='alert-stats'),
]
