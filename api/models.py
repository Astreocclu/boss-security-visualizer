import os
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from PIL import Image


def validate_image_size(image):
    """Validate that uploaded image is not too large."""
    max_size = 10 * 1024 * 1024  # 10MB
    if image.size > max_size:
        raise ValidationError(f'Image size cannot exceed {max_size / (1024 * 1024):.1f}MB')


def validate_image_dimensions(image):
    """Validate image dimensions."""
    max_width, max_height = 8192, 8192
    try:
        img = Image.open(image)
        if img.width > max_width or img.height > max_height:
            raise ValidationError(
                f'Image dimensions cannot exceed {max_width}x{max_height} pixels. '
                f'Current dimensions: {img.width}x{img.height}'
            )
    except Exception as e:
        raise ValidationError(f'Invalid image file: {str(e)}')


def upload_to_originals(instance, filename):
    """Generate upload path for original images."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('originals', str(instance.user.id), filename)


def upload_to_generated(instance, filename):
    """Generate upload path for generated images."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('generated', str(instance.request.user.id), filename)


class UserProfileManager(models.Manager):
    """Custom manager for UserProfile model."""

    def get_or_create_for_user(self, user):
        """Get or create a profile for the given user."""
        profile, created = self.get_or_create(user=user)
        return profile, created


class UserProfile(models.Model):
    """Extended user profile with additional information."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="Associated user account"
    )
    company_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Company or organization name"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserProfileManager()

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def full_name(self):
        """Return user's full name or username if not available."""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username

    def get_total_requests(self):
        """Get total number of visualization requests for this user."""
        return self.user.visualization_requests.count()

    def get_completed_requests(self):
        """Get number of completed visualization requests."""
        return self.user.visualization_requests.filter(status='complete').count()


class ScreenTypeManager(models.Manager):
    """Custom manager for ScreenType model."""

    def active(self):
        """Return only active screen types."""
        return self.filter(is_active=True)

    def get_by_name(self, name):
        """Get screen type by name (case-insensitive)."""
        return self.filter(name__iexact=name).first()


