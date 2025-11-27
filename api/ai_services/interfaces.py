"""
Core interfaces for AI services in the homescreen visualization system.

These interfaces define the contract that all AI service implementations must follow,
ensuring a consistent API regardless of the underlying AI provider.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import enum


class AIServiceType(enum.Enum):
    """Types of AI services available."""
    IMAGE_GENERATION = "image_generation"
    COMPUTER_VISION = "computer_vision"
    IMAGE_ENHANCEMENT = "image_enhancement"


class ProcessingStatus(enum.Enum):
    """Status of AI processing operations."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AIServiceConfig:
    """Configuration for an AI service."""
    service_name: str
    service_type: AIServiceType
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    model_name: Optional[str] = None
    max_requests_per_minute: int = 60
    timeout_seconds: int = 30
    additional_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}


@dataclass
class AIServiceResult:
    """Base result from an AI service operation."""
    success: bool
    status: ProcessingStatus
    message: str = ""
    error_details: Optional[str] = None
    processing_time_seconds: float = 0.0
    cost_estimate: Optional[float] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WindowDetectionResult(AIServiceResult):
    """Result from window/door detection in an image."""
    detected_windows: List[Dict[str, Any]] = None
    confidence_scores: List[float] = None
    bounding_boxes: List[Tuple[int, int, int, int]] = None  # (x1, y1, x2, y2)

    def __post_init__(self):
        super().__post_init__()
        if self.detected_windows is None:
            self.detected_windows = []
        if self.confidence_scores is None:
            self.confidence_scores = []
        if self.bounding_boxes is None:
            self.bounding_boxes = []


@dataclass
class ScreenAnalysisResult(AIServiceResult):
    """Result from screen pattern analysis."""
    screen_type: Optional[str] = None
    mesh_pattern: Optional[str] = None
    opacity_level: float = 0.0
    color_analysis: Dict[str, Any] = None
    texture_features: Dict[str, Any] = None

    def __post_init__(self):
        super().__post_init__()
        if self.color_analysis is None:
            self.color_analysis = {}
        if self.texture_features is None:
            self.texture_features = {}


@dataclass
class QualityAssessmentResult(AIServiceResult):
    """Result from image quality assessment."""
    overall_score: float = 0.0
    realism_score: float = 0.0
    technical_quality: float = 0.0
    aesthetic_score: float = 0.0
    improvement_suggestions: List[str] = None

    def __post_init__(self):
        super().__post_init__()
        if self.improvement_suggestions is None:
            self.improvement_suggestions = []


class AIImageGenerationService(ABC):
    """Abstract base class for AI image generation services."""

    def __init__(self, config: AIServiceConfig):
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate the service configuration."""
        pass

    @abstractmethod
    def generate_screen_visualization(
        self,
        original_image: Image.Image,
        screen_type: str,
        detection_areas: List[Tuple[int, int, int, int]] = None,
        style_preferences: Dict[str, Any] = None
    ) -> AIServiceResult:
        """
        Generate a realistic screen visualization on the provided image.

        Args:
            original_image: The original house/building image
            screen_type: Type of screen to apply (security, lifestyle, etc.)
            detection_areas: Optional pre-detected window/door areas
            style_preferences: Optional style customization parameters

        Returns:
            AIServiceResult with generated image data
        """
        pass

    @abstractmethod
    def enhance_image_quality(
        self,
        image: Image.Image,
        enhancement_type: str = "general"
    ) -> AIServiceResult:
        """
        Enhance the quality of a generated image.

        Args:
            image: Image to enhance
            enhancement_type: Type of enhancement to apply

        Returns:
            AIServiceResult with enhanced image
        """
        pass

    @abstractmethod
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status and health information."""
        pass


class AIVisionService(ABC):
    """Abstract base class for AI computer vision services."""

    def __init__(self, config: AIServiceConfig):
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate the service configuration."""
        pass

    @abstractmethod
    def detect_windows_and_doors(
        self,
        image: Image.Image,
        confidence_threshold: float = 0.7,
        screen_type: str = None
    ) -> WindowDetectionResult:
        """
        Detect windows and doors in an image with context-aware analysis.

        Args:
            image: Input image to analyze
            confidence_threshold: Minimum confidence for detections
            screen_type: Type of screen for context-aware detection

        Returns:
            WindowDetectionResult with detection information
        """
        pass

    @abstractmethod
    def analyze_screen_pattern(
        self,
        image: Image.Image,
        screen_area: Tuple[int, int, int, int] = None
    ) -> ScreenAnalysisResult:
        """
        Analyze screen patterns and characteristics in an image.

        Args:
            image: Image containing screen to analyze
            screen_area: Optional bounding box of screen area

        Returns:
            ScreenAnalysisResult with analysis data
        """
        pass

    @abstractmethod
    def assess_image_quality(
        self,
        image: Image.Image,
        reference_image: Image.Image = None
    ) -> QualityAssessmentResult:
        """
        Assess the quality and realism of a generated image.

        Args:
            image: Generated image to assess
            reference_image: Optional reference for comparison

        Returns:
            QualityAssessmentResult with quality metrics
        """
        pass

    @abstractmethod
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status and health information."""
        pass


class AIServiceProvider(ABC):
    """Abstract base class for AI service providers that can offer multiple services."""

    @abstractmethod
    def get_available_services(self) -> List[AIServiceType]:
        """Get list of available service types from this provider."""
        pass

    @abstractmethod
    def create_service(self, service_type: AIServiceType, config: AIServiceConfig):
        """Create a specific service instance."""
        pass

    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        pass
