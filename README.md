# AI Strategic Co-pilot

An AI-powered strategic co-pilot that guides business leaders through a rigorous, Socratic process of developing, refining, and testing their organizational strategy using a multi-agent workflow system.

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
  - Google Gemini API key (recommended)
  - OpenAI API key
  - Anthropic API key

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

Available LLM providers:
- **Google Gemini** (Recommended): Set `GOOGLE_API_KEY` in `.env`
- **OpenAI**: Set `OPENAI_API_KEY` in `.env`
- **Anthropic**: Set `ANTHROPIC_API_KEY` in `.env`

The system will automatically detect and use the available API key.

### Running the Application

Start the FastAPI server:
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

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