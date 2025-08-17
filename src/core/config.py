"""
Configuration management for the AI Strategic Co-pilot application.
Handles environment variables, LLM settings, and application configuration.
"""

import os
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application
    app_name: str = Field(default="AI Strategic Co-pilot")
    app_version: str = Field(default="2.0.0")
    debug: bool = Field(default=False)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")

    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_reload: bool = Field(default=False)

    # LLM Provider Configuration
    llm_provider: Literal["anthropic", "openai", "google"] = Field(default="anthropic")

    # API Keys
    anthropic_api_key: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)
    google_api_key: Optional[str] = Field(default=None)

    # LangSmith Tracing (matching .env file variables)
    langsmith_tracing: bool = Field(default=False, alias="LANGSMITH_TRACING")
    langsmith_endpoint: str = Field(default="https://api.smith.langchain.com", alias="LANGSMITH_ENDPOINT")
    langsmith_api_key: Optional[str] = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="strategy-coach", alias="LANGSMITH_PROJECT")

    # Agent Configuration
    default_model: str = Field(default="claude-3-sonnet-20240229")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, gt=0)

    # Session Management
    session_timeout_minutes: int = Field(default=60, gt=0)
    max_conversation_history: int = Field(default=100, gt=0)

    # Testing Configuration
    test_business_case_path: str = Field(
        default="testing/business-cases/business-case-for-testing.md"
    )
    playwright_headless: bool = Field(default=False)
    playwright_timeout: int = Field(default=30000, gt=0)

    # Development Features
    enable_cors: bool = Field(default=True)
    enable_websockets: bool = Field(default=True)
    enable_static_files: bool = Field(default=True)

    def get_llm_api_key(self) -> Optional[str]:
        """Get the API key for the configured LLM provider."""
        if self.llm_provider == "anthropic":
            return self.anthropic_api_key
        elif self.llm_provider == "openai":
            return self.openai_api_key
        elif self.llm_provider == "google":
            return self.google_api_key
        return None

    def setup_langsmith_tracing(self) -> None:
        """Configure LangSmith tracing environment variables."""
        if self.langsmith_tracing and self.langsmith_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_ENDPOINT"] = self.langsmith_endpoint
            os.environ["LANGCHAIN_API_KEY"] = self.langsmith_api_key
            os.environ["LANGCHAIN_PROJECT"] = self.langsmith_project
            print(f"✅ LangSmith tracing configured for project: {self.langsmith_project}")
            return True
        else:
            print(f"⚠️ LangSmith tracing not configured: tracing={self.langsmith_tracing}, api_key={'set' if self.langsmith_api_key else 'missing'}")
            return False

    def validate_configuration(self) -> list[str]:
        """Validate the configuration and return any errors."""
        errors = []

        # Check if LLM API key is available
        if not self.get_llm_api_key():
            errors.append(
                f"No API key configured for LLM provider: {self.llm_provider}"
            )

        # Check LangSmith configuration if tracing is enabled
        if self.langsmith_tracing and not self.langsmith_api_key:
            errors.append("LangSmith tracing enabled but no API key provided")

        return errors


# Global settings instance
settings = Settings()

# Configure LangSmith tracing on import
settings.setup_langsmith_tracing()
