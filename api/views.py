import logging
import time
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import VisualizationRequest, ScreenType, GeneratedImage, UserProfile
from .serializers import (
    VisualizationRequestListSerializer,
    VisualizationRequestDetailSerializer,
    VisualizationRequestCreateSerializer,
    ScreenTypeSerializer,
    GeneratedImageSerializer,
    UserProfileSerializer
)
# from .tasks import process_image_request # Import later if using Celery

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class for API responses."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class ScreenTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing screen types.
    Supports filtering, searching, and caching.
    """
    serializer_class = ScreenTypeSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']

    def get_queryset(self):
        """Return active screen types by default."""
        queryset = ScreenType.objects.all()

        # Filter by active status if not explicitly requested
        if not self.request.query_params.get('is_active'):
            queryset = queryset.filter(is_active=True)

        return queryset

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        """List screen types with caching."""
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active screen types."""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class VisualizationRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing visualization requests.
    Supports filtering, searching, pagination, and optimized queries.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'screen_type']
    search_fields = ['screen_type__name']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return visualization requests for the authenticated user with optimized queries.
        """
        user = self.request.user
        queryset = VisualizationRequest.objects.filter(user=user)

        # Optimize queries based on action
        if self.action == 'list':
            queryset = queryset.select_related('screen_type', 'user').prefetch_related('results')
        elif self.action in ['retrieve', 'update', 'partial_update']:
            queryset = queryset.select_related('screen_type', 'user').prefetch_related('results')

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return VisualizationRequestListSerializer
        elif self.action == 'create':
            return VisualizationRequestCreateSerializer
        return VisualizationRequestDetailSerializer

    def get_object(self):
        """Get object with permission check."""
        obj = super().get_object()

        # Ensure user can only access their own requests
        if obj.user != self.request.user:
            raise PermissionDenied("You can only access your own requests.")

        return obj

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Override create to log validation errors."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Create a new visualization request with proper error handling.
        """
        try:
            # Save the instance with the current user
            instance = serializer.save(user=self.request.user, status='pending')

            logger.info(f"VisualizationRequest created: ID={instance.id}, User={self.request.user.username}")

            # Trigger AI processing
            self._trigger_ai_processing(instance)

        except Exception as e:
            logger.error(f"Error creating visualization request: {str(e)}")
            raise ValidationError("Failed to create visualization request. Please try again.")

    def perform_update(self, serializer):
        """Update request with validation."""
        instance = serializer.instance

        # Only allow updates to pending requests
        if instance.status not in ['pending', 'failed']:
            raise ValidationError("Cannot update requests that are processing or completed.")

        serializer.save()
        logger.info(f"VisualizationRequest updated: ID={instance.id}")

    def perform_destroy(self, instance):
        """Delete request with proper cleanup."""
        # Only allow deletion of pending or failed requests
        if instance.status in ['processing']:
            raise ValidationError("Cannot delete requests that are currently processing.")

        logger.info(f"VisualizationRequest deleted: ID={instance.id}")
        super().perform_destroy(instance)

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed visualization request."""
        instance = self.get_object()

        if instance.status != 'failed':
            return Response(
                {'error': 'Only failed requests can be retried.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reset status and clear error message
        instance.status = 'pending'
        instance.error_message = ''
        instance.save()

        # TODO: Trigger AI processing
        # self._trigger_ai_processing(instance)

        logger.info(f"VisualizationRequest retry: ID={instance.id}")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate a visualization request."""
        instance = self.get_object()

        # Reset status and clear error message
        instance.status = 'pending'
        instance.error_message = ''
        instance.progress_percentage = 0
        instance.status_message = "Queued for regeneration..."
        instance.save()

        # Trigger AI processing
        self._trigger_ai_processing(instance)

        logger.info(f"VisualizationRequest regenerate: ID={instance.id}")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user's request statistics."""
        user = request.user
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'processing': queryset.filter(status='processing').count(),
            'completed': queryset.filter(status='complete').count(),
            'failed': queryset.filter(status='failed').count(),
        }

        return Response(stats)

    def _trigger_ai_processing(self, instance):
        """
        Trigger AI-enhanced processing for the visualization request.
        """
        from .ai_enhanced_processor import AIEnhancedImageProcessor
        import threading

        def process_in_background():
            """Process the image in a background thread using AI services."""
            try:
                # Use AI-enhanced processor (Gemini)
                processor = AIEnhancedImageProcessor()
                generated_images = processor.process_image(instance)
                logger.info(f"Successfully processed request {instance.id} with AI enhancement, generated {len(generated_images)} images")
            except Exception as e:
                logger.error(f"Error in AI processing for request {instance.id}: {str(e)}")
                instance.mark_as_failed(str(e))

        # Start processing in background thread
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()

        logger.info(f"AI-enhanced processing started for request {instance.id}")


class GeneratedImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing generated images.
    Users can only view images from their own requests.
    """
    serializer_class = GeneratedImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['request']
    ordering_fields = ['generated_at']
    ordering = ['-generated_at']

    def get_queryset(self):
        """Return generated images for the authenticated user's requests."""
        user = self.request.user
        return GeneratedImage.objects.filter(
            request__user=user
        ).select_related('request', 'request__user', 'request__screen_type')

    def get_object(self):
        """Get object with permission check."""
        obj = super().get_object()

        # Ensure user can only access images from their own requests
        if obj.request.user != self.request.user:
            raise PermissionDenied("You can only access images from your own requests.")

        return obj


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user profiles.
    Users can only view and edit their own profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's profile."""
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create the user's profile."""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def list(self, request, *args, **kwargs):
        """Return the user's profile as a single object."""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Profiles are created automatically, so redirect to update."""
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """Update the user's profile."""
        serializer.save(user=self.request.user)
        logger.info(f"UserProfile updated: User={self.request.user.username}")


class AIServiceViewSet(viewsets.ViewSet):
    """
    API endpoint for managing AI services and providers.
    Provides information about available AI services and their status.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get overall AI services status."""
        try:
            from .ai_services import ai_service_registry, AIServiceFactory

            status_info = {
                'registry_status': ai_service_registry.get_registry_status(),
                'factory_status': AIServiceFactory.get_factory_status(),
                'timestamp': time.time()
            }

            return Response(status_info)

        except Exception as e:
            logger.error(f"Error getting AI services status: {str(e)}")
            return Response(
                {'error': 'Failed to get AI services status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def providers(self, request):
        """Get information about available AI providers."""
        try:
            from .ai_services import ai_service_registry

            providers_info = {}
            all_providers = ai_service_registry.get_all_providers()

            for provider_name, provider in all_providers.items():
                providers_info[provider_name] = ai_service_registry.get_provider_capabilities(provider_name)

            return Response(providers_info)

        except Exception as e:
            logger.error(f"Error getting AI providers info: {str(e)}")
            return Response(
                {'error': 'Failed to get AI providers information'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def health(self, request):
        """Get health status of AI services."""
        try:
            from .ai_services import ai_service_registry

            health_info = {}
            all_providers = ai_service_registry.get_all_providers()

            for provider_name, provider in all_providers.items():
                if hasattr(provider, 'get_service_health'):
                    health_info[provider_name] = provider.get_service_health()
                else:
                    health_info[provider_name] = {'status': 'unknown'}

            return Response(health_info)

        except Exception as e:
            logger.error(f"Error getting AI services health: {str(e)}")
            return Response(
                {'error': 'Failed to get AI services health'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# TODO: Add authentication views using dj-rest-auth or custom implementation