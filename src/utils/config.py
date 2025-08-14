import os
from typing import Optional
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # API Keys
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, alias="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(None, alias="GOOGLE_API_KEY")
    
    # Application Configuration
    app_name: str = Field("AI Strategic Co-pilot", alias="APP_NAME")
    app_version: str = Field("0.1.0", alias="APP_VERSION")
    debug: bool = Field(False, alias="DEBUG")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    
    # Server Configuration
    host: str = Field("0.0.0.0", alias="HOST")
    port: int = Field(8000, alias="PORT")
    reload: bool = Field(True, alias="RELOAD")
    
    # Session Management
    session_timeout_minutes: int = Field(60, alias="SESSION_TIMEOUT_MINUTES")
    max_sessions: int = Field(1000, alias="MAX_SESSIONS")
    
    # File Storage
    strategy_maps_dir: str = Field("data/sessions", alias="STRATEGY_MAPS_DIR")
    logs_dir: str = Field("logs", alias="LOGS_DIR")
    data_directory: str = Field("data", alias="DATA_DIRECTORY")
    
    # CORS Configuration
    cors_origins: list = Field([
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081"
    ], alias="CORS_ORIGINS")
    
    # LangSmith Configuration
    langchain_tracing_v2: bool = Field(False, alias="LANGCHAIN_TRACING_V2")
    langchain_project: str = Field("strategy-coach", alias="LANGCHAIN_PROJECT")
    langsmith_api_key: Optional[str] = Field(None, alias="LANGSMITH_API_KEY")
    
    # Agent Configuration
    default_llm_provider: str = Field("openai", alias="DEFAULT_LLM_PROVIDER")
    default_model: str = Field("gpt-4", alias="DEFAULT_MODEL")
    default_temperature: float = Field(0.7, alias="DEFAULT_TEMPERATURE")
    max_tokens: int = Field(4000, alias="MAX_TOKENS")
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(60, alias="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_requests_per_hour: int = Field(1000, alias="RATE_LIMIT_REQUESTS_PER_HOUR")
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    def validate_api_keys(self) -> None:
        """Validate that at least one API key is provided."""
        if not self.openai_api_key and not self.anthropic_api_key and not self.google_api_key:
            raise ValueError(
                "At least one API key must be provided (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY)"
            )
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration based on the default provider."""
        config = {
            "temperature": self.default_temperature,
            "max_tokens": self.max_tokens,
        }
        
        if self.default_llm_provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OpenAI API key is required for OpenAI provider")
            config.update({
                "model": self.default_model,
                "api_key": self.openai_api_key,
            })
        elif self.default_llm_provider == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError("Anthropic API key is required for Anthropic provider")
            config.update({
                "model": self.default_model,
                "api_key": self.anthropic_api_key,
            })
        elif self.default_llm_provider == "google":
            if not self.google_api_key:
                raise ValueError("Google API key is required for Google provider")
            config.update({
                "model": "gemini-pro" if self.default_model == "gpt-4" else self.default_model,
                "api_key": self.google_api_key,
            })
        else:
            raise ValueError(f"Unsupported LLM provider: {self.default_llm_provider}")
        
        return config


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def get_config() -> Settings:
    """Get the global configuration instance (alias for get_settings)."""
    return settings


def setup_environment() -> None:
    """Setup environment variables for LangChain and other services."""
    # Set LangChain environment variables if configured
    if settings.langchain_tracing_v2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
        if settings.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    
    # Set API keys in environment for LangChain integrations
    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    if settings.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key