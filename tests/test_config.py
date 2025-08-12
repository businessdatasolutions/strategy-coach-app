import pytest
import os
from unittest.mock import patch, MagicMock

from src.utils.config import Settings, get_settings, setup_environment


class TestSettings:
    """Test the Settings configuration class."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        # Clear environment variables for this test
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            assert settings.app_name == "AI Strategic Co-pilot"
            assert settings.app_version == "0.1.0"
            assert settings.debug is False
            assert settings.log_level == "INFO"
            assert settings.host == "0.0.0.0"
            assert settings.port == 8000
            assert settings.session_timeout_minutes == 60
            assert settings.max_sessions == 1000
            assert settings.strategy_maps_dir == "data/sessions"
            assert settings.logs_dir == "logs"
            assert settings.default_llm_provider == "openai"
            assert settings.default_model == "gpt-4"
            assert settings.default_temperature == 0.7
            assert settings.max_tokens == 4000
    
    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        with patch.dict(os.environ, {
            "APP_NAME": "Test App",
            "DEBUG": "true",
            "PORT": "9000",
            "DEFAULT_TEMPERATURE": "0.5"
        }):
            settings = Settings()
            
            assert settings.app_name == "Test App"
            assert settings.debug is True
            assert settings.port == 9000
            assert settings.default_temperature == 0.5
    
    def test_api_key_validation_no_keys(self):
        """Test validation fails when no API keys are provided."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            with pytest.raises(ValueError, match="At least one API key must be provided"):
                settings.validate_api_keys()
    
    def test_api_key_validation_openai_only(self):
        """Test validation passes with only OpenAI key."""
        settings = Settings(openai_api_key="test_key")
        
        # Should not raise an exception
        settings.validate_api_keys()
    
    def test_api_key_validation_anthropic_only(self):
        """Test validation passes with only Anthropic key."""
        settings = Settings(anthropic_api_key="test_key")
        
        # Should not raise an exception
        settings.validate_api_keys()
    
    def test_api_key_validation_both_keys(self):
        """Test validation passes with both keys."""
        settings = Settings(
            openai_api_key="openai_key",
            anthropic_api_key="anthropic_key"
        )
        
        # Should not raise an exception
        settings.validate_api_keys()
    
    def test_get_llm_config_openai(self):
        """Test LLM configuration for OpenAI provider."""
        settings = Settings(
            openai_api_key="test_openai_key",
            default_llm_provider="openai",
            default_model="gpt-4",
            default_temperature=0.8,
            max_tokens=2000
        )
        
        config = settings.get_llm_config()
        
        assert config["model"] == "gpt-4"
        assert config["api_key"] == "test_openai_key"
        assert config["temperature"] == 0.8
        assert config["max_tokens"] == 2000
    
    def test_get_llm_config_anthropic(self):
        """Test LLM configuration for Anthropic provider."""
        settings = Settings(
            anthropic_api_key="test_anthropic_key",
            default_llm_provider="anthropic",
            default_model="claude-3-sonnet-20240229",
            default_temperature=0.6,
            max_tokens=3000
        )
        
        config = settings.get_llm_config()
        
        assert config["model"] == "claude-3-sonnet-20240229"
        assert config["api_key"] == "test_anthropic_key"
        assert config["temperature"] == 0.6
        assert config["max_tokens"] == 3000
    
    def test_get_llm_config_openai_no_key(self):
        """Test LLM configuration fails for OpenAI without key."""
        settings = Settings(default_llm_provider="openai")
        
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            settings.get_llm_config()
    
    def test_get_llm_config_anthropic_no_key(self):
        """Test LLM configuration fails for Anthropic without key."""
        settings = Settings(default_llm_provider="anthropic")
        
        with pytest.raises(ValueError, match="Anthropic API key is required"):
            settings.get_llm_config()
    
    def test_get_llm_config_unsupported_provider(self):
        """Test LLM configuration fails for unsupported provider."""
        settings = Settings(
            openai_api_key="test_key",
            default_llm_provider="unsupported"
        )
        
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            settings.get_llm_config()


class TestConfigurationFunctions:
    """Test configuration utility functions."""
    
    def test_get_settings(self):
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)
    
    def test_setup_environment_with_tracing(self):
        """Test environment setup with LangChain tracing enabled."""
        settings = Settings(
            openai_api_key="test_openai_key",
            anthropic_api_key="test_anthropic_key",
            langchain_tracing_v2=True,
            langchain_project="test_project",
            langsmith_api_key="test_langsmith_key"
        )
        
        with patch("src.utils.config.settings", settings):
            setup_environment()
            
            assert os.environ.get("LANGCHAIN_TRACING_V2") == "true"
            assert os.environ.get("LANGCHAIN_PROJECT") == "test_project"
            assert os.environ.get("LANGSMITH_API_KEY") == "test_langsmith_key"
            assert os.environ.get("OPENAI_API_KEY") == "test_openai_key"
            assert os.environ.get("ANTHROPIC_API_KEY") == "test_anthropic_key"
    
    def test_setup_environment_without_tracing(self):
        """Test environment setup without LangChain tracing."""
        settings = Settings(
            openai_api_key="test_openai_key",
            anthropic_api_key="test_anthropic_key",
            langchain_tracing_v2=False
        )
        
        with patch("src.utils.config.settings", settings):
            # Clear environment first
            for key in ["LANGCHAIN_TRACING_V2", "LANGCHAIN_PROJECT", "LANGSMITH_API_KEY"]:
                os.environ.pop(key, None)
            
            setup_environment()
            
            # Tracing should not be set
            assert os.environ.get("LANGCHAIN_TRACING_V2") != "true"
            # But API keys should still be set
            assert os.environ.get("OPENAI_API_KEY") == "test_openai_key"
            assert os.environ.get("ANTHROPIC_API_KEY") == "test_anthropic_key"