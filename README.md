# AI Strategic Co-pilot v2.0

An AI-powered strategic co-pilot that guides business leaders through a rigorous, sequential process of developing, refining, and testing their organizational strategy using specialized AI agents.

## 🎯 Overview

This application implements a **Sequential State Machine** architecture with three distinct phases:

- **WHY Phase**: Discover organizational purpose using Simon Sinek methodology
- **HOW Phase**: Define strategic approach using analogical reasoning and logic validation  
- **WHAT Phase**: Create actionable strategy map and implementation plan

Each phase is managed by specialized AI agents built with LangChain/LangGraph, ensuring methodical progression from core purpose to actionable planning.

## 🏗️ Architecture

```
User Interface (React/HTML) 
        ↓
Phase Manager (State Machine)
        ↓
┌─────────────┬─────────────┬─────────────┐
│ WHY Agent   │ HOW Agents  │ WHAT Agents │
│ (Simon      │ (Analogy +  │ (Strategy   │
│  Sinek)     │  Logic)     │  Map + Open)│
└─────────────┴─────────────┴─────────────┘
        ↓
LangChain/LangGraph + LangSmith Tracing
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (optional but recommended)
- API keys for your chosen LLM provider (Anthropic Claude, OpenAI, or Google Gemini)
- LangSmith account for tracing (optional but recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/businessdatasolutions/strategy-coach-app.git
   cd strategy-coach-app
   git checkout v2-major-rewrite
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Choose your setup method:**

#### Option A: Docker (Recommended)
```bash
# Start the application with Docker Compose
docker-compose up --build

# Run tests
docker-compose --profile testing run test
```

#### Option B: Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install Playwright browsers (for testing)
playwright install chromium

# Run the application
uvicorn src.api.main:app --reload --port 8000

# Run tests
pytest
```

### Configuration

Edit your `.env` file with the required API keys:

```bash
# Choose your LLM provider
LLM_PROVIDER=anthropic  # or openai, google

# Add your API key
ANTHROPIC_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here

# Optional: LangSmith tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_PROJECT=strategy-coach-app-v2
```

## 🧪 Testing

The application includes comprehensive testing capabilities:

### Run Basic Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e            # End-to-end tests only

# Run tests for specific components
pytest -m agent         # Agent-specific tests
pytest -m why_phase     # WHY phase tests
pytest -m testing_agent # Testing agent tests
```

### Automated Testing Agent

The application includes a sophisticated Testing Agent that can simulate realistic user interactions:

```bash
# Run the Testing Agent with AFAS Software business case
python -m src.testing.testing_agent --mode full_journey

# Test individual phases
python -m src.testing.testing_agent --mode why_phase
python -m src.testing.testing_agent --mode how_phase
python -m src.testing.testing_agent --mode what_phase
```

## 📁 Project Structure

```
├── src/
│   ├── core/              # Core system components
│   │   ├── config.py      # Configuration management
│   │   ├── models.py      # Pydantic data models
│   │   ├── phase_manager.py # State machine controller
│   │   └── session_state.py # Session management
│   ├── agents/            # AI agent implementations
│   │   ├── base_agent.py  # Base agent class
│   │   ├── why_agent.py   # WHY phase agent
│   │   ├── analogy_agent.py # HOW phase analogy agent
│   │   ├── logic_agent.py   # HOW phase logic agent
│   │   ├── strategy_map_agent.py # WHAT phase strategy map
│   │   └── open_strategy_agent.py # WHAT phase open strategy
│   ├── api/               # FastAPI backend
│   │   ├── main.py        # API entry point
│   │   ├── routes.py      # HTTP routes
│   │   └── websocket.py   # WebSocket handlers
│   └── testing/           # Testing agent system
│       ├── testing_agent.py # Main testing agent
│       ├── business_case_parser.py # Business case parser
│       └── user_simulator.py # User response simulation
├── tests/                 # Test suite
├── frontend/              # Web UI components
├── testing/               # Business cases and test scenarios
├── technical-documentation/ # LangChain/LangGraph patterns
└── docker-compose.yml     # Development environment
```

## 🔧 Development

### Adding New Agents

1. Create agent class in `src/agents/`
2. Extend `BaseAgent` class
3. Implement required methods
4. Add to phase manager routing
5. Create comprehensive tests

### Running Individual Components

```bash
# Test WHY Agent in isolation
python -m src.agents.why_agent

# Test Phase Manager
python -m src.core.phase_manager

# Run API server only
uvicorn src.api.main:app --reload
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## 📊 Monitoring

### LangSmith Tracing

If you've configured LangSmith, all agent interactions are automatically traced:

1. Visit [LangSmith Dashboard](https://smith.langchain.com)
2. Select your project: `strategy-coach-app-v2`
3. Monitor agent performance, costs, and conversation flows

### Application Logs

```bash
# View application logs
docker-compose logs -f app

# View specific component logs
docker-compose logs -f redis
```

## 🚢 Deployment

### Production Docker Build

```bash
# Build production image
docker build --target production -t strategy-coach-app:v2.0.0 .

# Run in production mode
docker run -p 8000:8000 --env-file .env.production strategy-coach-app:v2.0.0
```

### Environment Variables for Production

```bash
DEBUG=false
LOG_LEVEL=WARNING
API_RELOAD=false
ENABLE_CORS=false
LANGCHAIN_TRACING_V2=true  # Keep tracing for monitoring
```

## 🎮 Usage Examples

### Basic Strategy Session

1. Start the application: `docker-compose up`
2. Open browser to `http://localhost:8000`
3. Begin with WHY phase: "I want to develop a strategy for my software company"
4. Follow agent guidance through each phase
5. Receive final strategy map JSON output

### Testing Different Business Cases

1. Add your business case to `testing/business-cases/`
2. Update `TEST_BUSINESS_CASE_PATH` in `.env`
3. Run Testing Agent: `python -m src.testing.testing_agent`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-agent`
3. Make changes and add tests
4. Ensure all tests pass: `pytest`
5. Submit pull request

## 🛟 Troubleshooting

### Common Issues

**API Key Issues:**
```bash
# Verify your API keys are set
python -c "from src.core.config import settings; print(settings.get_llm_api_key())"
```

**Import Errors:**
```bash
# Ensure PYTHONPATH is set correctly
export PYTHONPATH=/path/to/project/src
```

**Docker Issues:**
```bash
# Clean rebuild
docker-compose down -v
docker-compose up --build
```

### Support

- 📋 [Issues](https://github.com/businessdatasolutions/strategy-coach-app/issues)
- 📖 [Documentation](./technical-documentation/)
- 💬 [Discussions](https://github.com/businessdatasolutions/strategy-coach-app/discussions)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Simon Sinek** - "Start with Why" methodology
- **Carroll & Sørensen** - Analogical reasoning framework  
- **Kaplan & Norton** - Strategy Maps framework
- **LangChain Team** - Agent orchestration platform
- **AFAS Software** - Business case example for testing

---

Built with ❤️ using LangChain, LangGraph, and FastAPI