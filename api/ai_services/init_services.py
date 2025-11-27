
def initialize_ai_services():
    """Initialize AI services with proper error handling"""
    from api.ai_services.config import ai_config_manager
    from api.ai_services.registry import ai_service_registry
    from api.ai_services.providers.openai_provider import OpenAIProvider
    from api.ai_services.providers.mock_provider import MockAIProvider
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Load configurations
        ai_config_manager.load_configs()
        
        # Register Mock Provider (always available)
        mock_provider = MockAIProvider()
        ai_service_registry.register_provider('mock_ai', mock_provider)
        logger.info("Mock AI provider registered successfully")
        
        # Register OpenAI Provider (if API key available)
        openai_config = ai_config_manager.get_config('openai')
        if openai_config and openai_config.api_key:
            openai_provider = OpenAIProvider()
            ai_service_registry.register_provider('openai', openai_provider)
            logger.info("OpenAI provider registered successfully")
        else:
            logger.warning("OpenAI API key not found, skipping OpenAI provider registration")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing AI services: {str(e)}")
        return False

# Call this function when Django starts
initialize_ai_services()
