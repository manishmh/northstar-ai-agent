import pytest
from openai import AsyncOpenAI
from app.config import settings

@pytest.mark.asyncio
async def test_openrouter_connection():
    if not settings.openrouter_api_key or settings.openrouter_api_key == "dummy-key":
        pytest.skip("No valid OpenRouter API key provided.")
        
    client = AsyncOpenAI(
        base_url=settings.openrouter_base_url or "https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key
    )
    
    try:
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": "Hello. Just say hi and nothing else."}]
        )
        assert response.choices[0].message is not None
    except Exception as e:
        pytest.fail(f"LLM Connection failed: {e}")
