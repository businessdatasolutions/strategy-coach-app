# CLAUDE.md - AI Strategic Co-pilot Project Documentation

## Project Overview

**Strategy Coach App v2.0** is an AI-powered strategic co-pilot that guides business leaders through a rigorous, sequential process of developing, refining, and testing their organizational strategy. The system leverages specialist AI agents focused on distinct phases of strategy development: WHY → HOW → WHAT.

### Vision
To create an AI-powered strategic co-pilot that guides business leaders through a Socratic, sequential process of strategy development, moving from core purpose to actionable planning in a logical sequence.

### Target User
Business Unit Managers at large corporations who need to create clear, defensible strategies to gain alignment and resources within their organization.

## System Architecture

### LangGraph-Native StateGraph Model
The system is built using **LangGraph's StateGraph** architecture, leveraging native LangGraph patterns for state management, agent coordination, and phase transitions.

1. **WHY Phase** - Discovery of organizational purpose using Simon Sinek methodology
2. **HOW Phase** - Strategic logic development using Analogy and Logic agents  
3. **WHAT Phase** - Strategy mapping and implementation planning

### Core LangGraph Components

#### StateGraph Architecture
- **StateGraph**: Central state machine managing WHY → HOW → WHAT progression
- **Agent Nodes**: Each specialist agent implemented as LangGraph node functions
- **Conditional Edges**: Phase transitions handled via LangGraph conditional routing
- **Built-in Checkpointing**: Session persistence using InMemorySaver/SqliteSaver
- **Structured State**: StrategyCoachState TypedDict with reducers

#### Agent Node Functions

##### WHY Agent Node (Phase 1)
- **Implementation**: `why_agent_node(state: StrategyCoachState)` function
- **Methodology**: Simon Sinek's "Start with Why" with LangChain structured output
- **Integration**: Uses `WHYStatement` schema for structured LLM responses
- **Output**: WHY Statement with Core Beliefs and Values stored in state

##### HOW Agent Node (Phase 2)  
- **Implementation**: `how_agent_node(state: StrategyCoachState)` function
- **Methodology**: Combined Carroll & Sørensen analogical reasoning + logic validation
- **Integration**: Uses `HOWStrategy` schema accessing `why_output` from state
- **Output**: Strategic logic with analogical analysis and logical validation

##### WHAT Agent Node (Phase 3)
- **Implementation**: `what_agent_node(state: StrategyCoachState)` function  
- **Methodology**: Combined Kaplan & Norton Strategy Map + Open Strategy
- **Integration**: Uses `WHATStrategy` schema accessing all previous phase outputs
- **Output**: Complete strategy_map.json with implementation planning

## Technical Stack

### Core Dependencies
- **LangChain Ecosystem**: langchain, langchain-core, langchain-anthropic, langgraph, langsmith
- **API Framework**: FastAPI with uvicorn, WebSocket support
- **Data Validation**: Pydantic v2+ with pydantic-settings
- **Testing**: pytest with asyncio, coverage, mock support
- **Browser Automation**: Playwright for E2E testing
- **Code Quality**: black, isort, flake8, mypy

### Project Structure
```
src/
├── core/           # LangGraph StateGraph and state management
│   ├── graph.py    # ✅ Main StateGraph implementation
│   ├── state.py    # ✅ StrategyCoachState TypedDict and reducers  
│   ├── routing.py  # ✅ Conditional edge functions
│   ├── models.py   # ✅ Pydantic structured output models
│   └── config.py   # ✅ Settings and configuration
├── agents/         # LangGraph agent node functions
│   └── why_node.py # ✅ WHY phase node function (Simon Sinek)
├── api/           # FastAPI integration with LangGraph
│   ├── main.py        # ✅ FastAPI app wrapping StateGraph
│   └── endpoints.py   # ✅ Routes calling graph.stream()/invoke()
└── testing/       # Automated testing agent with Playwright
    ├── testing_agent.py     # Main Playwright testing agent
    ├── business_case_parser.py # AFAS case parser & user simulation
    ├── screenshot_manager.py  # Screenshot capture & management
    └── report_generator.py    # Markdown report generation

tests/
├── core/          # ✅ StateGraph and checkpointing tests
│   ├── test_graph.py   # ✅ LangGraph integration tests
│   ├── test_state.py   # ✅ State management tests
│   ├── test_routing.py # ✅ Routing logic tests
│   └── test_models.py  # ✅ Pydantic model tests
└── agents/        # ✅ Agent node function tests  
    └── test_why_node.py # ✅ WHY agent comprehensive tests

frontend/
└── index.html    # ✅ Interactive chat interface for WHY agent testing
```