class ScreenType(models.Model):
    """Screen type options for visualization."""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Screen type name (e.g., Security, Lifestyle)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the screen type"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this screen type is available for selection"
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Order for displaying screen types"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ScreenTypeManager()

    class Meta:
        verbose_name = "Screen Type"
        verbose_name_plural = "Screen Types"
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Validate model data."""
        if self.name:
            self.name = self.name.strip().title()

    def save(self, *args, **kwargs):
        """Override save to call clean."""
        self.clean()
        super().save(*args, **kwargs)

    def get_request_count(self):
        """Get number of requests using this screen type."""
        return self.visualization_requests.count()


class VisualizationRequestManager(models.Manager):
    """Custom manager for VisualizationRequest model."""

    def for_user(self, user):
        """Get requests for a specific user."""
        return self.filter(user=user)

    def pending(self):
        """Get pending requests."""
        return self.filter(status='pending')

    def processing(self):
        """Get processing requests."""
        return self.filter(status='processing')

    def completed(self):
        """Get completed requests."""
        return self.filter(status='complete')

    def failed(self):
        """Get failed requests."""
        return self.filter(status='failed')

    def recent(self, days=7):
        """Get requests from the last N days."""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)


class VisualizationRequest(models.Model):
    """Request for image visualization with screen overlay."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='visualization_requests',
        help_text="User who made the request"
    )
    original_image = models.ImageField(
        upload_to=upload_to_originals,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_image_size,
            validate_image_dimensions,
        ],
        help_text="Original image to be processed"
    )
    clean_image = models.ImageField(
        upload_to=upload_to_generated,
        null=True,
        blank=True,
        help_text="Intermediate cleaned image (Step 1)"
    )
    screen_type = models.ForeignKey(
        ScreenType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visualization_requests',
        help_text="Type of screen to overlay"
    )
    opacity = models.CharField(
        max_length=10,
        choices=[('80', '80%'), ('95', '95%'), ('99', '99%')],
        null=True,
        blank=True,
        help_text="Screen opacity percentage"
    )
    color = models.CharField(
        max_length=50,
        choices=[('Black', 'Black'), ('Dark Bronze', 'Dark Bronze'), ('Stucco', 'Stucco')],
        null=True,
        blank=True,
        help_text="Screen frame/fabric color"
    )
    status = models.CharField(
        max_length=20,
        default='pending',
        choices=STATUS_CHOICES,
        help_text="Current processing status"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if processing failed"
    )
    processing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When processing started"
    )
    processing_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When processing completed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    task_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Background task ID for async processing"
    )
    progress_percentage = models.PositiveIntegerField(
        default=0,
        help_text="Processing progress percentage (0-100)"
    )
    status_message = models.CharField(
        max_length=200,
        blank=True,
        help_text="Current processing status message"
    )

    objects = VisualizationRequestManager()

    class Meta:
        verbose_name = "Visualization Request"
        verbose_name_plural = "Visualization Requests"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Request {self.id} by {self.user.username} ({self.status})"

    def clean(self):
        """Validate model data."""
        if self.status == 'processing' and not self.processing_started_at:
            self.processing_started_at = timezone.now()

        if self.status == 'complete' and not self.processing_completed_at:
            self.processing_completed_at = timezone.now()

    def save(self, *args, **kwargs):
        """Override save to call clean."""
        self.clean()
        super().save(*args, **kwargs)

    @property
    def processing_duration(self):
        """Get processing duration if available."""
        if self.processing_started_at and self.processing_completed_at:
            return self.processing_completed_at - self.processing_started_at
        return None

    @property
    def is_completed(self):
        """Check if request is completed."""
        return self.status == 'complete'

    @property
    def is_failed(self):
        """Check if request failed."""
        return self.status == 'failed'

    @property
    def is_processing(self):
        """Check if request is currently processing."""
        return self.status == 'processing'

    def mark_as_processing(self, task_id=None):
        """Mark request as processing."""
        self.status = 'processing'
        self.processing_started_at = timezone.now()
        self.progress_percentage = 0
        self.status_message = "Starting image processing..."
        if task_id:
            self.task_id = task_id
        self.save()

    def update_progress(self, progress, status_message=None):
        """Update processing progress."""
        self.progress_percentage = min(100, max(0, progress))
        if status_message:
            self.status_message = status_message
        self.save(update_fields=['progress_percentage', 'status_message'])

    def mark_as_complete(self):
        """Mark request as complete."""
        self.status = 'complete'
        self.processing_completed_at = timezone.now()
        self.progress_percentage = 100
        self.status_message = "Processing completed successfully!"
        self.save()

    def mark_as_failed(self, error_message=None):
        """Mark request as failed."""
        self.status = 'failed'
        self.progress_percentage = 0
        if error_message:
            self.error_message = error_message
            self.status_message = f"Failed: {error_message}"
        else:
            self.status_message = "Processing failed"
        self.save()

    def get_result_count(self):
        """Get number of generated results."""
        return self.results.count()


class GeneratedImageManager(models.Manager):
    """Custom manager for GeneratedImage model."""

    def for_request(self, request):
        """Get images for a specific request."""
        return self.filter(request=request)

    def recent(self, days=7):
        """Get images generated in the last N days."""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return self.filter(generated_at__gte=cutoff_date)


class GeneratedImage(models.Model):
    """Generated image result from visualization processing."""

    request = models.ForeignKey(
        VisualizationRequest,
        related_name='results',
        on_delete=models.CASCADE,
        help_text="Associated visualization request"
    )
    generated_image = models.ImageField(
        upload_to=upload_to_generated,
        help_text="Generated image with screen overlay"
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    image_width = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Image width in pixels"
    )
    image_height = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Image height in pixels"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata (e.g., quality score, generation params)"
    )
    generated_at = models.DateTimeField(auto_now_add=True)

    objects = GeneratedImageManager()

    class Meta:
        verbose_name = "Generated Image"
        verbose_name_plural = "Generated Images"
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['request', '-generated_at']),
            models.Index(fields=['generated_at']),
        ]

    def __str__(self):
        return f"Result for Request {self.request.id}"

    def save(self, *args, **kwargs):
        """Override save to extract image metadata."""
        if self.generated_image and not self.file_size:
            try:
                self.file_size = self.generated_image.size

                # Extract image dimensions
                img = Image.open(self.generated_image)
                self.image_width = img.width
                self.image_height = img.height
            except Exception:
                pass  # Ignore errors in metadata extraction

        super().save(*args, **kwargs)

    @property
    def file_size_mb(self):
        """Get file size in MB."""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None

    @property
    def dimensions(self):
        """Get image dimensions as string."""
        if self.image_width and self.image_height:
            return f"{self.image_width}x{self.image_height}"
        return None
