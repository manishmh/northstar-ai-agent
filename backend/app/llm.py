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
    
    if settings.openai_api_key:
        _provider = "openai"
        _model = settings.openai_model
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
        
    elif settings.openrouter_api_key:
        _provider = "openrouter"
        _model = settings.openrouter_model or settings.llm_model
        _client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url
        )
        
    else:
        raise ValueError("Configuration Error: Neither OPENAI_API_KEY nor OPENROUTER_API_KEY is configured. Please configure an LLM provider.")
        
    logger.info(f"LLM provider: {_provider}")
    print(f"LLM provider: {_provider}") # For visibility if logger is not configured

_initialize_provider()

def get_llm_provider() -> str:
    return _provider

def get_llm_model() -> str:
    return _model

def get_llm_client() -> AsyncOpenAI:
    return _client
