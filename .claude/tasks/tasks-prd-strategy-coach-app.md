## Relevant Files

### Core System Files
- `src/core/phase_manager.py` - Central phase state machine controller that routes between agents
- `src/core/session_state.py` - Session management and state persistence
- `src/core/models.py` - Pydantic models for structured outputs and data validation
- `tests/core/test_phase_manager.py` - Unit tests for phase management logic
- `tests/core/test_session_state.py` - Unit tests for session state management

### Agent Implementation Files  
- `src/agents/why_agent.py` - WHY Agent using Simon Sinek methodology
- `src/agents/analogy_agent.py` - Analogy Agent using Carroll & Sørensen method
- `src/agents/logic_agent.py` - Logic Agent for strategic argument validation
- `src/agents/strategy_map_agent.py` - Strategy Map Agent using Kaplan & Norton framework
- `src/agents/open_strategy_agent.py` - Open Strategy Agent for implementation planning
- `src/agents/base_agent.py` - Base agent class with common functionality
- `tests/agents/test_why_agent.py` - Unit tests for WHY Agent
- `tests/agents/test_analogy_agent.py` - Unit tests for Analogy Agent
- `tests/agents/test_logic_agent.py` - Unit tests for Logic Agent
- `tests/agents/test_strategy_map_agent.py` - Unit tests for Strategy Map Agent
- `tests/agents/test_open_strategy_agent.py` - Unit tests for Open Strategy Agent

### API and Backend Files
- `src/api/main.py` - FastAPI application entry point
- `src/api/routes.py` - API routes for user interactions
- `src/api/websocket.py` - WebSocket handlers for real-time communication
- `src/api/middleware.py` - Request/response middleware
- `tests/api/test_routes.py` - API endpoint tests
- `tests/api/test_websocket.py` - WebSocket functionality tests

### Frontend Files
- `frontend/index.html` - Main web application interface
- `frontend/js/app.js` - Core JavaScript application logic
- `frontend/js/phase-tracker.js` - Phase progress tracking component
- `frontend/js/chat-interface.js` - Chat interface for user-agent interaction
- `frontend/css/styles.css` - Application styling
- `frontend/css/components.css` - Component-specific styles
- `tests/frontend/test_ui.html` - Simple HTML test interface for manual testing

### Testing Agent Files
- `src/testing/testing_agent.py` - Main Testing Agent for automated system testing
- `src/testing/business_case_parser.py` - Parser for business case files
- `src/testing/user_simulator.py` - User response simulation logic
- `src/testing/test_scenarios.py` - Test scenario definitions
- `src/testing/report_generator.py` - Test report generation
- `tests/testing/test_testing_agent.py` - Unit tests for Testing Agent

### Configuration and Infrastructure Files
- `pyproject.toml` - Python project dependencies and configuration
- `docker-compose.yml` - Multi-service development environment
- `Dockerfile` - Container configuration for the application
- `.env.example` - Environment variables template
- `langsmith.yaml` - LangSmith tracing configuration
- `pytest.ini` - Test configuration
- `README.md` - Project documentation and setup instructions

### Notes

- Unit tests should typically be placed alongside the code files they are testing (e.g., `MyComponent.tsx` and `MyComponent.test.tsx` in the same directory).
- Use `npx jest [optional/path/to/test/file]` to run tests. Running without a path executes all tests found by the Jest configuration.
- Each finished task should also be testable by the user using a simple UI build with plain HTML, JS and CSS.

## Tasks

- [ ] 1.0 Project Foundation & Environment Setup
  - [ ] 1.1 Initialize Python project with pyproject.toml and dependencies (LangChain, LangGraph, FastAPI, Pydantic, pytest)
  - [ ] 1.2 Set up project directory structure (src/, tests/, frontend/, testing/)
  - [ ] 1.3 Configure environment variables and LangSmith tracing integration
  - [ ] 1.4 Create Docker configuration for development environment
  - [ ] 1.5 Set up pytest configuration and basic test structure
  - [ ] 1.6 Create README.md with setup and running instructions

