# Mistral AI Integration Implementation Guide

## Task 8.0: Implement Mistral AI Integration for Multi-Model Support

This guide provides detailed implementation instructions based on official Mistral AI documentation.

## Prerequisites

### 1. API Key Setup
- Obtain API key from [Mistral AI Platform](https://console.mistral.ai/)
- Set environment variable: `MISTRAL_API_KEY`

### 2. Installation (Task 8.1)

```bash
# Basic installation
pip install mistralai

# With Poetry (if using)
poetry add mistralai

# For Azure deployment
pip install mistralai[azure]

# For GCP deployment  
pip install mistralai[gcp]
```

## Implementation Steps

### Task 8.2: Configuration Setup

Update `.env.example`:
```env
# Mistral AI Configuration
MISTRAL_API_KEY=your-mistral-api-key-here
```

Update `src/utils/config.py`:
```python
class Config(BaseModel):
    # Existing fields...
    
    # Mistral AI
    mistral_api_key: str = Field(None, env="MISTRAL_API_KEY")
    
    # Model configuration
    mistral_models: dict = Field(default={
        "mistral-large-latest": {"name": "Mistral Large", "context": 32000},
        "mistral-medium-latest": {"name": "Mistral Medium", "context": 32000},
        "mistral-small-latest": {"name": "Mistral Small", "context": 32000},
        "open-mixtral-8x7b": {"name": "Mixtral 8x7B", "context": 32000},
        "open-mixtral-8x22b": {"name": "Mixtral 8x22B", "context": 64000},
        "codestral-latest": {"name": "Codestral", "context": 32000},
        "mistral-embed": {"name": "Mistral Embed", "context": 8192}
    })
```

### Task 8.3-8.4: LLM Client Implementation

Update `src/utils/llm_client.py`:

```python
from mistralai import Mistral
from mistralai.models import ChatCompletionResponse
import os
from typing import Optional, List, Dict, Any

def _create_mistral_client(config: Config, model_name: str = None):
    """Create and configure Mistral AI client."""
    
    if not config.mistral_api_key:
        raise ValueError("Mistral API key not configured")
    
    # Initialize client
    client = Mistral(api_key=config.mistral_api_key)
    
    # Determine model
    if not model_name:
        model_name = "mistral-large-latest"  # Default to best model
    
    # Model validation
    available_models = list(config.mistral_models.keys())
    if model_name not in available_models:
        logger.warning(f"Model {model_name} not recognized, using mistral-large-latest")
        model_name = "mistral-large-latest"
    
    logger.info(f"Initialized Mistral client with model: {model_name}")
    
    class MistralWrapper:
        """Wrapper to match LangChain interface."""
        
        def __init__(self, client: Mistral, model: str):
            self.client = client
            self.model = model
            
        def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
            """Synchronous chat completion."""
            try:
                # Convert messages to Mistral format
                mistral_messages = []
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    
                    # Map roles if needed
                    if role == "human":
                        role = "user"
                    elif role == "ai":
                        role = "assistant"
                    
                    mistral_messages.append({
                        "role": role,
                        "content": content
                    })
                
                # Make API call
                response = self.client.chat.complete(
                    model=self.model,
                    messages=mistral_messages,
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", 4000),
                    top_p=kwargs.get("top_p", 1.0)
                )
                
                # Extract response
                if response and response.choices:
                    return response.choices[0].message.content
                return ""
                
            except Exception as e:
                logger.error(f"Mistral API error: {e}")
                raise
        
        async def ainvoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
            """Async chat completion - Mistral doesn't have native async."""
            # For now, use sync version
            return self.invoke(messages, **kwargs)
        
        def stream(self, messages: List[Dict[str, str]], **kwargs):
            """Streaming chat completion."""
            try:
                mistral_messages = []
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    
                    if role == "human":
                        role = "user"
                    elif role == "ai":
                        role = "assistant"
                    
                    mistral_messages.append({
                        "role": role,
                        "content": content
                    })
                
                # Stream response
                response = self.client.chat.stream(
                    model=self.model,
                    messages=mistral_messages,
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", 4000)
                )
                
                # Yield chunks
                with response as event_stream:
                    for event in event_stream:
                        if event.data and event.data.choices:
                            chunk = event.data.choices[0].delta.content
                            if chunk:
                                yield chunk
                                
            except Exception as e:
                logger.error(f"Mistral streaming error: {e}")
                raise
    
    return MistralWrapper(client, model_name)
```

### Task 8.5: Prompt Optimization for Mistral

Update prompt templates for Mistral's instruction format:

```python
# In src/utils/prompts.py

MISTRAL_SYSTEM_PROMPT = """You are an AI Strategic Coach powered by Mistral AI.
Your responses should be clear, structured, and actionable.
Focus on providing strategic insights and guidance."""

def format_prompt_for_mistral(base_prompt: str, context: Dict[str, Any]) -> str:
    """Format prompts optimized for Mistral models."""
    
    # Mistral responds well to structured prompts
    formatted = f"""<context>
{context.get('conversation_history', '')}
</context>

<task>
{base_prompt}
</task>

<instructions>
- Provide clear, actionable guidance
- Use structured formatting when appropriate
- Focus on strategic insights
- Be concise but comprehensive
</instructions>

Response:"""
    
    return formatted
```

### Task 8.6: Rate Limiting and Error Handling

```python
from typing import Optional
import time
import random

class MistralRateLimiter:
    """Rate limiter for Mistral API."""
    
    def __init__(self):
        self.last_request_time = 0
        self.min_interval = 0.1  # 100ms between requests
        
    def wait_if_needed(self):
        """Implement exponential backoff."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

def handle_mistral_error(func):
    """Decorator for Mistral API error handling."""
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_message = str(e)
                
                # Handle specific Mistral errors
                if "rate_limit" in error_message.lower():
                    wait_time = (2 ** retry_count) + random.uniform(0, 1)
                    logger.warning(f"Rate limit hit, waiting {wait_time}s")
                    time.sleep(wait_time)
                    retry_count += 1
                    
                elif "model_not_found" in error_message.lower():
                    logger.error(f"Model not found: {error_message}")
                    raise ValueError(f"Invalid Mistral model specified")
                    
                elif "unauthorized" in error_message.lower():
                    logger.error("Invalid Mistral API key")
                    raise ValueError("Mistral API authentication failed")
                    
                else:
                    logger.error(f"Mistral API error: {error_message}")
                    raise
                    
        raise Exception(f"Max retries ({max_retries}) exceeded for Mistral API")
    
    return wrapper
```

### Task 8.7: Provider Priority Integration

Update the main LLM client creation logic:

```python
def create_llm_client(config: Config = None, model_name: str = None):
    """Create LLM client with Mistral in provider chain."""
    
    if config is None:
        config = get_config()
    
    # Provider priority order
    providers = [
        ("anthropic", config.anthropic_api_key, _create_anthropic_client),
        ("mistral", config.mistral_api_key, _create_mistral_client),  # Add Mistral
        ("openai", config.openai_api_key, _create_openai_client),
        ("google", config.google_api_key, _create_google_client),
    ]
    
    # Check default provider first
    if config.default_llm_provider == "mistral" and config.mistral_api_key:
        logger.info("Using Mistral as default provider")
        return _create_mistral_client(config, model_name or config.default_model)
    
    # Fallback chain
    for provider_name, api_key, creator_func in providers:
        if api_key:
            logger.info(f"Using {provider_name} as provider")
            return creator_func(config, model_name)
    
    raise ValueError("No LLM provider configured")
```

### Task 8.8-8.9: Agent Testing

Create test file `tests/test_mistral_integration.py`:

```python
import pytest
from src.utils.llm_client import create_llm_client
from src.agents.why_agent import WhyAgent
from src.agents.logic_agent import LogicAgent
from src.agents.analogy_agent import AnalogyAgent
from src.agents.open_strategy_agent import OpenStrategyAgent

@pytest.fixture
def mistral_client():
    """Create Mistral client for testing."""
    return create_llm_client(model_name="mistral-large-latest")

def test_mistral_why_agent(mistral_client):
    """Test WHY agent with Mistral."""
    agent = WhyAgent(llm_client=mistral_client)
    
    response = agent.process_user_input(
        "We want to implement DevOps practices",
        session_id="test-session"
    )
    
    assert response is not None
    assert "questions" in response or "topics" in response

def test_mistral_logic_agent(mistral_client):
    """Test Logic agent with Mistral."""
    agent = LogicAgent(llm_client=mistral_client)
    
    response = agent.process_user_input(
        "Our strategy is to increase revenue by cutting costs",
        session_id="test-session"
    )
    
    assert response is not None
    assert len(response.get("topics", [])) > 0

def test_mistral_conversation_quality():
    """Test conversation quality with different Mistral models."""
    models = ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"]
    
    for model in models:
        client = create_llm_client(model_name=model)
        
        # Test strategic reasoning
        response = client.invoke([{
            "role": "user",
            "content": "What are the key considerations for digital transformation?"
        }])
        
        assert len(response) > 100  # Ensure substantive response
        print(f"Model {model}: {len(response)} chars")
```

### Task 8.10-8.11: Cost Tracking and Model Selection

```python
class MistralCostTracker:
    """Track Mistral API usage and costs."""
    
    # Pricing per 1M tokens (example rates)
    PRICING = {
        "mistral-large-latest": {"input": 4.0, "output": 12.0},
        "mistral-medium-latest": {"input": 2.7, "output": 8.1},
        "mistral-small-latest": {"input": 0.2, "output": 0.6},
        "open-mixtral-8x7b": {"input": 0.7, "output": 0.7},
        "open-mixtral-8x22b": {"input": 2.0, "output": 6.0}
    }
    
    def __init__(self):
        self.usage = {}
        
    def track_usage(self, model: str, input_tokens: int, output_tokens: int):
        """Track token usage."""
        if model not in self.usage:
            self.usage[model] = {"input": 0, "output": 0, "calls": 0}
        
        self.usage[model]["input"] += input_tokens
        self.usage[model]["output"] += output_tokens
        self.usage[model]["calls"] += 1
        
    def get_cost_estimate(self) -> float:
        """Calculate estimated cost."""
        total_cost = 0.0
        
        for model, usage in self.usage.items():
            if model in self.PRICING:
                input_cost = (usage["input"] / 1_000_000) * self.PRICING[model]["input"]
                output_cost = (usage["output"] / 1_000_000) * self.PRICING[model]["output"]
                total_cost += input_cost + output_cost
                
        return total_cost

def select_mistral_model_by_complexity(task_type: str, phase: str) -> str:
    """Select appropriate Mistral model based on task complexity."""
    
    # High complexity tasks
    if task_type in ["strategic_reasoning", "complex_analysis"] or phase == "why":
        return "mistral-large-latest"
    
    # Medium complexity
    elif task_type in ["logic_validation", "pattern_matching"] or phase == "how":
        return "mistral-medium-latest"
    
    # Low complexity
    elif task_type in ["simple_qa", "summarization"] or phase == "what":
        return "mistral-small-latest"
    
    # Code-related tasks
    elif task_type == "code_generation":
        return "codestral-latest"
    
    # Default
    return "mistral-medium-latest"
```

### Task 8.12: Documentation Updates

Update `CLAUDE.md`:
```markdown
## Environment Variables

```env
# LLM Providers (at least one required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
MISTRAL_API_KEY=your-mistral-key  # NEW: Mistral AI support

# Provider Selection
DEFAULT_LLM_PROVIDER=mistral  # Options: openai, anthropic, google, mistral
DEFAULT_MODEL=mistral-large-latest  # Mistral models available
```

## Mistral AI Integration

The application now supports Mistral AI models:

- **Mistral Large**: Best performance for complex strategic reasoning
- **Mistral Medium**: Balanced performance and cost
- **Mistral Small**: Efficient for simple tasks
- **Mixtral 8x7B/8x22B**: Open-weight mixture of experts models
- **Codestral**: Specialized for code generation

### Configuration
1. Get API key from [console.mistral.ai](https://console.mistral.ai/)
2. Set `MISTRAL_API_KEY` in `.env`
3. Optionally set `DEFAULT_LLM_PROVIDER=mistral`
```

### Task 8.13-8.15: Testing and Validation

```python
# tests/test_mistral_comparison.py

def test_provider_comparison():
    """Compare Mistral with other providers."""
    
    prompt = "What are three key factors for successful digital transformation?"
    
    providers = {
        "mistral": "mistral-large-latest",
        "anthropic": "claude-3-5-haiku-20241022",
        "openai": "gpt-4",
    }
    
    results = {}
    
    for provider, model in providers.items():
        try:
            client = create_llm_client(model_name=model)
            start_time = time.time()
            
            response = client.invoke([{
                "role": "user",
                "content": prompt
            }])
            
            elapsed = time.time() - start_time
            
            results[provider] = {
                "response_length": len(response),
                "response_time": elapsed,
                "quality_score": assess_response_quality(response)
            }
            
        except Exception as e:
            results[provider] = {"error": str(e)}
    
    # Compare results
    print("Provider Comparison Results:")
    for provider, metrics in results.items():
        print(f"{provider}: {metrics}")

def test_phase_based_model_switching():
    """Test dynamic model switching based on phase."""
    
    session_state = {"phase": "why", "completeness": 0.2}
    
    # Should use large model for WHY phase
    model = select_mistral_model_by_complexity(
        task_type="strategic_reasoning",
        phase=session_state["phase"]
    )
    assert model == "mistral-large-latest"
    
    # Switch to medium for HOW phase
    session_state["phase"] = "how"
    model = select_mistral_model_by_complexity(
        task_type="pattern_matching",
        phase=session_state["phase"]
    )
    assert model == "mistral-medium-latest"
    
    # Use small for simple WHAT phase tasks
    session_state["phase"] = "what"
    model = select_mistral_model_by_complexity(
        task_type="summarization",
        phase=session_state["phase"]
    )
    assert model == "mistral-small-latest"
```

## Testing Commands

```bash
# Install Mistral SDK
pip install mistralai

# Run Mistral-specific tests
pytest tests/test_mistral_integration.py -v

# Test all agents with Mistral
pytest tests/agents/ --mistral-only -v

# Compare providers
python tests/test_mistral_comparison.py

# Full integration test
pytest tests/api/test_conversation_flow.py --provider=mistral
```

## Deployment Considerations

1. **API Key Security**: Never commit API keys
2. **Rate Limits**: Mistral has generous rate limits but implement backoff
3. **Cost Management**: Monitor usage with cost tracker
4. **Model Selection**: Use appropriate model for task complexity
5. **Error Handling**: Graceful fallback to other providers if needed

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify API key is correct
   - Check key has proper permissions

2. **Model Not Found**
   - Ensure model name is exact (e.g., "mistral-large-latest")
   - Check model availability in your region

3. **Rate Limiting**
   - Implement exponential backoff
   - Consider using multiple API keys

4. **Response Quality**
   - Use mistral-large for complex reasoning
   - Optimize prompts for Mistral's format

## Benefits Achieved

✅ **Multi-provider flexibility**: Users can choose based on needs
✅ **Cost optimization**: Different models for different complexity
✅ **European compliance**: Data sovereignty options
✅ **Open-weight options**: Potential for self-hosting
✅ **Improved redundancy**: Fallback options if primary provider fails