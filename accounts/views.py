from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import User, BeekeeperProfile
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    BeekeeperProfileSerializer,
    BeekeeperProfileCreateSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Register a new user",
        description="Create a new user account for the Smart Nyuki application",
        responses={
            201: OpenApiResponse(
                response=UserSerializer,
                description="User created successfully"
            ),
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="User login",
        description="Authenticate user and return JWT tokens",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'format': 'email'},
                    'password': {'type': 'string'}
                },
                'required': ['email', 'password']
            }
        },
        responses={
            200: OpenApiResponse(
                description="Login successful",
                response={
                    'type': 'object',
                    'properties': {
                        'user': {'$ref': '#/components/schemas/User'},
                        'tokens': {
                            'type': 'object',
                            'properties': {
                                'refresh': {'type': 'string'},
                                'access': {'type': 'string'}
                            }
                        }
                    }
                }
            ),
            401: OpenApiResponse(description="Invalid credentials")
        }
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view and update endpoint"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Get user profile",
        description="Retrieve current user's profile information",
        responses={
            200: UserProfileSerializer
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user profile",
        description="Update current user's profile information",
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class BeekeeperProfileListCreateView(generics.ListCreateAPIView):
    """List and create beekeeper profiles"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BeekeeperProfileCreateSerializer
        return BeekeeperProfileSerializer
    
    def get_queryset(self):
        return BeekeeperProfile.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="List beekeeper profiles",
        description="Get list of beekeeper profiles for the current user",
        responses={200: BeekeeperProfileSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create beekeeper profile",
        description="Create a new beekeeper profile for the current user",
        request=BeekeeperProfileCreateSerializer,
        responses={
            201: BeekeeperProfileSerializer,
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def post(self, request, *args, **kwargs):
        # Check if user already has a beekeeper profile
        if hasattr(request.user, 'beekeeper_profile'):
            return Response(
                {'error': 'User already has a beekeeper profile'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().post(request, *args, **kwargs)


class BeekeeperProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete beekeeper profile"""
    
    serializer_class = BeekeeperProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BeekeeperProfile.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="Get beekeeper profile",
        description="Retrieve a specific beekeeper profile",
        responses={200: BeekeeperProfileSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update beekeeper profile",
        description="Update a specific beekeeper profile",
        responses={
            200: BeekeeperProfileSerializer,
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete beekeeper profile",
        description="Delete a specific beekeeper profile",
        responses={204: OpenApiResponse(description="Profile deleted successfully")}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """Change user password endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Change password",
        description="Change current user's password",
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response(
                {'message': 'Password changed successfully'}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Logout user",
    description="Logout current user by blacklisting refresh token",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string'}
            },
            'required': ['refresh']
        }
    },
    responses={
        200: OpenApiResponse(description="Logout successful"),
        400: OpenApiResponse(description="Invalid token")
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user by blacklisting refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response(
            {'message': 'Logout successful'}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': 'Invalid token'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
