import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm_provider: str = os.getenv("LLM_PROVIDER", "")
    
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "")
    llm_model: str = os.getenv("LLM_MODEL", "openrouter/free")  # fallback for openrouter
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    max_message_length: int = int(os.getenv("MAX_MESSAGE_LENGTH", "4000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
