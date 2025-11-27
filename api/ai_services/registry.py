"""
AI Service Registry for managing and discovering available AI services.

The registry maintains a catalog of available AI service providers and their
capabilities, allowing for dynamic service discovery and selection.
"""

import logging
from typing import Dict, List, Optional, Type
from .interfaces import AIServiceProvider, AIServiceType, AIServiceConfig

logger = logging.getLogger(__name__)


class AIServiceRegistry:
    """
    Registry for managing AI service providers and their capabilities.
    
    This class implements a singleton pattern to ensure a single source of truth
    for available AI services throughout the application.
    """
    
    _instance = None
    _providers: Dict[str, AIServiceProvider] = {}
    _service_mappings: Dict[AIServiceType, List[str]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the registry with default service mappings."""
        self._providers = {}
        self._service_mappings = {
            AIServiceType.IMAGE_GENERATION: [],
            AIServiceType.COMPUTER_VISION: [],
            AIServiceType.IMAGE_ENHANCEMENT: []
        }
        logger.info("AI Service Registry initialized")
    
    def register_provider(self, provider_name: str, provider: AIServiceProvider) -> bool:
        """
        Register a new AI service provider.
        
        Args:
            provider_name: Unique name for the provider
            provider: Provider instance implementing AIServiceProvider
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            if provider_name in self._providers:
                logger.warning(f"Provider '{provider_name}' already registered, overwriting")
            
            self._providers[provider_name] = provider
            
            # Update service mappings
            available_services = provider.get_available_services()
            for service_type in available_services:
                if provider_name not in self._service_mappings[service_type]:
                    self._service_mappings[service_type].append(provider_name)
            
            logger.info(f"Successfully registered provider '{provider_name}' with services: {available_services}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register provider '{provider_name}': {str(e)}")
            return False
    
    def unregister_provider(self, provider_name: str) -> bool:
        """
        Unregister an AI service provider.
        
        Args:
            provider_name: Name of the provider to unregister
            
        Returns:
            bool: True if unregistration successful, False otherwise
        """
        try:
            if provider_name not in self._providers:
                logger.warning(f"Provider '{provider_name}' not found in registry")
                return False
            
            # Remove from service mappings
            for service_type, providers in self._service_mappings.items():
                if provider_name in providers:
                    providers.remove(provider_name)
            
            # Remove from providers
            del self._providers[provider_name]
            
            logger.info(f"Successfully unregistered provider '{provider_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister provider '{provider_name}': {str(e)}")
            return False
    
    def get_provider(self, provider_name: str) -> Optional[AIServiceProvider]:
        """
        Get a specific provider by name.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            AIServiceProvider instance or None if not found
        """
        return self._providers.get(provider_name)
    
    def get_providers_for_service(self, service_type: AIServiceType) -> List[str]:
        """
        Get list of provider names that support a specific service type.
        
        Args:
            service_type: Type of service needed
            
        Returns:
            List of provider names
        """
        return self._service_mappings.get(service_type, []).copy()
    
    def get_all_providers(self) -> Dict[str, AIServiceProvider]:
        """
        Get all registered providers.

        Returns:
            Dictionary mapping provider names to provider instances
        """
        return self._providers.copy()

    def get_available_providers(self) -> List[str]:
        """
        Get list of all available provider names.

        Returns:
            List of provider names
        """
        return list(self._providers.keys())
    
    def get_provider_capabilities(self, provider_name: str) -> Dict[str, any]:
        """
        Get detailed capabilities of a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Dictionary with provider capabilities and information
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return {}
        
        try:
            capabilities = {
                'provider_name': provider_name,
                'available_services': provider.get_available_services(),
                'provider_info': provider.get_provider_info(),
                'is_available': True
            }
            return capabilities
        except Exception as e:
            logger.error(f"Failed to get capabilities for provider '{provider_name}': {str(e)}")
            return {
                'provider_name': provider_name,
                'available_services': [],
                'provider_info': {},
                'is_available': False,
                'error': str(e)
            }
    
    def get_registry_status(self) -> Dict[str, any]:
        """
        Get overall registry status and statistics.
        
        Returns:
            Dictionary with registry status information
        """
        status = {
            'total_providers': len(self._providers),
            'providers_by_service': {},
            'provider_status': {}
        }
        
        # Count providers by service type
        for service_type, providers in self._service_mappings.items():
            status['providers_by_service'][service_type.value] = len(providers)
        
        # Get status for each provider
        for provider_name in self._providers:
            status['provider_status'][provider_name] = self.get_provider_capabilities(provider_name)
        
        return status
    
    def find_best_provider(
        self,
        service_type: AIServiceType,
        requirements: Dict[str, any] = None
    ) -> Optional[str]:
        """
        Find the best provider for a specific service type based on requirements.
        
        Args:
            service_type: Type of service needed
            requirements: Optional requirements for provider selection
            
        Returns:
            Name of the best provider or None if none found
        """
        available_providers = self.get_providers_for_service(service_type)
        
        if not available_providers:
            logger.warning(f"No providers available for service type: {service_type}")
            return None
        
        if not requirements:
            # Return first available provider if no specific requirements
            return available_providers[0]
        
        # TODO: Implement more sophisticated provider selection logic
        # based on requirements like cost, speed, quality, etc.
        
        # For now, return the first available provider
        return available_providers[0]
    
    def clear_registry(self):
        """Clear all registered providers (mainly for testing)."""
        self._providers.clear()
        for service_type in self._service_mappings:
            self._service_mappings[service_type].clear()
        logger.info("AI Service Registry cleared")


# Global registry instance
ai_service_registry = AIServiceRegistry()
