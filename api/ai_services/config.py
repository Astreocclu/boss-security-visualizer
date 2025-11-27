"""
Configuration management for AI services.

This module handles loading, validating, and managing configurations
for different AI service providers.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from .interfaces import AIServiceConfig, AIServiceType

logger = logging.getLogger(__name__)


class AIServiceConfigManager:
    """
    Manager for AI service configurations.

    Handles loading configurations from various sources including
    environment variables, configuration files, and Django settings.
    """

    def __init__(self):
        self._configs: Dict[str, AIServiceConfig] = {}
        self._load_default_configs()

    def load_configs(self):
        """Public method to reload configurations."""
        self._load_default_configs()

    def _load_default_configs(self):
        """Load default configurations for known AI services."""
        try:
            # Load from Django settings if available
            if hasattr(settings, 'AI_SERVICES_CONFIG'):
                self._load_from_django_settings()

            # Load from environment variables
            self._load_from_environment()

            # Load from configuration file if it exists
            config_file = getattr(settings, 'AI_SERVICES_CONFIG_FILE', None)
            if config_file and os.path.exists(config_file):
                self._load_from_file(config_file)

        except Exception as e:
            logger.error(f"Error loading default AI service configs: {str(e)}")

    def _load_from_django_settings(self):
        """Load configurations from Django settings."""
        try:
            ai_config = settings.AI_SERVICES_CONFIG

            for service_name, config_data in ai_config.items():
                config = self._create_config_from_dict(service_name, config_data)
                if config:
                    self._configs[service_name] = config
                    logger.info(f"Loaded config for '{service_name}' from Django settings")

        except Exception as e:
            logger.error(f"Error loading configs from Django settings: {str(e)}")

    def _load_from_environment(self):
        """Load configurations from environment variables."""
        try:
            # OpenAI configuration
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                config = AIServiceConfig(
                    service_name='openai',
                    service_type=AIServiceType.IMAGE_GENERATION,
                    api_key=openai_key,
                    api_endpoint=os.getenv('OPENAI_API_ENDPOINT', 'https://api.openai.com/v1'),
                    model_name=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                    max_requests_per_minute=int(os.getenv('OPENAI_MAX_REQUESTS', '60')),
                    timeout_seconds=int(os.getenv('OPENAI_TIMEOUT', '30'))
                )
                self._configs['openai'] = config
                logger.info(f"Loaded OpenAI config from environment (key: {openai_key[:10]}...)")
            else:
                logger.info("No OpenAI API key found in environment")

            # Google Cloud Vision configuration
            google_key = os.getenv('GOOGLE_CLOUD_API_KEY')
            if google_key:
                config = AIServiceConfig(
                    service_name='google_vision',
                    service_type=AIServiceType.COMPUTER_VISION,
                    api_key=google_key,
                    api_endpoint=os.getenv('GOOGLE_VISION_ENDPOINT', 'https://vision.googleapis.com/v1'),
                    max_requests_per_minute=int(os.getenv('GOOGLE_MAX_REQUESTS', '60')),
                    timeout_seconds=int(os.getenv('GOOGLE_TIMEOUT', '30'))
                )
                self._configs['google_vision'] = config
                logger.info("Loaded Google Vision config from environment")

            # Anthropic Claude configuration
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                config = AIServiceConfig(
                    service_name='anthropic',
                    service_type=AIServiceType.COMPUTER_VISION,
                    api_key=anthropic_key,
                    api_endpoint=os.getenv('ANTHROPIC_API_ENDPOINT', 'https://api.anthropic.com/v1'),
                    model_name=os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229'),
                    max_requests_per_minute=int(os.getenv('ANTHROPIC_MAX_REQUESTS', '60')),
                    timeout_seconds=int(os.getenv('ANTHROPIC_TIMEOUT', '30'))
                )
                self._configs['anthropic'] = config
                logger.info("Loaded Anthropic config from environment")

        except Exception as e:
            logger.error(f"Error loading configs from environment: {str(e)}")

    def _load_from_file(self, config_file: str):
        """Load configurations from a JSON file."""
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)

            for service_name, config_data in file_config.items():
                config = self._create_config_from_dict(service_name, config_data)
                if config:
                    self._configs[service_name] = config
                    logger.info(f"Loaded config for '{service_name}' from file")

        except Exception as e:
            logger.error(f"Error loading configs from file '{config_file}': {str(e)}")

    def _create_config_from_dict(self, service_name: str, config_data: Dict[str, Any]) -> Optional[AIServiceConfig]:
        """Create an AIServiceConfig from dictionary data."""
        try:
            # Parse service type
            service_type_str = config_data.get('service_type', 'image_generation')
            service_type = AIServiceType(service_type_str)

            config = AIServiceConfig(
                service_name=service_name,
                service_type=service_type,
                api_key=config_data.get('api_key'),
                api_endpoint=config_data.get('api_endpoint'),
                model_name=config_data.get('model_name'),
                max_requests_per_minute=config_data.get('max_requests_per_minute', 60),
                timeout_seconds=config_data.get('timeout_seconds', 30),
                additional_params=config_data.get('additional_params', {})
            )

            return config

        except Exception as e:
            logger.error(f"Error creating config for '{service_name}': {str(e)}")
            return None

    def get_config(self, service_name: str) -> Optional[AIServiceConfig]:
        """
        Get configuration for a specific service.

        Args:
            service_name: Name of the service

        Returns:
            AIServiceConfig or None if not found
        """
        return self._configs.get(service_name)

    def set_config(self, service_name: str, config: AIServiceConfig):
        """
        Set configuration for a service.

        Args:
            service_name: Name of the service
            config: Configuration to set
        """
        self._configs[service_name] = config
        logger.info(f"Set config for service '{service_name}'")

    def get_all_configs(self) -> Dict[str, AIServiceConfig]:
        """
        Get all loaded configurations.

        Returns:
            Dictionary mapping service names to configurations
        """
        return self._configs.copy()

    def get_configs_by_type(self, service_type: AIServiceType) -> Dict[str, AIServiceConfig]:
        """
        Get all configurations for a specific service type.

        Args:
            service_type: Type of service

        Returns:
            Dictionary mapping service names to configurations
        """
        return {
            name: config for name, config in self._configs.items()
            if config.service_type == service_type
        }

    def validate_config(self, config: AIServiceConfig) -> bool:
        """
        Validate a service configuration.

        Args:
            config: Configuration to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
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
            logger.error(f"Error validating config: {str(e)}")
            return False

    def save_to_file(self, config_file: str):
        """
        Save current configurations to a JSON file.

        Args:
            config_file: Path to save the configuration file
        """
        try:
            config_data = {}

            for service_name, config in self._configs.items():
                config_data[service_name] = {
                    'service_type': config.service_type.value,
                    'api_endpoint': config.api_endpoint,
                    'model_name': config.model_name,
                    'max_requests_per_minute': config.max_requests_per_minute,
                    'timeout_seconds': config.timeout_seconds,
                    'additional_params': config.additional_params
                    # Note: API keys are not saved to file for security
                }

            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"Saved configurations to '{config_file}'")

        except Exception as e:
            logger.error(f"Error saving configs to file '{config_file}': {str(e)}")

    def get_manager_status(self) -> Dict[str, Any]:
        """
        Get configuration manager status.

        Returns:
            Dictionary with status information
        """
        status = {
            'total_configs': len(self._configs),
            'configs_by_type': {},
            'configured_services': list(self._configs.keys())
        }

        # Count configs by service type
        for service_type in AIServiceType:
            configs = self.get_configs_by_type(service_type)
            status['configs_by_type'][service_type.value] = len(configs)

        return status


# Global configuration manager instance
ai_config_manager = AIServiceConfigManager()
