## Relevant Files

### LangGraph Core Files
- `src/core/graph.py` - Main StateGraph implementation and compilation
- `src/core/state.py` - StrategyCoachState TypedDict and reducer functions  
- `src/core/models.py` - Pydantic models for structured outputs (WHY/HOW/WHAT)
- `src/core/routing.py` - Conditional edge functions for phase transitions
- `tests/core/test_graph.py` - StateGraph integration tests
- `tests/core/test_state.py` - State management and reducer tests
- `tests/core/test_models.py` - Pydantic model validation tests

### LangGraph Agent Node Files
- `src/agents/why_node.py` - WHY phase node function using Simon Sinek methodology
- `src/agents/how_node.py` - HOW phase node function (analogy + logic combined)
- `src/agents/what_node.py` - WHAT phase node function (strategy map + open strategy)
- `src/agents/completion_checks.py` - Phase completion detection logic
- `tests/agents/test_why_node.py` - Unit tests for WHY node function
- `tests/agents/test_how_node.py` - Unit tests for HOW node function  
- `tests/agents/test_what_node.py` - Unit tests for WHAT node function

### FastAPI Integration Files
- `src/api/main.py` - FastAPI application wrapping LangGraph
- `src/api/endpoints.py` - API routes calling graph.stream() and graph.invoke()
- `tests/api/test_graph_endpoints.py` - LangGraph-FastAPI integration tests

### Testing Agent & Automation Files
- `src/testing/testing_agent.py` - Main Playwright-based testing agent
- `src/testing/business_case_parser.py` - AFAS Software business case parser
- `src/testing/user_simulator.py` - Realistic user response generator based on business case
- `src/testing/screenshot_manager.py` - Screenshot capture and management (every 5th interaction)
- `src/testing/interaction_logger.py` - JSON interaction logging and session recording
- `src/testing/report_generator.py` - Beautiful Markdown report generator with embedded screenshots
- `tests/testing/test_playwright_agent.py` - Testing agent validation tests
- `testing/business-cases/business-case-for-testing.md` - AFAS Software business case data
- `testing/reports/` - Generated test reports with screenshots and interaction logs

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

- All agent logic implemented as **LangGraph node functions** following StateGraph patterns
- Use **pytest** for testing LangGraph components: `pytest tests/core/test_graph.py -v`
- Leverage **LangGraph's built-in testing** capabilities including graph.invoke() for unit tests
- Use **LangGraph checkpointing** for session persistence instead of custom session management
- Each phase should be testable in isolation using LangGraph's state management

## Tasks

- [x] 1.0 Project Foundation & Environment Setup
  - [x] 1.1 Initialize Python project with pyproject.toml and dependencies (LangChain, LangGraph, FastAPI, Pydantic, pytest)
  - [x] 1.2 Set up project directory structure (src/, tests/, frontend/, testing/)
  - [x] 1.3 Configure environment variables and LangSmith tracing integration
  - [x] 1.4 Create Docker configuration for development environment
  - [x] 1.5 Set up pytest configuration and basic test structure
  - [x] 1.6 Create README.md with setup and running instructions

- [x] 2.0 LangGraph StateGraph Core Implementation
  - [x] 2.1 Implement Pydantic models for structured outputs (WHY/HOW/WHAT phases)
  - [x] 2.2 Create StrategyCoachState TypedDict with proper reducers and LangGraph message handling
  - [x] 2.3 Build main StateGraph with node registration and conditional edge routing
  - [x] 2.4 Implement LangGraph checkpointing for session persistence (InMemorySaver → SqliteSaver)
  - [x] 2.5 Create conditional edge functions for phase transition logic
  - [x] 2.6 Add comprehensive StateGraph integration tests and checkpointing validation

- [x] 3.0 WHY Agent Node Implementation  
  - [x] 3.1 Create why_agent_node() function following LangGraph node pattern
  - [x] 3.2 Implement Simon Sinek methodology with LangChain structured output (WHYStatement)
  - [x] 3.3 Build Socratic questioning workflow within node function
  - [x] 3.4 Create phase completion detection logic for WHY → HOW transition
  - [x] 3.5 Add comprehensive unit tests for WHY node function using graph.invoke()
  - [x] 3.6 Build isolated WHY phase test using LangGraph state management

