# AI Strategic Co-pilot 🚀

An AI-powered strategic co-pilot that guides business leaders through a rigorous, Socratic process of developing, refining, and testing their organizational strategy using a multi-agent workflow system.

**Status**: Production Ready | **Version**: 1.0 | **Default Model**: Claude Sonnet 4.0

## Features

✨ **Multi-Agent Strategic Coaching**
- WHY Agent: Simon Sinek's Golden Circle methodology
- Analogy Agent: Carroll & Sørensen's analogical reasoning
- Logic Agent: Deductive argument validation
- Open Strategy Agent: Implementation planning

🎯 **Research-Backed Methodologies**
- Purpose discovery through introspective questioning
- Pattern matching with successful strategies
- Logical consistency validation
- Stakeholder engagement planning

🚀 **Modern Tech Stack**
- FastAPI for high-performance API
- LangGraph for agent orchestration
- Support for multiple LLM providers
- Real-time conversation streaming
- Interactive web UI with progress tracking

## Overview

This system leverages specialized AI agents managed by a central orchestrator to engage users in structured dialogue. Each agent uses distinct, research-backed methodologies to challenge thinking on different facets of strategy development.

## Architecture

The system uses an Orchestrator-Worker model built with LangGraph:
- **Orchestrator Agent**: Central controller managing conversation flow
- **Strategy Map Agent**: Persistent state manager with JSON persistence
- **Specialist Agents**: WHY, Analogy, Logic, and Open Strategy agents

## Setup

### Prerequisites
- Python 3.10 or higher
- One of the following API keys:
  - Anthropic API key (recommended for Claude Sonnet 4.0)
  - OpenAI API key (GPT-4 support)
  - Google Gemini API key (Gemini 2.0 support)
  - Mistral API key (coming soon)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd strategy-coach-app-v1
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

Configure your preferred LLM provider in `.env`:
```env
# Recommended configuration
ANTHROPIC_API_KEY=your-key-here
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_MODEL=claude-sonnet-4-20250514

# Alternative providers
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
MISTRAL_API_KEY=your-mistral-key  # Coming soon
```

The system will automatically detect and use the available API key.

### Running the Application

1. **Start the API server:**
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start the Web UI (in a separate terminal):**
```bash
cd web
python3 -m http.server 8081
```

3. **Access the application:**
- Web UI: `http://localhost:8081`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src/ tests/
ruff check src/ tests/
```

### Type Checking
```bash
mypy src/
```

## API Endpoints

- `POST /conversation/start` - Initialize a new strategy session
- `POST /conversation/message` - Send a message in the conversation
- `GET /conversation/export/{session_id}` - Export the strategy map JSON

## Project Structure

```
strategy-coach-app-v1/
├── src/
│   ├── agents/           # Specialist agent implementations
│   ├── api/              # FastAPI application
│   ├── models/           # Data models and state definitions
│   └── utils/            # Utility functions
├── tests/                # Test suite
├── agents/               # Agent documentation
└── .claude/              # Project management files
```

## License

[Your License Here]