## Development Workflow

### Development Strategy
**Scaffolding Approach**: Build one element at a time and test that element before expanding the system with a new element. This incremental development strategy ensures:
- Each component is fully functional before integration
- Issues are isolated and easier to debug
- System complexity grows manageable increments
- Continuous validation of functionality at each step

**Documentation Verification**: Before starting any task, verify the implementation requirements against the relevant documentation available through Context7. Use "use context7" in prompts to access up-to-date, version-specific documentation for libraries and frameworks being used. This ensures compliance with current APIs and prevents issues with outdated code examples.

### Task Management Rules

#### Task Implementation Protocol
1. **One sub-task at a time** - Do NOT start next sub-task until user permission
2. **Completion Protocol**:
   - Mark sub-task completed: `[ ]` → `[x]`
   - When all subtasks complete:
     - Run full test suite (`pytest`)
     - Stage changes (`git add .`) only if tests pass
     - Clean up temporary files/code
     - Commit with conventional format and descriptive message
     - Mark parent task as completed

#### Task List Maintenance
- Update task list after significant work
- Add newly discovered tasks
- Maintain "Relevant Files" section accuracy
- Check which sub-task is next before starting work

### Testing Strategy

#### LangGraph-Native Testing
- **Graph Testing**: Direct StateGraph testing using `graph.invoke()` with test states
- **Node Testing**: Unit testing of individual agent node functions
- **Checkpoint Testing**: State persistence and recovery validation using checkpointer
- **Streaming Testing**: Real-time conversation testing via `graph.stream()`
- **Edge Testing**: Conditional routing and phase transition logic

#### Test Coverage
- **Unit Tests**: Individual agent node functions with mock StrategyCoachState
- **Graph Tests**: Complete StateGraph execution with realistic scenarios  
- **Checkpoint Tests**: Session persistence using `graph.get_state()` and history
- **API Tests**: FastAPI endpoints wrapping LangGraph functionality
- **E2E Tests**: Browser automation with LangGraph streaming integration

### Code Quality Standards

#### Python Configuration
- **Black**: Line length 88, Python 3.11 target
- **isort**: Black profile, known first party "src"
- **mypy**: Strict typing with untyped definitions disallowed
- **pytest**: Async mode auto, strict markers and config

#### Git Workflow
- **Branch Strategy**: Each major version should be started in a new branch on GitHub
  - Current: `v2-major-rewrite` (for v2.0 development)
  - Target: `main` (for PRs and stable releases)
- **Commit Format**: Conventional commits with detailed descriptions
- **Testing**: All tests must pass before commits
- **Documentation**: Update relevant files section after changes

## PRD and Task Generation Process

### PRD Creation Rules
1. **Clarifying Questions**: Must ask clarifying questions before writing PRD
2. **Target Audience**: Junior developer focused
3. **Structure**: Introduction, Goals, User Stories, Functional Requirements, Non-Goals, Design/Technical Considerations, Success Metrics, Open Questions
4. **Output**: Markdown format in `/tasks/` directory as `prd-[feature-name].md`

### Task List Generation Rules
1. **Two-Phase Process**: 
   - Phase 1: Generate parent tasks, wait for "Go" confirmation
   - Phase 2: Generate detailed sub-tasks
2. **Current State Assessment**: Review existing codebase patterns and components
3. **File Identification**: List relevant files needing creation/modification
4. **Output**: Markdown format as `tasks-[prd-file-name].md`

## Current Project Status

### Completed (Task 1.0)
- ✅ Python project structure with pyproject.toml
- ✅ All required dependencies (LangChain, LangGraph, FastAPI, Pydantic)
- ✅ Directory structure (src/, tests/, frontend/, testing/)
- ✅ Docker configuration
- ✅ pytest configuration and basic test structure
- ✅ README.md with setup instructions

