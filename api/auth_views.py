import logging
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from django_ratelimit.exceptions import Ratelimited
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user data."""

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data to the response
        user_serializer = UserSerializer(self.user)
        data['user'] = user_serializer.data

        # Create or get user profile
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        if created:
            logger.info(f"Created new profile for user: {self.user.username}")

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff

        return token


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with enhanced error handling."""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                username = request.data.get('username', 'Unknown')
                logger.info(f"Successful login for user: {username}")

            return response

        except Ratelimited:
            logger.warning(f"Rate limit exceeded for IP: {request.META.get('REMOTE_ADDR')}")
            return Response(
                {'detail': 'Too many login attempts. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        except Exception as e:
            username = request.data.get('username', 'Unknown')
            logger.warning(f"Failed login attempt for user: {username}")

            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

from django.conf import settings

@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='post')
class DevLoginView(APIView):
    """Development login view that bypasses password check. Only available in DEBUG mode."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        if not settings.DEBUG:
            return Response(
                {'detail': 'This endpoint is not available in production.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            username = request.data.get('username')
            if not username:
                return Response({'detail': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Get user or create if strictly needed, but for now let's just get
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Optional: Auto-create user for dev convenience
                user = User.objects.create_user(username=username, password='password123')
                UserProfile.objects.create(user=user)
                logger.info(f"Created new dev user: {username}")

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Add custom claims
            access_token['username'] = user.username
            access_token['email'] = user.email
            access_token['is_staff'] = user.is_staff

            logger.info(f"Successful dev login for user: {username}")

            return Response({
                'refresh': str(refresh),
                'access': str(access_token),
                'user': UserSerializer(user).data
            })

        except Exception as e:
            logger.error(f"Dev login failed: {str(e)}")
            return Response(
                {'detail': 'Login failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class CustomTokenRefreshView(TokenRefreshView):
    """Custom JWT token refresh view with logging."""

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                logger.info("Token refreshed successfully")

            return response

        except Exception as e:
            logger.warning(f"Token refresh failed: {str(e)}")
            return Response(
                {'detail': 'Token refresh failed'},
                status=status.HTTP_401_UNAUTHORIZED
            )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@ratelimit(key='ip', rate='3/h', method='POST', block=True)
def register_user(request):
    """Register a new user account."""

    try:
        # Extract user data
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()

        # Validation
        if not username:
            raise ValidationError({'username': 'Username is required'})

        if not email:
            raise ValidationError({'email': 'Email is required'})

        if not password:
            raise ValidationError({'password': 'Password is required'})

        if len(password) < 6:
            raise ValidationError({'password': 'Password must be at least 6 characters'})

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'Email already exists'})

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create user profile
        profile = UserProfile.objects.create(user=user)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Add custom claims
        access_token['username'] = user.username
        access_token['email'] = user.email

        logger.info(f"New user registered: {username}")

        return Response({
            'message': 'User created successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)

    except Ratelimited:
        logger.warning(f"Registration rate limit exceeded for IP: {request.META.get('REMOTE_ADDR')}")
        return Response(
            {'detail': 'Too many registration attempts. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    except ValidationError as e:
        return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response(
            {'detail': 'Registration failed. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """Logout user by blacklisting the refresh token."""

    try:
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()

        logger.info(f"User logged out: {request.user.username}")

        return Response(
            {'message': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response(
            {'detail': 'Logout failed'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """Get current user's profile information."""

    try:
        user_serializer = UserSerializer(request.user)

        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile_serializer = UserProfileSerializer(profile)

        return Response({
            'user': user_serializer.data,
            'profile': profile_serializer.data
        })

    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
        return Response(
            {'detail': 'Failed to fetch profile'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """Update current user's profile information."""

    try:
        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Update profile
        profile_serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=request.method == 'PATCH'
        )

        if profile_serializer.is_valid():
            profile_serializer.save()

            # Also update user fields if provided
            user_data = {}
            for field in ['first_name', 'last_name', 'email']:
                if field in request.data:
                    user_data[field] = request.data[field]

            if user_data:
                user_serializer = UserSerializer(
                    request.user,
                    data=user_data,
                    partial=True
                )
                if user_serializer.is_valid():
                    user_serializer.save()

            logger.info(f"Profile updated for user: {request.user.username}")

            return Response({
                'user': UserSerializer(request.user).data,
                'profile': profile_serializer.data
            })

        return Response(
            profile_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return Response(
            {'detail': 'Failed to update profile'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
