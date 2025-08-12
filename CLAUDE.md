# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Strategic Co-pilot - A fully-functional multi-agent workflow system that guides business leaders through developing organizational strategy using specialized AI agents with research-backed methodologies.

**Project Status**: ✅ COMPLETE - All development tasks finished (Sections 1.0-5.0)

## Architecture

**Core Components**:
- **FastAPI Application** (`src/api/main.py`): RESTful API with comprehensive endpoints
- **Orchestrator** (`src/agents/orchestrator.py`): Central StateGraph managing conversation flow
- **Advanced Router** (`src/agents/router.py`): Intelligent agent selection based on context
- **Strategy Map Agent** (`src/agents/strategy_map_agent.py`): Persistent JSON state management
- **Conversation Synthesizer** (`src/agents/synthesizer.py`): Response synthesis and integration

**Specialist Agents**:
- **WHY Agent** (`src/agents/why_agent.py`): Simon Sinek's Golden Circle methodology
- **Analogy Agent** (`src/agents/analogy_agent.py`): Carroll & Sørensen's analogical reasoning
- **Logic Agent** (`src/agents/logic_agent.py`): Deductive argument validation
- **Open Strategy Agent** (`src/agents/open_strategy_agent.py`): Implementation planning

**Workflow**: API Request → Session Management → Orchestrator → Router → Specialist Agent → Strategy Map Update → Response Synthesis → API Response

## Quick Start

```bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure API keys (create .env file)
echo "OPENAI_API_KEY=your-key-here" > .env
# or
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# 3. Start the server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 4. Access the API
# Browser: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

## Development Commands

```bash
# Testing
pytest                          # Run all tests (100+ tests)
pytest tests/api/               # Run API integration tests
pytest tests/agents/            # Run agent-specific tests
pytest -v --cov=src            # Run with coverage report

# Code quality
black src/ tests/              # Format code
ruff check src/ tests/          # Lint code
mypy src/                       # Type checking

# Development server
./venv/bin/uvicorn src.api.main:app --reload  # Auto-reload on changes
```

## Task Management Protocol

When working on tasks from `.claude/tasks/tasks-prd-multi-agent-strategy-coach.md`:

### Task List Updates
- **ALWAYS** keep the task list file current by updating completed tasks with `[x]` immediately after completion
- Use the TodoWrite tool to track internal progress and communicate status to user
- The task list file serves as the master record of project progress

### Sub-task Execution
1. Complete one sub-task at a time with focused implementation
2. **ALWAYS ASK** for user permission before proceeding to the next sub-task ("Would you like me to proceed to task X.X?")
3. Mark completed tasks immediately in both TodoWrite tool and the task list file
4. When encountering issues, document them clearly and continue with user guidance

### Task Completion Protocol
When all sub-tasks in a parent task are complete:
1. Run comprehensive tests to ensure stability
2. Update task list file to mark parent task as `[x]`
3. If requested by user, stage changes and commit with conventional format
4. Provide summary of completed functionality to user

### Permission and Communication
- User has explicitly granted permission to continue to next sub-tasks when asked
- Always ask before starting a new sub-task to maintain user control
- Provide clear progress updates and explain what each task accomplishes

## Key Implementation Details

- **State Management**: Uses LangGraph's `AgentState` TypedDict with `conversation_history` and `strategy_map_path`
- **Session Files**: Each session creates unique `{session_id}_strategy_map.json` for persistence
- **Agent Communication**: Agents return structured outputs (questions/topics/plans) to Orchestrator for synthesis
- **Strategy Map Structure**: Four perspectives with Six Value Components (Financial, Manufactured, Intellectual, Human, Social & Relationship, Natural)

## API Endpoints

### Conversation Management
- `POST /conversation/start` - Initialize new strategic conversation session
- `POST /conversation/{session_id}/message` - Send message and receive AI response
- `GET /conversation/{session_id}/export` - Export complete strategy map with summary
- `GET /conversation/{session_id}/export/download` - Download strategy map as JSON file

### Session Management  
- `GET /sessions` - List all active conversation sessions
- `GET /sessions/{session_id}` - Get detailed session information
- `DELETE /sessions/{session_id}` - Delete a specific session
- `POST /sessions/cleanup` - Manually trigger expired session cleanup

### Health & Monitoring
- `GET /` - API root information
- `GET /health` - Service health check with component status
- `GET /docs` - Interactive Swagger UI documentation
- `GET /redoc` - Alternative ReDoc documentation

## Project Structure

```
strategy-coach-app-v1/
├── src/
│   ├── api/
│   │   ├── main.py           # FastAPI application with all endpoints
│   │   └── middleware.py      # Rate limiting, validation, error handling
│   ├── agents/
│   │   ├── orchestrator.py   # Central workflow orchestrator
│   │   ├── router.py         # Advanced routing logic
│   │   ├── synthesizer.py    # Response synthesis
│   │   ├── strategy_map_agent.py  # JSON persistence & validation
│   │   ├── why_agent.py      # WHY discovery (Simon Sinek)
│   │   ├── analogy_agent.py  # Analogical reasoning
│   │   ├── logic_agent.py    # Logical validation
│   │   └── open_strategy_agent.py # Implementation planning
│   ├── models/
│   │   └── state.py          # AgentState, StrategyMapState definitions
│   └── utils/
│       ├── config.py         # Configuration management
│       ├── logging_config.py # Comprehensive logging
│       ├── llm_client.py     # LLM client wrapper
│       └── prompts.py        # Prompt templates
├── tests/                    # 100+ unit and integration tests
│   ├── agents/              # Agent-specific tests
│   ├── api/                 # API integration tests
│   ├── models/              # State model tests
│   └── utils/               # Utility tests
├── data/sessions/           # Strategy map JSON storage
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── CLAUDE.md               # This file
```

## Middleware & Features

- **Rate Limiting**: 60 req/min, 1000 req/hour per IP
- **Request Validation**: JSON validation, size limits, content-type checks
- **Session Management**: UUID-based sessions with automatic expiration
- **Background Tasks**: Async strategy map updates, periodic cleanup
- **Error Handling**: Comprehensive error responses with logging
- **CORS Support**: Configurable origins for cross-origin requests
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Testing Coverage

- **Unit Tests**: All agents, models, utilities (~80 tests)
- **Integration Tests**: Complete conversation flows (~45 tests)
- **Test Coverage**: Comprehensive coverage of critical paths
- **Test Fixtures**: Mock LLM clients, orchestrators, state management

## Environment Variables

Create `.env` file with:
```
# Required (at least one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional
DEBUG=False
LOG_LEVEL=INFO
SESSION_TIMEOUT_MINUTES=60
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```