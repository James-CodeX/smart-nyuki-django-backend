from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Beekeeper profile endpoints
    path('beekeeper-profiles/', views.BeekeeperProfileListCreateView.as_view(), name='beekeeper_profile_list'),
    path('beekeeper-profiles/<uuid:pk>/', views.BeekeeperProfileDetailView.as_view(), name='beekeeper_profile_detail'),
]
