# 🎯 Strategy Coach Evaluation Suite

## Overview

This comprehensive evaluation framework provides automated testing for the AI Strategic Co-pilot multi-agent system. It simulates complete coaching sessions, evaluates conversation quality, validates strategy map generation, and ensures proper agent routing.

## Features

### 🔬 Evaluation Capabilities

1. **End-to-End Session Testing**
   - Simulates full coaching conversations (10-15 turns)
   - Tests all four specialist agents (WHY, Analogy, Logic, Open Strategy)
   - Validates complete strategy map generation
   - Captures UI interactions via Playwright

2. **Multi-Dimensional Metrics**
   - **Answer Relevancy**: Contextual appropriateness of responses
   - **Faithfulness**: Accuracy and consistency with strategy framework
   - **Strategic Quality**: Business value of insights provided
   - **Strategy Map Completeness**: Coverage of all strategic dimensions
   - **Agent Routing Accuracy**: Correct specialist selection
   - **Conversation Coherence**: Logical flow and continuity

3. **Visual Documentation**
   - Screenshots at key interaction points
   - Strategy map evolution tracking
   - HTML reports with embedded visuals
   - JSON metrics for CI/CD integration

4. **CI/CD Integration**
   - GitHub Actions workflow
   - Quality gates (80% success threshold)
   - Automated PR comments with results
   - Daily scheduled evaluations
   - Performance benchmarking

## Setup

### Prerequisites

```bash
# Install Python dependencies
pip install -r tests/evaluation/requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps chromium

# Set up environment variables
cp .env.example .env
# Add your API keys to .env
```

### Directory Structure

```
tests/evaluation/
├── test_full_session_evaluation.py  # Main evaluation test suite
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── screenshots/                     # Captured screenshots (auto-created)
├── reports/                        # Generated reports (auto-created)
│   ├── evaluation_report_*.html   # Detailed HTML reports
│   ├── summary_*.json             # Summary metrics for CI/CD
│   └── junit.xml                  # JUnit format for CI integration
└── test_scenarios/                 # Additional test scenarios (optional)
```

## Usage

### Running Locally

```bash
# Start the API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Start the Web UI (in another terminal)
cd web && python3 -m http.server 8081

# Run evaluation tests (in another terminal)
pytest tests/evaluation/test_full_session_evaluation.py -v

# Run with HTML report
pytest tests/evaluation/test_full_session_evaluation.py \
  --html=tests/evaluation/reports/report.html \
  --self-contained-html

# Run specific scenario
pytest tests/evaluation/test_full_session_evaluation.py::test_full_coaching_session[Tech Startup Strategy] -v

# Run in parallel
pytest tests/evaluation/test_full_session_evaluation.py -n auto
```

### Manual Evaluation

```python
# Run evaluation script directly
python tests/evaluation/test_full_session_evaluation.py
```

### CI/CD Pipeline

The evaluation automatically runs on:
- Push to main/develop branches
- Pull requests
- Daily schedule (2 AM UTC)
- Manual workflow dispatch

```yaml
# Trigger manually via GitHub Actions
workflow_dispatch:
  inputs:
    scenarios: 'all'  # or 'quick', 'full'
```

## Test Scenarios

### Pre-configured Scenarios

1. **Tech Startup Strategy**
   - B2B SaaS focus
   - Tests all four agents
   - 12 conversation turns
   - High quality thresholds

2. **Non-Profit Mission Alignment**
   - Education focus
   - Tests WHY and Open Strategy
   - 10 conversation turns
   - Moderate thresholds

3. **Enterprise Digital Transformation**
   - Retail industry
   - Complex multi-agent flow
   - 15 conversation turns
   - Comprehensive coverage

### Adding Custom Scenarios

