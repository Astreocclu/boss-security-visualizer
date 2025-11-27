from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from PIL import Image
import io
from .models import VisualizationRequest, GeneratedImage, ScreenType, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information."""

    full_name = serializers.ReadOnlyField()
    total_requests = serializers.SerializerMethodField()
    completed_requests = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'company_name', 'phone_number', 'full_name',
            'total_requests', 'completed_requests', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_total_requests(self, obj):
        """Get total number of requests for this user."""
        return obj.get_total_requests()

    def get_completed_requests(self, obj):
        """Get number of completed requests for this user."""
        return obj.get_completed_requests()

    def validate_phone_number(self, value):
        """Validate phone number format."""
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValidationError("Please enter a valid phone number.")
        return value


class UserSerializer(serializers.ModelSerializer):
    """Enhanced user serializer with profile information."""

    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'profile', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    def get_full_name(self, obj):
        """Get user's full name."""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username


class ScreenTypeSerializer(serializers.ModelSerializer):
    """Enhanced serializer for screen types."""

    request_count = serializers.SerializerMethodField()

    class Meta:
        model = ScreenType
        fields = [
            'id', 'name', 'description', 'is_active', 'sort_order',
            'request_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'request_count']

    def get_request_count(self, obj):
        """Get number of requests using this screen type."""
        return obj.get_request_count()

    def validate_name(self, value):
        """Validate screen type name."""
        if not value or not value.strip():
            raise ValidationError("Screen type name cannot be empty.")

        # Check for uniqueness (case-insensitive)
        existing = ScreenType.objects.filter(name__iexact=value.strip())
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise ValidationError("A screen type with this name already exists.")

        return value.strip().title()


class GeneratedImageSerializer(serializers.ModelSerializer):
    """Enhanced serializer for generated images."""

    generated_image_url = serializers.SerializerMethodField()
    file_size_mb = serializers.ReadOnlyField()
    dimensions = serializers.ReadOnlyField()

    class Meta:
        model = GeneratedImage
        fields = [
            'id', 'generated_image_url', 'file_size', 'file_size_mb',
            'image_width', 'image_height', 'dimensions', 'metadata', 'generated_at'
        ]
        read_only_fields = fields

    def get_generated_image_url(self, obj):
        """Get absolute URL for the generated image."""
        if obj.generated_image:
            request = self.context.get('request')
            url = obj.generated_image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class VisualizationRequestListSerializer(serializers.ModelSerializer):
    """Optimized serializer for listing requests with minimal data."""

    screen_type_name = serializers.CharField(
        source='screen_type.name',
        read_only=True,
        allow_null=True
    )
    original_image_url = serializers.ImageField(source='original_image', read_only=True)
    result_count = serializers.SerializerMethodField()
    processing_duration = serializers.SerializerMethodField()
    latest_result_url = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = VisualizationRequest
        fields = [
            'id', 'user_name', 'original_image_url', 'screen_type_name',
            'status', 'created_at', 'updated_at', 'result_count',
            'processing_duration', 'error_message', 'progress_percentage', 'status_message',
            'latest_result_url'
        ]
        read_only_fields = fields

    def get_result_count(self, obj):
        """Get number of generated results."""
        return obj.get_result_count()

    def get_processing_duration(self, obj):
        """Get processing duration in seconds."""
        duration = obj.processing_duration
        if duration:
            return duration.total_seconds()
        return None

    def get_latest_result_url(self, obj):
        """Get absolute URL of the latest generated image."""
        latest_result = obj.results.first()
        if latest_result and latest_result.generated_image:
            request = self.context.get('request')
            url = latest_result.generated_image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class VisualizationRequestDetailSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for creating and viewing request details."""

    # Read-only fields for response
    screen_type_details = ScreenTypeSerializer(source='screen_type', read_only=True)
    results = GeneratedImageSerializer(many=True, read_only=True)
    original_image_url = serializers.ImageField(source='original_image', read_only=True)
    clean_image_url = serializers.ImageField(source='clean_image', read_only=True)
    user = UserSerializer(read_only=True)
    processing_duration = serializers.SerializerMethodField()

    # Write-only fields for creation/update
    screen_type = serializers.PrimaryKeyRelatedField(
        queryset=ScreenType.objects.filter(is_active=True),
        write_only=True,
        allow_null=True,
        required=False,
        help_text="ID of the screen type to apply"
    )

    class Meta:
        model = VisualizationRequest
        fields = [
            # Read-only response fields
            'id', 'user', 'original_image_url', 'clean_image_url', 'screen_type_details',
            'status', 'created_at', 'updated_at', 'task_id', 'results',
            'processing_started_at', 'processing_completed_at', 'processing_duration',
            'error_message', 'progress_percentage', 'status_message',
            # Write-only fields for creation
            'original_image', 'screen_type', 'opacity', 'color'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'created_at', 'updated_at', 'task_id',
            'results', 'original_image_url', 'clean_image_url', 'screen_type_details',
            'processing_started_at', 'processing_completed_at', 'error_message',
            'progress_percentage', 'status_message'
        ]
        extra_kwargs = {
            'original_image': {
                'write_only': True,
                'required': True,
                'help_text': 'Image file to process (JPEG, PNG, WebP supported)'
            }
        }

    def get_processing_duration(self, obj):
        """Get processing duration in seconds."""
        duration = obj.processing_duration
        if duration:
            return duration.total_seconds()
        return None

    def validate_original_image(self, value):
        """Validate uploaded image file."""
        if not value:
            raise ValidationError("Image file is required.")

        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if hasattr(value, 'content_type') and value.content_type not in allowed_types:
            raise ValidationError(
                f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
            )

        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise ValidationError(
                f"File size too large. Maximum size is {max_size / (1024 * 1024):.1f}MB"
            )

        # Validate image dimensions and format
        try:
            # For InMemoryUploadedFile, we need to read the content
            if isinstance(value, (InMemoryUploadedFile, TemporaryUploadedFile)):
                image = Image.open(value)

                # Check dimensions
                max_width, max_height = 8192, 8192
                if image.width > max_width or image.height > max_height:
                    raise ValidationError(
                        f"Image dimensions too large. Maximum: {max_width}x{max_height}px. "
                        f"Current: {image.width}x{image.height}px"
                    )

                # Reset file pointer for later use
                value.seek(0)

        except Exception as e:
            raise ValidationError(f"Invalid image file: {str(e)}")

        return value

    def validate_screen_type(self, value):
        """Validate screen type selection."""
        if value and not value.is_active:
            raise ValidationError("Selected screen type is not available.")
        return value

    def validate(self, attrs):
        """Perform cross-field validation."""
        # Add any cross-field validation logic here
        return attrs

    def create(self, validated_data):
        """Create a new visualization request."""
        # The user will be set in the view's perform_create method
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update an existing visualization request."""
        # Only allow updating certain fields
        allowed_fields = ['screen_type']

        # Filter out fields that shouldn't be updated
        for field in list(validated_data.keys()):
            if field not in allowed_fields:
                validated_data.pop(field)

        return super().update(instance, validated_data)


class VisualizationRequestCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating requests."""

    class Meta:
        model = VisualizationRequest
        fields = ['id', 'original_image', 'screen_type', 'opacity', 'color', 'status', 'progress_percentage', 'status_message', 'created_at']
        read_only_fields = ['id', 'status', 'progress_percentage', 'status_message', 'created_at']
        extra_kwargs = {
            'original_image': {'required': True},
            'screen_type': {'required': False, 'allow_null': True}
        }

    def validate_original_image(self, value):
        """Validate uploaded image file."""
        # Reuse validation from detail serializer
        detail_serializer = VisualizationRequestDetailSerializer()
        return detail_serializer.validate_original_image(value)

    def validate_screen_type(self, value):
        """Validate screen type selection."""
        if value and not value.is_active:
            raise ValidationError("Selected screen type is not available.")
        return value
