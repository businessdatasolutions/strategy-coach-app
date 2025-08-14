"""
LLM Client utility for the Strategy Coach application.

Provides a centralized interface for LLM interactions with configuration
management, error handling, and retry logic.
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from functools import lru_cache

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from .config import get_config
from . import get_logger


logger = get_logger(__name__)


class LLMClientError(Exception):
    """Custom exception for LLM client errors."""
    pass


@lru_cache(maxsize=1)
def get_llm_client(model_name: Optional[str] = None) -> BaseChatModel:
    """
    Get an LLM client instance with configuration.
    
    Args:
        model_name: Optional model name override
        
    Returns:
        Configured LLM client instance
        
    Raises:
        LLMClientError: If client cannot be initialized
    """
    try:
        config = get_config()
        
        # Determine which LLM provider to use
        provider = model_name or config.default_llm_provider
        
        if provider == "google" or provider.startswith("gemini"):
            return _create_google_client(config, model_name)
        elif provider == "openai" or provider.startswith("gpt"):
            return _create_openai_client(config, model_name)
        elif provider == "anthropic" or provider.startswith("claude"):
            return _create_anthropic_client(config, model_name)
        else:
            # Try to use Anthropic first, then OpenAI, then Google
            if config.anthropic_api_key:
                logger.info("Using Anthropic as default provider")
                return _create_anthropic_client(config, model_name)
            elif config.openai_api_key:
                logger.info("Using OpenAI as default provider")
                return _create_openai_client(config, model_name)
            elif config.google_api_key:
                logger.info("Using Google Gemini as default provider")
                return _create_google_client(config, model_name)
            else:
                raise LLMClientError("No LLM API keys configured")
    
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {str(e)}")
        raise LLMClientError(f"LLM client initialization failed: {str(e)}")


def _create_openai_client(config: Any, model_name: Optional[str] = None) -> ChatOpenAI:
    """Create OpenAI client with configuration."""
    
    # Get API key from environment or config
    api_key = os.getenv("OPENAI_API_KEY") or config.openai_api_key
    
    if not api_key:
        raise LLMClientError("OpenAI API key not found in environment or config")
    
    # Determine model
    model = model_name or config.default_model
    
    # Create client with configuration
    client_params = {
        "model": model,
        "temperature": config.default_temperature,
        "max_tokens": config.max_tokens,
        "api_key": api_key
    }
    
    logger.info(f"Initializing OpenAI client with model: {model}")
    return ChatOpenAI(**client_params)


def _create_anthropic_client(config: Any, model_name: Optional[str] = None) -> ChatAnthropic:
    """Create Anthropic client with configuration."""
    
    # Get API key from environment or config
    api_key = os.getenv("ANTHROPIC_API_KEY") or config.anthropic_api_key
    
    if not api_key:
        raise LLMClientError("Anthropic API key not found in environment or config")
    
    # Determine model
    model = model_name or config.default_model
    if model.startswith("gpt"):  # If default is OpenAI model, use Claude instead
        model = "claude-3-5-haiku-20241022"
    elif not model.startswith("claude"):  # Ensure we're using a Claude model
        model = "claude-3-5-haiku-20241022"
    
    # Create client with configuration
    client_params = {
        "model": model,
        "temperature": config.default_temperature,
        "max_tokens": config.max_tokens,
        "api_key": api_key
    }
    
    logger.info(f"Initializing Anthropic client with model: {model}")
    return ChatAnthropic(**client_params)


def _create_google_client(config: Any, model_name: Optional[str] = None) -> ChatGoogleGenerativeAI:
    """Create Google Gemini client with configuration."""
    
    # Get API key from environment or config
    api_key = os.getenv("GOOGLE_API_KEY") or config.google_api_key
    
    if not api_key:
        raise LLMClientError("Google API key not found in environment or config")
    
    # Determine model
    model = model_name or config.default_model or "gemini-2.0-flash-exp"
    if model.startswith("gpt"):
        model = "gemini-2.0-flash-exp"  # Use latest Gemini model as fallback
    
    # Create client with configuration
    client_params = {
        "model": model,
        "temperature": config.default_temperature,
        "max_output_tokens": config.max_tokens,
        "google_api_key": api_key,
        "convert_system_message_to_human": True  # Gemini doesn't support system messages directly
    }
    
    logger.info(f"Initializing Google Gemini client with model: {model}")
    return ChatGoogleGenerativeAI(**client_params)


class LLMClientWrapper:
    """
    Wrapper class for LLM clients with enhanced error handling and retry logic.
    """
    
    def __init__(self, client: BaseChatModel, max_retries: int = 3):
        """
        Initialize the wrapper.
        
        Args:
            client: The underlying LLM client
            max_retries: Maximum number of retries for failed requests
        """
        self.client = client
        self.max_retries = max_retries
        self.logger = get_logger(self.__class__.__name__)
    
    def invoke(self, prompt: Union[str, BaseMessage], **kwargs) -> Any:
        """
        Invoke the LLM with retry logic and error handling.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for the LLM
            
        Returns:
            LLM response
            
        Raises:
            LLMClientError: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    self.logger.info(f"Retrying LLM request (attempt {attempt + 1}/{self.max_retries + 1})")
                
                response = self.client.invoke(prompt, **kwargs)
                
                if attempt > 0:
                    self.logger.info("LLM request succeeded after retry")
                
                return response
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"LLM request failed (attempt {attempt + 1}): {str(e)}")
                
                if attempt == self.max_retries:
                    break
                
                # Add exponential backoff for retries
                import time
                time.sleep(2 ** attempt)
        
        error_msg = f"LLM request failed after {self.max_retries + 1} attempts: {str(last_error)}"
        self.logger.error(error_msg)
        raise LLMClientError(error_msg)
    
    async def ainvoke(self, prompt: Union[str, BaseMessage], **kwargs) -> Any:
        """
        Async version of invoke with retry logic.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for the LLM
            
        Returns:
            LLM response
            
        Raises:
            LLMClientError: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    self.logger.info(f"Retrying async LLM request (attempt {attempt + 1}/{self.max_retries + 1})")
                
                response = await self.client.ainvoke(prompt, **kwargs)
                
                if attempt > 0:
                    self.logger.info("Async LLM request succeeded after retry")
                
                return response
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"Async LLM request failed (attempt {attempt + 1}): {str(e)}")
                
                if attempt == self.max_retries:
                    break
                
                # Add exponential backoff for retries
                import asyncio
                await asyncio.sleep(2 ** attempt)
        
        error_msg = f"Async LLM request failed after {self.max_retries + 1} attempts: {str(last_error)}"
        self.logger.error(error_msg)
        raise LLMClientError(error_msg)


def get_enhanced_llm_client(model_name: Optional[str] = None, max_retries: int = 3) -> LLMClientWrapper:
    """
    Get an enhanced LLM client with retry logic and error handling.
    
    Args:
        model_name: Optional model name override
        max_retries: Maximum number of retries for failed requests
        
    Returns:
        Enhanced LLM client wrapper
    """
    base_client = get_llm_client(model_name)
    return LLMClientWrapper(base_client, max_retries)


def test_llm_connection(model_name: Optional[str] = None) -> bool:
    """
    Test the LLM connection with a simple request.
    
    Args:
        model_name: Optional model name to test
        
    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = get_llm_client(model_name)
        response = client.invoke("Hello, this is a connection test.")
        
        if response and hasattr(response, 'content'):
            logger.info("LLM connection test successful")
            return True
        else:
            logger.warning("LLM connection test returned unexpected response")
            return False
            
    except Exception as e:
        logger.error(f"LLM connection test failed: {str(e)}")
        return False


# Export main functions
__all__ = [
    "get_llm_client",
    "get_enhanced_llm_client", 
    "LLMClientWrapper",
    "LLMClientError",
    "test_llm_connection"
]