- [ ] 4.0 HOW Agent Node Implementation
  - [ ] 4.1 Create how_agent_node() function combining analogy and logic methodologies
  - [ ] 4.2 Implement Carroll & Sørensen analogical reasoning with structured output
  - [ ] 4.3 Build logical validation within same node function using HOWStrategy output
  - [ ] 4.4 Create phase completion detection for HOW → WHAT transition
  - [ ] 4.5 Add comprehensive unit tests for HOW node function
  - [ ] 4.6 Build isolated HOW phase test using LangGraph checkpointing

- [ ] 5.0 WHAT Agent Node Implementation
  - [ ] 5.1 Create what_agent_node() function combining strategy map and open strategy
  - [ ] 5.2 Implement Kaplan & Norton framework with Six Value Components using structured output
  - [ ] 5.3 Build Open Strategy methodology for implementation planning within same node
  - [ ] 5.4 Generate final strategy_map.json as structured WHATStrategy output
  - [ ] 5.5 Add comprehensive unit tests for WHAT node function
  - [ ] 5.6 Build complete strategy generation test using full graph execution

- [x] 6.0 FastAPI-LangGraph Integration & Web API
  - [x] 6.1 Create FastAPI endpoints wrapping graph.stream() for real-time conversations
  - [x] 6.2 Implement thread_id based session management using LangGraph checkpointing
  - [x] 6.3 Build WebSocket integration for streaming LangGraph updates
  - [x] 6.4 Create API models for graph input/output and state inspection
  - [x] 6.5 Add comprehensive API tests using graph.invoke() and checkpointer
  - [x] 6.6 Build API documentation and testing endpoints

- [x] 7.0 Web UI & LangGraph Streaming Integration
  - [x] 7.1 Create HTML/CSS interface optimized for LangGraph streaming responses
  - [x] 7.2 Implement JavaScript client for graph.stream() WebSocket integration
  - [x] 7.3 Build phase progress tracker using LangGraph state inspection
  - [x] 7.4 Create UI components for phase transitions and structured output display
  - [ ] 7.5 Add comprehensive frontend tests with LangGraph backend integration

- [ ] 8.0 LangSmith Tracing & Observability Implementation
  - [ ] 8.1 Configure LangSmith environment variables and project setup (strategy-coach)
  - [ ] 8.2 Implement comprehensive tracing for all LangGraph agent node interactions
  - [ ] 8.3 Add tracing for state transitions and conditional edge routing
  - [ ] 8.4 Set up monitoring for LLM calls, token usage, and response times
  - [ ] 8.5 Create error tracking and debugging capabilities via LangSmith
  - [ ] 8.6 Build trace analysis and performance reporting dashboards

- [ ] 9.0 Automated Testing Agent with Playwright & UI Recording
  - [ ] 9.1 Create testing agent framework with Playwright browser automation
  - [ ] 9.2 Implement AFAS Software business case parser and user persona simulation
  - [ ] 9.3 Build WHY phase isolated testing with screenshot recording every 3rd interaction
  - [ ] 9.4 Build HOW phase isolated testing with analogical reasoning validation and screenshot recording every 3rd interaction
  - [ ] 9.5 Build WHAT phase isolated testing with strategy map generation and screenshot recording every 3rd interaction
  - [ ] 9.6 Create complete user journey testing (WHY → HOW → WHAT full flow)
  - [ ] 9.7 Implement JSON interaction logging and screenshot management
  - [ ] 9.8 Build beautiful Markdown test report generator with embedded screenshots
  - [ ] 9.9 Add LangSmith trace analysis integration for testing reports

- [ ] 10.0 LangGraph-Native Core Testing & Validation
  - [ ] 10.1 Build comprehensive graph testing using graph.invoke() with test scenarios
  - [ ] 10.2 Create checkpoint testing for session persistence and state recovery
  - [ ] 10.3 Implement streaming testing using graph.stream() with realistic business cases
  - [ ] 10.4 Add performance testing and token usage monitoring
  - [ ] 10.5 Create test reporting with LangSmith trace analysis and performance metrics