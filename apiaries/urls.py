from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApiariesViewSet, HivesViewSet

app_name = 'apiaries'

router = DefaultRouter()
router.register(r'apiaries', ApiariesViewSet, basename='apiaries')
router.register(r'hives', HivesViewSet, basename='hives')

urlpatterns = [
    path('', include(router.urls)),
]
