import logging
from openai import AsyncOpenAI
from .config import settings

logger = logging.getLogger(__name__)

# Determine provider and model
_provider = None
_model = None
_client = None

def _initialize_provider():
    global _provider, _model, _client
    
    configured = settings.llm_provider.lower()
    
    if configured == "groq":
        if not settings.groq_api_key:
            raise ValueError("Configuration Error: LLM_PROVIDER is set to 'groq' but GROQ_API_KEY is missing.")
        _provider = "groq"
        _model = settings.groq_model
        _client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url
        )
    elif configured == "openai" or (not configured and settings.openai_api_key):
        if not settings.openai_api_key:
            raise ValueError("Configuration Error: LLM_PROVIDER is set to 'openai' but OPENAI_API_KEY is missing.")
        _provider = "openai"
        _model = settings.openai_model
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    elif configured == "openrouter" or (not configured and settings.openrouter_api_key):
        if not settings.openrouter_api_key:
            raise ValueError("Configuration Error: LLM_PROVIDER is set to 'openrouter' but OPENROUTER_API_KEY is missing.")
        _provider = "openrouter"
        _model = settings.openrouter_model or settings.llm_model
        _client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url
        )
    else:
        raise ValueError("Configuration Error: No valid LLM provider configured. Please set LLM_PROVIDER and the corresponding API key.")
        
    logger.info(f"LLM provider: {_provider}")
    print(f"LLM provider: {_provider}") # For visibility if logger is not configured

_initialize_provider()

def get_llm_provider() -> str:
    return _provider

def get_llm_model() -> str:
    return _model

def get_llm_client() -> AsyncOpenAI:
    return _client
