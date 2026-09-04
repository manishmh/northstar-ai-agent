import pytest
import os
from unittest import mock
import importlib

@pytest.fixture
def clean_llm_module():
    # Reload llm module with mocked settings
    with mock.patch.dict(os.environ, {}, clear=True):
        yield

def reload_llm_with_settings(llm_provider="", openai_key="", openai_model="gpt-4o-mini", 
                            openrouter_key="", openrouter_model="openrouter/free",
                            groq_key="", groq_model="openai/gpt-oss-20b"):
    from app import config
    from app import llm
    
    config.settings.llm_provider = llm_provider
    config.settings.openai_api_key = openai_key
    config.settings.openai_model = openai_model
    config.settings.openrouter_api_key = openrouter_key
    config.settings.openrouter_model = openrouter_model
    config.settings.llm_model = "openrouter/free"
    
    config.settings.groq_api_key = groq_key
    config.settings.groq_model = groq_model
    config.settings.groq_base_url = "https://api.groq.com/openai/v1"
    
    # Reload module to trigger _initialize_provider
    importlib.reload(llm)
    return llm

def test_groq_provider(clean_llm_module):
    llm = reload_llm_with_settings(llm_provider="groq", groq_key="gsk-test")
    assert llm.get_llm_provider() == "groq"
    assert llm.get_llm_model() == "openai/gpt-oss-20b"
    client = llm.get_llm_client()
    assert client.api_key == "gsk-test"
    assert str(client.base_url) == "https://api.groq.com/openai/v1/"

def test_groq_provider_missing_key(clean_llm_module):
    with pytest.raises(ValueError, match="LLM_PROVIDER is set to 'groq' but GROQ_API_KEY is missing"):
        reload_llm_with_settings(llm_provider="groq", groq_key="")

def test_openai_provider(clean_llm_module):
    llm = reload_llm_with_settings(llm_provider="openai", openai_key="sk-test-openai")
    assert llm.get_llm_provider() == "openai"
    assert llm.get_llm_model() == "gpt-4o-mini"
    client = llm.get_llm_client()
    assert client.api_key == "sk-test-openai"

def test_openrouter_provider(clean_llm_module):
    llm = reload_llm_with_settings(llm_provider="openrouter", openrouter_key="sk-or-test")
    assert llm.get_llm_provider() == "openrouter"
    assert llm.get_llm_model() == "openrouter/free"
    client = llm.get_llm_client()
    assert client.api_key == "sk-or-test"
    assert str(client.base_url) == "https://openrouter.ai/api/v1/"

def test_implicit_openai(clean_llm_module):
    # Backward compatibility tests
    llm = reload_llm_with_settings(openai_key="sk-test-openai")
    assert llm.get_llm_provider() == "openai"

def test_implicit_openrouter(clean_llm_module):
    # Backward compatibility tests
    llm = reload_llm_with_settings(openrouter_key="sk-or-test")
    assert llm.get_llm_provider() == "openrouter"

def test_neither_key_raises_error(clean_llm_module):
    with pytest.raises(ValueError, match="Configuration Error: No valid LLM provider configured"):
        reload_llm_with_settings()
