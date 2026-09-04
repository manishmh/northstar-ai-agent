import pytest
import os
from unittest import mock
import importlib

@pytest.fixture
def clean_llm_module():
    # Reload llm module with mocked settings
    with mock.patch.dict(os.environ, {}, clear=True):
        yield

def reload_llm_with_settings(openai_key="", openai_model="gpt-4o-mini", 
                            openrouter_key="", openrouter_model="openrouter/free"):
    from app import config
    from app import llm
    
    config.settings.openai_api_key = openai_key
    config.settings.openai_model = openai_model
    config.settings.openrouter_api_key = openrouter_key
    config.settings.openrouter_model = openrouter_model
    config.settings.llm_model = "openrouter/free"
    
    # Reload module to trigger _initialize_provider
    importlib.reload(llm)
    return llm

def test_openai_only(clean_llm_module):
    llm = reload_llm_with_settings(openai_key="sk-test-openai")
    
    assert llm.get_llm_provider() == "openai"
    assert llm.get_llm_model() == "gpt-4o-mini"
    client = llm.get_llm_client()
    assert client.api_key == "sk-test-openai"

def test_openrouter_only(clean_llm_module):
    llm = reload_llm_with_settings(openrouter_key="sk-or-test")
    
    assert llm.get_llm_provider() == "openrouter"
    assert llm.get_llm_model() == "openrouter/free"
    client = llm.get_llm_client()
    assert client.api_key == "sk-or-test"
    assert str(client.base_url) == "https://openrouter.ai/api/v1/"

def test_both_keys_prefers_openai(clean_llm_module):
    llm = reload_llm_with_settings(openai_key="sk-test-openai", openrouter_key="sk-or-test")
    
    assert llm.get_llm_provider() == "openai"
    assert llm.get_llm_model() == "gpt-4o-mini"
    client = llm.get_llm_client()
    assert client.api_key == "sk-test-openai"

def test_neither_key_raises_error(clean_llm_module):
    with pytest.raises(ValueError, match="Configuration Error"):
        reload_llm_with_settings(openai_key="", openrouter_key="")
