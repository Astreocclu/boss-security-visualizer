"""
AI Service Factory for creating and managing AI service instances.

The factory provides a centralized way to create AI service instances
with proper configuration and error handling.
"""

import logging
from typing import Optional, Dict, Any
from .interfaces import (
    AIImageGenerationService,
    AIVisionService,
    AIServiceType,
    AIServiceConfig
)
from .registry import ai_service_registry

logger = logging.getLogger(__name__)


class AIServiceFactory:
    """
    Factory class for creating AI service instances.

    This factory works with the AI service registry to create properly
    configured service instances based on user requirements.
    """

    @staticmethod
    def create_image_generation_service(
        provider_name: str = None,
        config: AIServiceConfig = None,
        requirements: Dict[str, Any] = None
    ) -> Optional[AIImageGenerationService]:
        """
        Create an AI image generation service instance.

        Args:
            provider_name: Specific provider to use (optional)
            config: Service configuration (optional)
            requirements: Requirements for provider selection (optional)

        Returns:
            AIImageGenerationService instance or None if creation failed
        """
        try:
            # Determine provider
            if not provider_name:
                provider_name = ai_service_registry.find_best_provider(
                    AIServiceType.IMAGE_GENERATION,
                    requirements
                )

            if not provider_name:
                logger.error("No suitable image generation provider found")
                return None

            # Get provider instance
            provider = ai_service_registry.get_provider(provider_name)
            if not provider:
                logger.error(f"Provider '{provider_name}' not found in registry")
                return None

            # Create default config if not provided
            if not config:
                from .config import ai_config_manager
                config = ai_config_manager.get_config(provider_name)
                if not config:
                    config = AIServiceConfig(
                        service_name=provider_name,
                        service_type=AIServiceType.IMAGE_GENERATION
                    )

            # Create service instance
            service = provider.create_service(AIServiceType.IMAGE_GENERATION, config)

            logger.info(f"Successfully created image generation service using provider '{provider_name}'")
            return service

        except Exception as e:
            logger.error(f"Failed to create image generation service: {str(e)}")
            return None

    @staticmethod
    def create_vision_service(
        provider_name: str = None,
        config: AIServiceConfig = None,
        requirements: Dict[str, Any] = None
    ) -> Optional[AIVisionService]:
        """
        Create an AI vision service instance.

        Args:
            provider_name: Specific provider to use (optional)
            config: Service configuration (optional)
            requirements: Requirements for provider selection (optional)

        Returns:
            AIVisionService instance or None if creation failed
        """
        try:
            # Determine provider
            if not provider_name:
                provider_name = ai_service_registry.find_best_provider(
                    AIServiceType.COMPUTER_VISION,
                    requirements
                )

            if not provider_name:
                logger.error("No suitable vision service provider found")
                return None

            # Get provider instance
            provider = ai_service_registry.get_provider(provider_name)
            if not provider:
                logger.error(f"Provider '{provider_name}' not found in registry")
                return None

            # Create default config if not provided
            if not config:
                from .config import ai_config_manager
                config = ai_config_manager.get_config(provider_name)
                if not config:
                    config = AIServiceConfig(
                        service_name=provider_name,
                        service_type=AIServiceType.COMPUTER_VISION
                    )

            # Create service instance
            service = provider.create_service(AIServiceType.COMPUTER_VISION, config)

            logger.info(f"Successfully created vision service using provider '{provider_name}'")
            return service

        except Exception as e:
            logger.error(f"Failed to create vision service: {str(e)}")
            return None

    @staticmethod
    def create_service_by_type(
        service_type: AIServiceType,
        provider_name: str = None,
        config: AIServiceConfig = None,
        requirements: Dict[str, Any] = None
    ):
        """
        Create a service instance by service type.

        Args:
            service_type: Type of service to create
            provider_name: Specific provider to use (optional)
            config: Service configuration (optional)
            requirements: Requirements for provider selection (optional)

        Returns:
            Service instance or None if creation failed
        """
        if service_type == AIServiceType.IMAGE_GENERATION:
            return AIServiceFactory.create_image_generation_service(
                provider_name, config, requirements
            )
        elif service_type == AIServiceType.COMPUTER_VISION:
            return AIServiceFactory.create_vision_service(
                provider_name, config, requirements
            )
        elif service_type == AIServiceType.IMAGE_ENHANCEMENT:
            # Image enhancement can be handled by either image generation or vision services
            # Try image generation first, then vision
            service = AIServiceFactory.create_image_generation_service(
                provider_name, config, requirements
            )
            if not service:
                service = AIServiceFactory.create_vision_service(
                    provider_name, config, requirements
                )
            return service
        else:
            logger.error(f"Unknown service type: {service_type}")
            return None

    @staticmethod
    def get_available_providers(service_type: AIServiceType) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available providers for a service type.

        Args:
            service_type: Type of service

        Returns:
            Dictionary mapping provider names to their capabilities
        """
        providers = ai_service_registry.get_providers_for_service(service_type)
        provider_info = {}

        for provider_name in providers:
            provider_info[provider_name] = ai_service_registry.get_provider_capabilities(provider_name)

        return provider_info

    @staticmethod
    def validate_service_config(config: AIServiceConfig) -> bool:
        """
        Validate a service configuration.

        Args:
            config: Configuration to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Basic validation
            if not config.service_name:
                logger.error("Service name is required")
                return False

            if not isinstance(config.service_type, AIServiceType):
                logger.error("Invalid service type")
                return False

            if config.max_requests_per_minute <= 0:
                logger.error("Max requests per minute must be positive")
                return False

            if config.timeout_seconds <= 0:
                logger.error("Timeout seconds must be positive")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating service config: {str(e)}")
            return False

    @staticmethod
    def get_factory_status() -> Dict[str, Any]:
        """
        Get factory status and statistics.

        Returns:
            Dictionary with factory status information
        """
        registry_status = ai_service_registry.get_registry_status()

        status = {
            'factory_version': '1.0.0',
            'registry_status': registry_status,
            'supported_service_types': [st.value for st in AIServiceType],
            'total_available_services': sum(
                count if isinstance(count, int) else 0
                for count in registry_status['providers_by_service'].values()
            )
        }

        return status
