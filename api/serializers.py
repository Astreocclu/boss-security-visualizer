from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from PIL import Image
import io
from .models import VisualizationRequest, GeneratedImage, UserProfile
from api.tenants import get_tenant_config


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

    screen_type_display = serializers.CharField(
        source='get_screen_type_display',
        read_only=True
    )
    original_image_url = serializers.ImageField(source='original_image', read_only=True)
    result_count = serializers.SerializerMethodField()
    processing_duration = serializers.SerializerMethodField()
    latest_result_url = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = VisualizationRequest
        fields = [
            'id', 'user_name', 'original_image_url', 'screen_type', 'screen_type_display',
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
    screen_type_display = serializers.CharField(source='get_screen_type_display', read_only=True)
    results = GeneratedImageSerializer(many=True, read_only=True)
    original_image_url = serializers.ImageField(source='original_image', read_only=True)
    clean_image_url = serializers.ImageField(source='clean_image', read_only=True)
    user = UserSerializer(read_only=True)
    processing_duration = serializers.SerializerMethodField()

    # Write-only fields for creation/update
    screen_type = serializers.ChoiceField(
        choices=VisualizationRequest.SCREEN_TYPE_CHOICES,
        required=False,
        allow_null=True,
        help_text="Type of screen to apply"
    )

    class Meta:
        model = VisualizationRequest
        fields = [
            # Read-only response fields
            'id', 'user', 'original_image_url', 'clean_image_url', 'screen_type_display',
            'status', 'created_at', 'updated_at', 'task_id', 'results',
            'processing_started_at', 'processing_completed_at', 'processing_duration',
            'error_message', 'progress_percentage', 'status_message',
            # Write-only fields for creation
            'original_image', 'screen_type', 'opacity', 'color',
            'screen_categories', 'mesh_choice', 'frame_color', 'mesh_color', 'scope',
            'window_count', 'door_count', 'door_type', 'patio_enclosure'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'created_at', 'updated_at', 'task_id',
            'results', 'original_image_url', 'clean_image_url', 'screen_type_display',
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
        fields = ['id', 'original_image', 'screen_type', 'opacity', 'color',
                  'screen_categories', 'mesh_choice', 'frame_color', 'mesh_color', 'scope',
                  'window_count', 'door_count', 'door_type', 'patio_enclosure',
                  'status', 'progress_percentage', 'status_message', 'created_at']
        read_only_fields = ['id', 'status', 'progress_percentage', 'status_message', 'created_at']
        extra_kwargs = {
            'original_image': {'required': True},
            'screen_type': {'required': False, 'allow_null': True},
            'scope': {'required': False}
        }

    def validate_original_image(self, value):
        """Validate uploaded image file."""
        # Reuse validation from detail serializer
        detail_serializer = VisualizationRequestDetailSerializer()
        return detail_serializer.validate_original_image(value)

    def validate_mesh_choice(self, value):
        """Validate mesh choice against tenant config."""
        config = get_tenant_config()
        valid_choices = [c[0] for c in config.get_mesh_choices()]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid mesh choice. Valid options: {valid_choices}"
            )
        return value
    
    def validate_frame_color(self, value):
        """Validate frame color against tenant config."""
        config = get_tenant_config()
        valid_choices = [c[0] for c in config.get_frame_color_choices()]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid frame color. Valid options: {valid_choices}"
            )
        return value


class LeadSerializer(serializers.ModelSerializer):
    """Serializer for lead capture."""
    visualization_id = serializers.IntegerField(write_only=True)
    pdf_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        from .models import Lead
        model = Lead
        fields = [
            'id', 'visualization_id', 'name', 'email', 'phone',
            'address_street', 'address_city', 'address_state', 'address_zip',
            'is_existing_customer', 'created_at', 'pdf_url'
        ]
        read_only_fields = ['id', 'created_at', 'pdf_url']

    def validate_visualization_id(self, value):
        """Validate visualization exists."""
        from .models import VisualizationRequest
        try:
            VisualizationRequest.objects.get(id=value)
        except VisualizationRequest.DoesNotExist:
            raise serializers.ValidationError("Visualization not found.")
        return value

    def validate_phone(self, value):
        """Validate phone has at least 10 digits."""
        digits = ''.join(c for c in value if c.isdigit())
        if len(digits) < 10:
            raise serializers.ValidationError("Phone must have at least 10 digits.")
        return value

    def validate_address_zip(self, value):
        """Validate ZIP is 5 digits."""
        digits = ''.join(c for c in value if c.isdigit())
        if len(digits) < 5:
            raise serializers.ValidationError("ZIP code must be at least 5 digits.")
        return value

    def create(self, validated_data):
        from .models import VisualizationRequest, Lead
        visualization_id = validated_data.pop('visualization_id')
        visualization = VisualizationRequest.objects.get(id=visualization_id)
        return Lead.objects.create(visualization=visualization, **validated_data)

    def get_pdf_url(self, obj):
        """Return the PDF URL for the visualization."""
        request = self.context.get('request')
        if obj.visualization.generated_pdf:
            if request:
                return request.build_absolute_uri(obj.visualization.generated_pdf.url)
            return obj.visualization.generated_pdf.url
        # Fallback to dynamic generation endpoint
        if request:
            return request.build_absolute_uri(f'/api/visualization/{obj.visualization.id}/pdf/')
        return f'/api/visualization/{obj.visualization.id}/pdf/'


