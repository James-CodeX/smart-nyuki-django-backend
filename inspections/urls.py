from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InspectionSchedulesViewSet, InspectionReportsViewSet

router = DefaultRouter()
router.register(r'schedules', InspectionSchedulesViewSet, basename='inspection-schedules')
router.register(r'reports', InspectionReportsViewSet, basename='inspection-reports')

app_name = 'inspections'

urlpatterns = [
    path('', include(router.urls)),
]