- [ ] 2.0 Core Phase Management System Implementation
  - [ ] 2.1 Implement Pydantic models for session state, phase transitions, and structured outputs
  - [ ] 2.2 Create SessionState class with phase tracking and conversation history
  - [ ] 2.3 Build PhaseManager as central state machine controller with routing logic
  - [ ] 2.4 Implement phase transition validation and user confirmation handling
  - [ ] 2.5 Add session persistence layer (in-memory for development, configurable for production)
  - [ ] 2.6 Create comprehensive unit tests for phase management logic

- [ ] 3.0 WHY Agent Implementation with Structured Output
  - [ ] 3.1 Create BaseAgent class with common functionality (LLM integration, state management)
  - [ ] 3.2 Implement WHY Agent using Simon Sinek methodology and Golden Circle framework
  - [ ] 3.3 Design structured output templates for WHY Statement, Core Beliefs, and Values
  - [ ] 3.4 Build Socratic questioning workflow for discovering organizational purpose
  - [ ] 3.5 Implement phase completion detection and transition triggers
  - [ ] 3.6 Create comprehensive unit tests and integration tests for WHY Agent
  - [ ] 3.7 Build simple test UI for WHY Agent isolated testing

- [ ] 4.0 HOW Agents Implementation (Analogy & Logic Agents)  
  - [ ] 4.1 Implement Analogy Agent using Carroll & Sørensen analogical reasoning method
  - [ ] 4.2 Build horizontal vs vertical relations analysis workflow
  - [ ] 4.3 Create structured outputs for causal theory development and analogical analysis
  - [ ] 4.4 Implement Logic Agent for strategic argument validation and deductive logic
  - [ ] 4.5 Build coordination logic between Analogy and Logic agents within HOW phase
  - [ ] 4.6 Create comprehensive unit tests for both HOW agents
  - [ ] 4.7 Build test UI for HOW phase isolated testing

- [ ] 5.0 WHAT Agents Implementation (Strategy Map & Open Strategy Agents)
  - [ ] 5.1 Implement Strategy Map Agent using Kaplan & Norton framework with Six Value Components
  - [ ] 5.2 Build structured strategy_map.json output with four perspectives (Stakeholder, Process, Learning, Value Creation)
  - [ ] 5.3 Implement Open Strategy Agent for inclusive strategy testing and implementation planning
  - [ ] 5.4 Create workflows for strategy validation, refinement, and mobilization planning  
  - [ ] 5.5 Build coordination between Strategy Map and Open Strategy agents
  - [ ] 5.6 Create comprehensive unit tests for both WHAT agents
  - [ ] 5.7 Build test UI for WHAT phase isolated testing

- [ ] 6.0 Web UI Development with Phase Progress Tracking
  - [ ] 6.1 Create responsive HTML/CSS interface with chat-style interaction
  - [ ] 6.2 Implement phase progress tracker with visual indicators for WHY → HOW → WHAT
  - [ ] 6.3 Build JavaScript chat interface with real-time message handling
  - [ ] 6.4 Create FastAPI backend with WebSocket support for real-time communication
  - [ ] 6.5 Implement API routes for session management and agent interactions
  - [ ] 6.6 Add phase transition UI components and confirmation dialogs
  - [ ] 6.7 Create comprehensive frontend and API tests

- [ ] 7.0 Automated Testing Agent & System Integration
  - [ ] 7.1 Implement Testing Agent with business case parsing capabilities
  - [ ] 7.2 Build User Simulator that generates realistic responses based on AFAS Software context
  - [ ] 7.3 Create modular test scenarios (single agent, single phase, partial journey, full journey)
  - [ ] 7.4 Implement Playwright browser automation for end-to-end testing
  - [ ] 7.5 Build test report generation with screenshots and interaction logs
  - [ ] 7.6 Create comprehensive test suite covering all system components
  - [ ] 7.7 Implement CI/CD pipeline with automated testing and deployment readiness