### Completed Tasks
- ✅ **Task 1.0**: Project Foundation & Environment Setup
- ✅ **Task 2.0**: LangGraph StateGraph Core Implementation
- ✅ **Task 3.0**: WHY Agent Node Implementation (Simon Sinek methodology)
- ✅ **Task 6.0**: FastAPI-LangGraph Integration & Web API
- ✅ **Task 7.0**: Web UI & LangGraph Streaming Integration

### Architectural Pivot Completed
- ✅ **LangGraph Documentation Review**: Analyzed LangGraph patterns and identified architecture mismatch
- ✅ **PRD Updated**: Rewritten to reflect LangGraph-native StateGraph architecture  
- ✅ **Task List Refactored**: Changed from custom PhaseManager to LangGraph node functions
- ✅ **LangGraph Implementation**: Complete StateGraph with WHY agent node
- ✅ **Real API Testing**: Validated with live Anthropic Claude API calls

### Live Testing Environment
- ✅ **FastAPI Server**: Running at http://localhost:8000 with LangGraph integration
- ✅ **WHY Agent**: Live testing ready with Simon Sinek methodology
- ✅ **Frontend UI**: Interactive chat interface for real-time testing
- ✅ **API Endpoints**: REST and WebSocket endpoints for LangGraph streaming
- ✅ **Health Check**: http://localhost:8000/health (operational status)
- ✅ **Debug Endpoints**: Direct WHY agent testing and graph inspection
- ✅ **AFAS Business Case**: Realistic test data for automated testing agent

### Next Task (Task 9.0)  
**Automated Testing Agent with Playwright & UI Recording**
- Next sub-task: 9.1 "Create testing agent framework with Playwright browser automation"

**Testing Strategy**: Implement comprehensive testing agent that:
- Uses AFAS Software business case for realistic user simulation
- Tests each phase (WHY/HOW/WHAT) individually and in complete journey
- Records interactions with screenshots every 5th interaction
- Generates beautiful Markdown reports with embedded screenshots
- Validates LangGraph functionality through actual browser automation

## Development Environment

### Local Setup
- **Python**: >=3.11 required
- **Virtual Environment**: Always use `python3 -m venv venv && source venv/bin/activate`
- **Dependencies**: Use `pip install -e ".[dev]"` for development setup (in virtual environment)
- **Environment**: Copy `.env.example` to `.env` and configure API keys
- **Testing**: Run `pytest` for test suite (in virtual environment)
- **Code Quality**: `black`, `isort`, `flake8`, `mypy` configured
- **Container**: Docker Compose available for development environment

### API Configuration
- **Primary LLM**: Anthropic Claude (claude-sonnet-4-20250514)
- **Backup LLMs**: OpenAI GPT-4, Google Gemini configured
- **LangSmith**: Tracing enabled for interaction monitoring (Project: strategy-coach)
- **Rate Limiting**: 60 requests/minute, 1000/hour configured
- **Real API Testing**: Environment configured with valid API keys for live testing

### Permissions
- Allowed bash operations: mkdir, git checkout/rm, cp, pytest
- Additional working directories: `/Users/witoldtenhove/Documents/Projects`

### Monitoring and Tracing
- **LangSmith**: Configured for interaction tracing
- **Session Management**: In-memory for development, configurable for production
- **API Monitoring**: Logging setup for performance and error tracking

### MCP Server Integration
- **Optimal MCP Usage**: Make full use of available MCP (Model Context Protocol) servers for enhanced capabilities
- **Available MCP Tools**: Leverage any connected MCP servers (e.g., IDE integration, file system access, database connections)
- **Tool Discovery**: Use MCP servers to extend functionality beyond standard tools when available
- **Integration Strategy**: Prioritize MCP-provided tools over built-in alternatives when available for better performance and capabilities

## Success Metrics

- **Phase Completion Rate**: Users successfully completing all three phases
- **Logical Flow**: Smooth guidance through phased journey
- **Methodological Fidelity**: Faithful implementation of research-backed frameworks
- **Output Quality**: Well-structured strategy_map.json with complete strategy elements

## Non-Goals (Out of Scope)

- Direct business advice or opinions from the coach
- External data gathering or market analysis
- Financial models or projections generation
- Pluggable research agents or "Board of Directors" feedback features

---

*This documentation consolidates all Claude-specific project information and should be kept updated as the project evolves.*