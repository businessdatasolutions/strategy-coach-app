# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Strategic Co-pilot - A fully-functional multi-agent workflow system that guides business leaders through developing organizational strategy using specialized AI agents with research-backed methodologies.

**Project Status**: 
- ✅ **COMPLETE** - Core functionality (Tasks 1.0-6.0 including Web UI)
- 🚧 **PLANNED** - Enhanced features (Tasks 7.0-8.0)
  - Task 7.0: Progress Feedback & Strategic Completeness System
  - Task 8.0: Mistral AI Integration for Multi-Model Support
- 🔄 **ACTIVE** - Bug fixes and improvements

**Current Configuration**:
- Default LLM: Claude Sonnet 4.0 (`claude-sonnet-4-20250514`)
- Supported Providers: Anthropic ✅, OpenAI ✅, Google ✅, Mistral 🚧

## Recent Updates (Aug 2025)

- **Claude Sonnet 4.0 Upgrade**: Improved conversation quality and strategic reasoning
- **Cursor Auto-Focus**: Better UX with automatic input field focus
- **Progress Feedback Feature**: Added to PRD for better user guidance (Task 7.0)
- **Mistral AI Integration**: Planned multi-model support (Task 8.0)
- **Cognitive Bias Detection**: Enhancement planned for Logic Agent
- **Documentation Updates**: Comprehensive guides for all new features

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
echo "ANTHROPIC_API_KEY=your-key-here" > .env
echo "DEFAULT_LLM_PROVIDER=anthropic" >> .env
echo "DEFAULT_MODEL=claude-sonnet-4-20250514" >> .env
# Optional providers:
# echo "OPENAI_API_KEY=your-key-here" >> .env
# echo "GOOGLE_API_KEY=your-key-here" >> .env
# echo "MISTRAL_API_KEY=your-key-here" >> .env  # Coming soon

# 3. Start the API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 4. Start the Web UI (in separate terminal)
cd web
python3 -m http.server 8081

# 5. Access the application
# Web UI: http://localhost:8081
# API Docs: http://localhost:8000/docs
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
├── web/                      # Web UI application
│   ├── index.html           # Main UI with Alpine.js + Tailwind
│   ├── demo.html            # Demo page with screenshots
│   └── interactive-demo.html # Interactive selection demo
├── tests/                    # 100+ unit and integration tests
│   ├── agents/              # Agent-specific tests
│   ├── api/                 # API integration tests
│   ├── models/              # State model tests
│   └── utils/               # Utility tests
├── issues/                  # Known issues and feature specifications
│   ├── ISSUE_*.md          # Issue documentation
│   └── FEATURE_*.md        # Feature specifications
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
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...

# LLM Configuration
DEFAULT_LLM_PROVIDER=anthropic  # Options: anthropic, openai, google, mistral (coming)
DEFAULT_MODEL=claude-sonnet-4-20250514  # Best for strategic reasoning
# Alternative models:
# anthropic: claude-3-5-haiku-20241022 (faster, cheaper)
# openai: gpt-4, gpt-3.5-turbo
# google: gemini-2.0-flash-exp
# mistral: mistral-large-latest (planned)

# Optional
DEBUG=False
LOG_LEVEL=INFO
SESSION_TIMEOUT_MINUTES=60
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

## Known Issues

### 🔴 Open Issues

1. **AI Coach Synthesis Validation Loop** (issues/ISSUE_AI_COACH_SYNTHESIS_VALIDATION_LOOP.md) - **NEW**
   - AI coach trapped in endless WHY synthesis validation cycles
   - Repeats same comprehensive framework without user progression
   - Discovered by Testing Agent validation - affects all coaching sessions
   - Priority: **Critical**

2. **AI Coach Assumes User Agreement** (issues/ISSUE_AI_ASSUMES_USER_AGREEMENT.md)
   - AI asks validation questions but doesn't wait for user confirmation
   - Confirmed by Testing Agent - systematic problem across conversations
   - Violates fundamental coaching principles and user agency
   - Priority: **High**

3. **Logic Agent Cognitive Bias Detection** (issues/ISSUE_LOGIC_AGENT_COGNITIVE_BIAS.md)
   - Logic Agent needs Kahneman's framework for bias detection
   - Enhancement to identify cognitive biases in strategic thinking
   - Priority: High

4. **LangGraph Supervisor Integration** (issues/ISSUE_LANGGRAPH_SUPERVISOR_INTEGRATION.md)
   - Explore hybrid architecture combining supervisor pattern with our strategic coaching system
   - Add tool integration and explicit agent handoff capabilities
   - Priority: Medium-High

### 🚀 Planned Features

1. **Achievement Badges** (issues/FEATURE_ACHIEVEMENT_BADGES.md)
   - Gamification system with milestone-based badge rewards
   - Visual recognition for strategic progress achievements
   - Priority: Medium

2. **Testing Agent User Journey** (issues/FEATURE_TESTING_AGENT_USER_JOURNEY.md)
   - Intelligent testing agent simulating complete user journey with business case context
   - Multi-modal recording system with text and visual snapshots
   - Priority: High (Quality Assurance)

### ✅ Resolved Issues

1. **Cursor Focus** (issues/ISSUE_CURSOR_FOCUS.md) - RESOLVED
   - Input field now auto-focuses after AI response
   - Improves conversation flow UX

2. **Duplicate Messages** (issues/ISSUE_DUPLICATE_MESSAGES.md) - PARTIALLY RESOLVED
   - Fixed initialization issue preventing duplicates
   - Some edge cases may still occur

3. **Duplicate Interactive Selections** (issues/ISSUE_DUPLICATE_INTERACTIVE_SELECTIONS.md) - RESOLVED
   - Implemented content-based ID generation for interactive elements
   - Interactive elements functionality disabled for system stability
   - Will be re-enabled during gamification feature development
   - Fixed visual clutter and user confusion issues

4. **Chart.js Stack Overflow** - RESOLVED
   - Fixed infinite recursion in chart update logic causing stack overflow errors
   - Implemented proper canvas cleanup and Alpine.js reactivity isolation
   - Added throttling and concurrent update prevention
   - Chart functionality now stable without console errors

5. **Simple Testing Agent Message Extraction** (issues/ISSUE_SIMPLE_TESTING_AGENT_MESSAGE_EXTRACTION.md) - RESOLVED
   - Fixed AI message extraction using Alpine.js data access
   - Implemented reliable browser automation with Playwright
   - Testing Agent now successfully validates strategic coaching quality
   - Produces comprehensive reports with screenshots and interaction data

5. **Question Quality** (issues/ISSUE_QUESTION_QUALITY.md)
   - Improvements needed for avoiding cognitive biases in questions

## Current Configuration

The application is currently configured to use:
- **Primary LLM**: Anthropic Claude 3.5 Haiku
- **CORS**: Supports ports 8080, 8081 for web UI
- **Session Storage**: JSON files in data/sessions/
- **Logging**: Comprehensive logging to logs/ directory