"""
Base AI service provider implementation.

This module provides a base class that other AI service providers can extend,
providing common functionality and utilities.
"""

import logging
import time
from typing import Dict, Any, List
from ..interfaces import AIServiceProvider, AIServiceType, AIServiceConfig

logger = logging.getLogger(__name__)


class BaseAIProvider(AIServiceProvider):
    """
    Base implementation for AI service providers.
    
    This class provides common functionality that can be shared across
    different AI service provider implementations.
    """
    
    def __init__(self, provider_name: str, supported_services: List[AIServiceType]):
        self.provider_name = provider_name
        self.supported_services = supported_services
        self._service_instances = {}
        self._last_request_time = {}
        self._request_counts = {}
        
        logger.info(f"Initialized {provider_name} provider with services: {supported_services}")
    
    def get_available_services(self) -> List[AIServiceType]:
        """Get list of available service types from this provider."""
        return self.supported_services.copy()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            'name': self.provider_name,
            'supported_services': [service.value for service in self.supported_services],
            'active_instances': len(self._service_instances),
            'total_requests': sum(self._request_counts.values()),
            'status': 'active'
        }
    
    def _validate_service_type(self, service_type: AIServiceType) -> bool:
        """
        Validate that this provider supports the requested service type.
        
        Args:
            service_type: Type of service requested
            
        Returns:
            bool: True if supported, False otherwise
        """
        if service_type not in self.supported_services:
            logger.error(f"Provider '{self.provider_name}' does not support service type: {service_type}")
            return False
        return True
    
    def _check_rate_limit(self, config: AIServiceConfig) -> bool:
        """
        Check if the request is within rate limits.
        
        Args:
            config: Service configuration with rate limit settings
            
        Returns:
            bool: True if request is allowed, False if rate limited
        """
        service_key = f"{self.provider_name}_{config.service_type.value}"
        current_time = time.time()
        
        # Initialize tracking if not exists
        if service_key not in self._last_request_time:
            self._last_request_time[service_key] = current_time
            self._request_counts[service_key] = 0
            return True
        
        # Check if we need to reset the counter (new minute)
        time_diff = current_time - self._last_request_time[service_key]
        if time_diff >= 60:  # Reset every minute
            self._request_counts[service_key] = 0
            self._last_request_time[service_key] = current_time
        
        # Check rate limit
        if self._request_counts[service_key] >= config.max_requests_per_minute:
            logger.warning(f"Rate limit exceeded for {service_key}")
            return False
        
        # Increment counter
        self._request_counts[service_key] += 1
        return True
    
    def _log_request(self, service_type: AIServiceType, operation: str, success: bool, duration: float):
        """
        Log a service request for monitoring and debugging.
        
        Args:
            service_type: Type of service used
            operation: Operation performed
            success: Whether the operation was successful
            duration: Duration of the operation in seconds
        """
        status = "SUCCESS" if success else "FAILED"
        logger.info(
            f"AI Request - Provider: {self.provider_name}, "
            f"Service: {service_type.value}, Operation: {operation}, "
            f"Status: {status}, Duration: {duration:.2f}s"
        )
    
    def _handle_service_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """
        Handle and format service errors consistently.
        
        Args:
            error: Exception that occurred
            operation: Operation that failed
            
        Returns:
            Dictionary with error information
        """
        error_info = {
            'provider': self.provider_name,
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': time.time()
        }
        
        logger.error(f"Service error in {self.provider_name}: {error_info}")
        return error_info
    
    def get_service_health(self) -> Dict[str, Any]:
        """
        Get health status of the provider and its services.
        
        Returns:
            Dictionary with health information
        """
        health_info = {
            'provider_name': self.provider_name,
            'status': 'healthy',
            'supported_services': [service.value for service in self.supported_services],
            'active_instances': len(self._service_instances),
            'request_stats': self._request_counts.copy(),
            'last_check': time.time()
        }
        
        # Add service-specific health checks
        for service_type in self.supported_services:
            service_key = f"{service_type.value}_health"
            try:
                # Perform basic health check for each service
                health_info[service_key] = self._check_service_health(service_type)
            except Exception as e:
                health_info[service_key] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_info['status'] = 'degraded'
        
        return health_info
    
    def _check_service_health(self, service_type: AIServiceType) -> Dict[str, Any]:
        """
        Check health of a specific service type.
        
        Args:
            service_type: Type of service to check
            
        Returns:
            Dictionary with service health information
        """
        # Base implementation - can be overridden by specific providers
        return {
            'status': 'healthy',
            'service_type': service_type.value,
            'last_request': self._last_request_time.get(
                f"{self.provider_name}_{service_type.value}", 
                None
            )
        }
    
    def cleanup(self):
        """Clean up provider resources."""
        self._service_instances.clear()
        self._last_request_time.clear()
        self._request_counts.clear()
        logger.info(f"Cleaned up {self.provider_name} provider resources")