```python
from test_full_session_evaluation import TestScenario

custom_scenario = TestScenario(
    name="Healthcare Innovation",
    description="Strategy for healthcare tech startup",
    initial_message="We're building AI for medical diagnosis...",
    expected_agents=["WHY", "Logic", "Open Strategy"],
    expected_topics=["healthcare", "AI", "regulation", "ethics"],
    conversation_turns=10,
    success_criteria={
        'min_relevancy': 0.75,
        'min_completeness': 0.65,
        'min_routing_accuracy': 0.6,
        'min_coherence': 0.7
    }
)
```

## Metrics Explained

### Core Metrics

| Metric | Description | Threshold | Calculation |
|--------|-------------|-----------|-------------|
| **Answer Relevancy** | How well responses address user queries | 0.6-0.7 | DeepEval semantic similarity |
| **Faithfulness** | Consistency with strategic framework | 0.7 | DeepEval fact-checking |
| **Strategic Quality** | Business value of insights | 0.6-0.7 | Custom GEval criteria |
| **Map Completeness** | % of strategy map fields populated | 0.5-0.65 | Field counting algorithm |
| **Routing Accuracy** | Correct agent selection rate | 0.5-0.6 | Sequence matching |
| **Conversation Coherence** | Logical flow between turns | 0.6-0.7 | Semantic overlap analysis |

### Success Criteria

- **PASS**: All metrics meet threshold requirements
- **FAIL**: One or more metrics below threshold
- **Quality Gate**: Overall success rate ≥ 80%

## Reports

### HTML Report

Generated after each evaluation run:
- Visual summary with charts
- Per-scenario breakdown
- Screenshots gallery
- Conversation samples
- Strategy map JSON
- Failure analysis

### JSON Summary

Machine-readable metrics for CI/CD:
```json
{
  "total_scenarios": 3,
  "passed": 2,
  "failed": 1,
  "success_rate": 66.67,
  "timestamp": "2024-08-15T10:30:00Z"
}
```

### JUnit XML

Standard test reporting format for CI tools:
- Test case results
- Execution times
- Error messages
- Stack traces

## Troubleshooting

### Common Issues

1. **Timeout Errors**
   - Increase `TIMEOUT_MS` in test file
   - Check API server is running
   - Verify LLM API keys are valid

2. **Low Scores**
   - Review conversation logs
   - Check agent prompts
   - Adjust success thresholds

3. **Screenshot Failures**
   - Ensure Playwright is installed
   - Check browser permissions
   - Verify display server (headless mode)

4. **CI/CD Failures**
   - Check secrets configuration
   - Verify network connectivity
   - Review workflow logs

### Debug Mode

```python
# Run with visible browser
evaluator = StrategyCoachEvaluator(headless=False)

# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Save intermediate states
evaluator.save_debug_info = True
```

## Best Practices

1. **Test Data Management**
   - Keep scenarios focused and realistic
   - Update expected outcomes regularly
   - Version control test configurations

2. **Performance Optimization**
   - Run tests in parallel when possible
   - Cache LLM responses for development
   - Use smaller models for quick tests

3. **Continuous Improvement**
   - Review failed tests weekly
   - Update thresholds based on baseline
   - Add new scenarios for edge cases

4. **Integration with Development**
   - Run subset of tests in pre-commit
   - Full suite on PR/merge
   - Monitor trends over time

## Advanced Features

### Custom Metrics

```python
from deepeval.metrics import BaseMetric

class BusinessValueMetric(BaseMetric):
    def measure(self, test_case):
        # Custom evaluation logic
        score = evaluate_business_value(test_case)
        return score
```

### LangSmith Integration

```python
from langsmith import Client

client = Client()
# Track evaluations in LangSmith
```

### Performance Profiling

```python
import cProfile
profiler = cProfile.Profile()
profiler.enable()
# Run tests
profiler.disable()
profiler.dump_stats('evaluation.prof')
```

## Contributing

1. Add test scenarios to cover new features
2. Update metrics when adding agents
3. Document threshold changes
4. Include screenshots in reports

## License

See main project LICENSE file.