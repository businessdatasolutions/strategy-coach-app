"""
End-to-End Evaluation Suite for AI Strategic Co-pilot
=====================================================
Professional evaluation system for multi-agent coaching workflow with:
- Full session simulation from WHY to implementation
- Strategy map completeness validation
- Agent routing verification
- Response quality assessment
- Screenshots and intermediate state capture
- CI/CD integration support
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import pytest
from playwright.sync_api import sync_playwright, Page, Browser
from playwright.async_api import async_playwright
import httpx
from deepeval import evaluate, assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    GEval,
    ContextualRelevancyMetric,
)
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.dataset import EvaluationDataset, Golden


# ==================== Configuration ====================

@dataclass
class EvaluationConfig:
    """Configuration for evaluation runs."""
    api_base_url: str = "http://localhost:8000"
    ui_base_url: str = "http://localhost:8081"
    screenshot_dir: Path = field(default_factory=lambda: Path("tests/evaluation/screenshots"))
    report_dir: Path = field(default_factory=lambda: Path("tests/evaluation/reports"))
    timeout_seconds: int = 120
    enable_screenshots: bool = True
    enable_video: bool = False
    ci_mode: bool = os.getenv("CI", "false").lower() == "true"
    
    def __post_init__(self):
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)


# ==================== Evaluation Metrics ====================

class StrategyCoachMetrics:
    """Custom metrics for strategy coaching evaluation."""
    
    @staticmethod
    def get_strategy_completeness_metric() -> GEval:
        """Metric for evaluating strategy map completeness."""
        return GEval(
            name="StrategyCompleteness",
            criteria=(
                "Evaluate if the strategy map contains: "
                "1) Clear WHY (purpose, beliefs, values), "
                "2) Stakeholder value propositions, "
                "3) Internal processes defined, "
                "4) Learning & growth capabilities, "
                "5) Value creation model"
            ),
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.CONTEXT
            ],
            threshold=0.7
        )
    
    @staticmethod
    def get_coaching_quality_metric() -> GEval:
        """Metric for evaluating coaching conversation quality."""
        return GEval(
            name="CoachingQuality",
            criteria=(
                "Evaluate the coaching quality based on: "
                "1) Questions are strategic not tactical, "
                "2) Progression from WHY to HOW to WHAT, "
                "3) Use of appropriate methodologies (Sinek, Carroll & Sørensen), "
                "4) Clear guidance and direction, "
                "5) Synthesis of user inputs into coherent strategy"
            ),
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT
            ],
            threshold=0.75
        )
    
    @staticmethod
    def get_agent_routing_accuracy_metric() -> GEval:
        """Metric for evaluating agent routing decisions."""
        return GEval(
            name="AgentRoutingAccuracy",
            criteria=(
                "Evaluate if the correct specialist agent was selected based on: "
                "1) WHY Agent for purpose/belief questions, "
                "2) Analogy Agent for pattern/comparison needs, "
                "3) Logic Agent for validation/consistency checks, "
                "4) Open Strategy Agent for implementation planning"
            ),
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.CONTEXT
            ],
            threshold=0.8
        )


# ==================== Test Data ====================

@dataclass
class CoachingScenario:
    """Test scenario for coaching session."""
    name: str
    company_context: Dict[str, str]
    user_messages: List[str]
    expected_outcomes: Dict[str, Any]
    expected_agent_sequence: List[str]
    
    
def get_test_scenarios() -> List[CoachingScenario]:
    """Get comprehensive test scenarios."""
    return [
        CoachingScenario(
            name="tech_startup_devops",
            company_context={
                "company_name": "TechCorp Solutions",
                "industry": "Software Development",
                "size": "500 employees",
                "challenge": "Slow delivery cycles"
            },
            user_messages=[
                # WHY Phase
                "We're a software company struggling with slow delivery cycles. We need to implement DevOps but need a strategy.",
                "We believe that technology should enable rapid innovation and continuous improvement for our clients.",
                "Our core values are automation, collaboration, and continuous learning.",
                
                # HOW Phase  
                "Companies like Netflix and Spotify seem to deploy continuously. How did they achieve this?",
                "Our current process has manual testing, separate dev/ops teams, and quarterly releases.",
                
                # WHAT Phase
                "What specific steps should we take to implement this transformation?",
                "How do we get buy-in from leadership and the development teams?"
            ],
            expected_outcomes={
                "why_complete": True,
                "perspectives_developed": ["stakeholder_customer", "internal_processes"],
                "specialist_agents_used": ["why_agent", "analogy_agent", "open_strategy_agent"],
                "completeness_min": 60,
                "has_implementation_plan": True
            },
            expected_agent_sequence=["why_agent", "why_agent", "why_agent", "analogy_agent", "logic_agent", "open_strategy_agent", "open_strategy_agent"]
        ),
        CoachingScenario(
            name="retail_digital_transformation",
            company_context={
                "company_name": "RetailChain Inc",
                "industry": "Retail",
                "size": "5000 employees",
                "challenge": "Digital transformation"
            },
            user_messages=[
                # WHY Phase
                "We're a traditional retail chain that needs to compete with e-commerce. Need a digital strategy.",
                "We exist to provide personalized shopping experiences that blend physical and digital seamlessly.",
                "Customer obsession, innovation, and community connection are our core values.",
                
                # HOW Phase
                "Target successfully transformed from pure retail to omnichannel. What can we learn?",
                "We have physical stores, basic e-commerce, but no integration between channels.",
                
                # WHAT Phase
                "What's our implementation roadmap for omnichannel transformation?",
                "How do we measure success of this transformation?"
            ],
            expected_outcomes={
                "why_complete": True,
                "perspectives_developed": ["stakeholder_customer", "internal_processes", "learning_growth"],
                "specialist_agents_used": ["why_agent", "analogy_agent", "logic_agent", "open_strategy_agent"],
                "completeness_min": 70,
                "has_implementation_plan": True
            },
            expected_agent_sequence=["why_agent", "why_agent", "why_agent", "analogy_agent", "logic_agent", "open_strategy_agent", "open_strategy_agent"]
        )
    ]


# ==================== API Client ====================

class StrategyCoachAPIClient:
    """Client for interacting with Strategy Coach API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
        
    def health_check(self) -> bool:
        """Check if API is healthy."""
        try:
            response = self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def start_session(self, company_context: Dict[str, str]) -> str:
        """Start a new coaching session."""
        response = self.client.post(
            f"{self.base_url}/conversation/start",
            json={"user_context": company_context}
        )
        response.raise_for_status()
        return response.json()["session_id"]
    
    def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Send a message in the conversation."""
        response = self.client.post(
            f"{self.base_url}/conversation/{session_id}/message",
            json={"message": message}
        )
        response.raise_for_status()
        return response.json()
    
    def get_strategy_map(self, session_id: str) -> Dict[str, Any]:
        """Get the current strategy map."""
        response = self.client.get(
            f"{self.base_url}/conversation/{session_id}/export"
        )
        response.raise_for_status()
        return response.json()["strategy_map"]
    
    def cleanup(self):
        """Cleanup client resources."""
        self.client.close()


# ==================== UI Automation ====================

class StrategyCoachUIAutomation:
    """Playwright-based UI automation for Strategy Coach."""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.screenshots: List[str] = []
        
    def start(self):
        """Start browser and navigate to UI."""
        self.playwright = sync_playwright().start()
        
        launch_options = {
            "headless": self.config.ci_mode,
            "slow_mo": 0 if self.config.ci_mode else 500
        }
        
        if self.config.enable_video:
            launch_options["record_video_dir"] = str(self.config.report_dir / "videos")
            
        self.browser = self.playwright.chromium.launch(**launch_options)
        self.page = self.browser.new_page()
        self.page.goto(self.config.ui_base_url)
        
        # Wait for UI to load
        self.page.wait_for_selector('button:has-text("New Session")', timeout=10000)
        
    def start_new_session(self) -> str:
        """Start a new session via UI."""
        # Click new session button
        self.page.click('button:has-text("New Session")')
        
        # Wait for welcome message
        self.page.wait_for_selector('.message-fade-in', timeout=10000)
        
        # Extract session ID from UI state (if visible)
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.config.enable_screenshots:
            self.take_screenshot(f"session_start_{session_id}")
            
        return session_id
    
    def send_message(self, message: str):
        """Send a message via UI."""
        # Type message
        input_field = self.page.locator('input[type="text"]')
        input_field.fill(message)
        
        # Press Enter or click Send
        input_field.press("Enter")
        
        # Wait for response
        self.page.wait_for_selector('.typing-indicator', state="visible", timeout=5000)
        self.page.wait_for_selector('.typing-indicator', state="hidden", timeout=30000)
        
    def take_screenshot(self, name: str):
        """Take a screenshot."""
        if not self.config.enable_screenshots:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.png"
        filepath = self.config.screenshot_dir / filename
        
        self.page.screenshot(path=str(filepath))
        self.screenshots.append(str(filepath))
        
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Extract conversation history from UI."""
        messages = []
        message_elements = self.page.locator('.message-fade-in').all()
        
        for element in message_elements:
            role = "user" if "user" in element.get_attribute("class") else "assistant"
            content = element.inner_text()
            messages.append({"role": role, "content": content})
            
        return messages
    
    def get_ui_metrics(self) -> Dict[str, Any]:
        """Extract UI metrics and state."""
        metrics = {}
        
        # Get completeness percentage
        completeness_elem = self.page.locator('text=/\\d+%/').first
        if completeness_elem:
            metrics["completeness"] = completeness_elem.inner_text()
            
        # Get current phase
        phase_indicators = self.page.locator('.phase-indicator.active')
        if phase_indicators.count() > 0:
            metrics["current_phase"] = phase_indicators.first.inner_text()
            
        # Get active agent
        agent_elem = self.page.locator('text=/Active Agent:.*/')
        if agent_elem.count() > 0:
            metrics["active_agent"] = agent_elem.first.inner_text()
            
        return metrics
    
    def cleanup(self):
        """Cleanup browser resources."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


# ==================== Evaluation Engine ====================

class StrategyCoachEvaluator:
    """Main evaluation engine for Strategy Coach."""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.api_client = StrategyCoachAPIClient(config.api_base_url)
        self.ui_automation = StrategyCoachUIAutomation(config) if not config.ci_mode else None
        self.results = []
        
    def evaluate_scenario(self, scenario: CoachingScenario) -> Dict[str, Any]:
        """Evaluate a single coaching scenario."""
        print(f"\n{'='*60}")
        print(f"Evaluating Scenario: {scenario.name}")
        print(f"{'='*60}")
        
        result = {
            "scenario": scenario.name,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "metrics": {},
            "errors": [],
            "artifacts": {}
        }
        
        try:
            # Start session
            session_id = self.api_client.start_session(scenario.company_context)
            result["session_id"] = session_id
            print(f"✓ Session started: {session_id}")
            
            # UI automation if enabled
            if self.ui_automation and not self.config.ci_mode:
                self.ui_automation.start()
                self.ui_automation.start_new_session()
            
            # Execute conversation
            conversation_history = []
            agent_sequence = []
            
            for i, message in enumerate(scenario.user_messages):
                print(f"\n→ User Message {i+1}: {message[:50]}...")
                
                # Send via API
                response = self.api_client.send_message(session_id, message)
                
                # Track conversation
                conversation_history.append({"role": "user", "content": message})
                conversation_history.append({"role": "assistant", "content": response["response"]})
                
                # Track agent routing
                if "current_agent" in response:
                    agent_sequence.append(response["current_agent"])
                    print(f"  Agent: {response['current_agent']}")
                
                # Track metrics
                print(f"  Phase: {response.get('current_phase', 'unknown')}")
                print(f"  Completeness: {response.get('completeness_percentage', 0):.1f}%")
                
                # UI automation
                if self.ui_automation and not self.config.ci_mode:
                    self.ui_automation.send_message(message)
                    self.ui_automation.take_screenshot(f"message_{i+1}")
                    
                # Small delay between messages
                time.sleep(1)
            
            # Get final strategy map
            strategy_map = self.api_client.get_strategy_map(session_id)
            result["strategy_map"] = strategy_map
            
            # Evaluate outcomes
            evaluation_results = self._evaluate_outcomes(
                scenario, 
                strategy_map, 
                conversation_history,
                agent_sequence
            )
            result["metrics"] = evaluation_results["metrics"]
            result["success"] = evaluation_results["success"]
            
            # Save artifacts
            result["artifacts"] = {
                "conversation": conversation_history,
                "agent_sequence": agent_sequence,
                "strategy_map_path": self._save_strategy_map(session_id, strategy_map)
            }
            
            if self.ui_automation:
                result["artifacts"]["screenshots"] = self.ui_automation.screenshots
                
            print(f"\n✓ Scenario completed successfully")
            
        except Exception as e:
            result["errors"].append(str(e))
            print(f"\n✗ Scenario failed: {e}")
            
        finally:
            if self.ui_automation and not self.config.ci_mode:
                self.ui_automation.cleanup()
                
        return result
    
    def _evaluate_outcomes(
        self, 
        scenario: CoachingScenario,
        strategy_map: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        agent_sequence: List[str]
    ) -> Dict[str, Any]:
        """Evaluate scenario outcomes against expectations."""
        
        metrics = {}
        success = True
        
        # Check WHY completion
        why_complete = bool(
            strategy_map.get("why", {}).get("purpose") and
            strategy_map.get("why", {}).get("beliefs") and
            strategy_map.get("why", {}).get("values")
        )
        metrics["why_complete"] = why_complete
        if scenario.expected_outcomes["why_complete"] and not why_complete:
            success = False
            print(f"  ✗ WHY not complete")
        else:
            print(f"  ✓ WHY complete")
        
        # Check completeness percentage
        completeness = strategy_map.get("completeness_percentage", 0)
        metrics["completeness"] = completeness
        if completeness < scenario.expected_outcomes["completeness_min"]:
            success = False
            print(f"  ✗ Completeness {completeness:.1f}% < {scenario.expected_outcomes['completeness_min']}%")
        else:
            print(f"  ✓ Completeness {completeness:.1f}% ≥ {scenario.expected_outcomes['completeness_min']}%")
        
        # Check perspectives developed
        completed_sections = strategy_map.get("completed_sections", [])
        for perspective in scenario.expected_outcomes["perspectives_developed"]:
            if perspective not in completed_sections:
                success = False
                print(f"  ✗ Perspective '{perspective}' not developed")
            else:
                print(f"  ✓ Perspective '{perspective}' developed")
        
        # Check specialist agents used
        unique_agents = set(agent_sequence)
        for expected_agent in scenario.expected_outcomes["specialist_agents_used"]:
            if expected_agent not in unique_agents:
                success = False
                print(f"  ✗ Agent '{expected_agent}' not used")
            else:
                print(f"  ✓ Agent '{expected_agent}' used")
        
        # Check implementation plan
        has_implementation = bool(strategy_map.get("implementation_plan"))
        metrics["has_implementation_plan"] = has_implementation
        if scenario.expected_outcomes["has_implementation_plan"] and not has_implementation:
            success = False
            print(f"  ✗ Implementation plan missing")
        else:
            print(f"  ✓ Implementation plan present")
        
        # DeepEval metrics
        test_cases = self._create_deepeval_test_cases(
            scenario,
            conversation_history,
            strategy_map
        )
        
        deepeval_metrics = [
            StrategyCoachMetrics.get_strategy_completeness_metric(),
            StrategyCoachMetrics.get_coaching_quality_metric(),
            AnswerRelevancyMetric(threshold=0.7),
        ]
        
        # Run DeepEval
        eval_results = evaluate(test_cases, deepeval_metrics, print_results=False)
        
        metrics["deepeval_scores"] = {
            metric.name: metric.score for metric in deepeval_metrics
        }
        
        return {
            "metrics": metrics,
            "success": success and eval_results
        }
    
    def _create_deepeval_test_cases(
        self,
        scenario: CoachingScenario,
        conversation_history: List[Dict[str, str]],
        strategy_map: Dict[str, Any]
    ) -> List[LLMTestCase]:
        """Create DeepEval test cases from scenario results."""
        
        test_cases = []
        
        # Create test case for overall coaching quality
        full_conversation = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation_history
        ])
        
        test_cases.append(
            LLMTestCase(
                input=scenario.company_context.get("challenge", ""),
                actual_output=full_conversation,
                context=[json.dumps(strategy_map)]
            )
        )
        
        # Create test cases for individual responses
        for i in range(0, len(conversation_history) - 1, 2):
            user_msg = conversation_history[i]["content"]
            assistant_msg = conversation_history[i + 1]["content"]
            
            test_cases.append(
                LLMTestCase(
                    input=user_msg,
                    actual_output=assistant_msg
                )
            )
            
        return test_cases
    
    def _save_strategy_map(self, session_id: str, strategy_map: Dict[str, Any]) -> str:
        """Save strategy map to file."""
        filepath = self.config.report_dir / f"strategy_map_{session_id}.json"
        with open(filepath, "w") as f:
            json.dump(strategy_map, f, indent=2)
        return str(filepath)
    
    def run_evaluation_suite(self) -> Dict[str, Any]:
        """Run complete evaluation suite."""
        print("\n" + "="*60)
        print("STRATEGY COACH EVALUATION SUITE")
        print("="*60)
        
        # Check API health
        if not self.api_client.health_check():
            raise RuntimeError("API health check failed. Ensure the server is running.")
        print("✓ API health check passed")
        
        # Run scenarios
        scenarios = get_test_scenarios()
        suite_results = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "api_url": self.config.api_base_url,
                "ui_url": self.config.ui_base_url,
                "ci_mode": self.config.ci_mode
            },
            "scenarios": [],
            "summary": {
                "total": len(scenarios),
                "passed": 0,
                "failed": 0
            }
        }
        
        for scenario in scenarios:
            result = self.evaluate_scenario(scenario)
            suite_results["scenarios"].append(result)
            
            if result["success"]:
                suite_results["summary"]["passed"] += 1
            else:
                suite_results["summary"]["failed"] += 1
        
        # Generate report
        self._generate_report(suite_results)
        
        print("\n" + "="*60)
        print("EVALUATION COMPLETE")
        print(f"Passed: {suite_results['summary']['passed']}/{suite_results['summary']['total']}")
        print("="*60)
        
        return suite_results
    
    def _generate_report(self, results: Dict[str, Any]):
        """Generate evaluation report."""
        
        # JSON report
        json_report_path = self.config.report_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_report_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ JSON report saved: {json_report_path}")
        
        # Markdown report
        md_report_path = self.config.report_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(md_report_path, "w") as f:
            f.write("# Strategy Coach Evaluation Report\n\n")
            f.write(f"**Date**: {results['timestamp']}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- Total Scenarios: {results['summary']['total']}\n")
            f.write(f"- Passed: {results['summary']['passed']}\n")
            f.write(f"- Failed: {results['summary']['failed']}\n\n")
            
            f.write("## Scenario Results\n\n")
            for scenario_result in results["scenarios"]:
                f.write(f"### {scenario_result['scenario']}\n\n")
                f.write(f"- **Status**: {'✓ PASSED' if scenario_result['success'] else '✗ FAILED'}\n")
                f.write(f"- **Session ID**: {scenario_result.get('session_id', 'N/A')}\n")
                
                if scenario_result.get("metrics"):
                    f.write(f"- **Metrics**:\n")
                    for key, value in scenario_result["metrics"].items():
                        f.write(f"  - {key}: {value}\n")
                
                if scenario_result.get("errors"):
                    f.write(f"- **Errors**:\n")
                    for error in scenario_result["errors"]:
                        f.write(f"  - {error}\n")
                        
                f.write("\n")
                
        print(f"✓ Markdown report saved: {md_report_path}")


# ==================== Test Functions ====================

@pytest.fixture
def evaluation_config():
    """Pytest fixture for evaluation config."""
    return EvaluationConfig()


@pytest.fixture
def evaluator(evaluation_config):
    """Pytest fixture for evaluator."""
    return StrategyCoachEvaluator(evaluation_config)


def test_full_coaching_session(evaluator):
    """Test complete coaching session end-to-end."""
    results = evaluator.run_evaluation_suite()
    
    # Assert all scenarios passed
    assert results["summary"]["failed"] == 0, f"Failed scenarios: {results['summary']['failed']}"
    
    # Assert minimum completeness achieved
    for scenario_result in results["scenarios"]:
        if scenario_result["success"]:
            metrics = scenario_result.get("metrics", {})
            assert metrics.get("completeness", 0) >= 50, f"Low completeness: {metrics.get('completeness', 0)}"
            assert metrics.get("why_complete", False), "WHY phase not completed"


def test_individual_scenario_tech_startup(evaluator):
    """Test tech startup DevOps scenario."""
    scenarios = get_test_scenarios()
    tech_scenario = [s for s in scenarios if s.name == "tech_startup_devops"][0]
    
    result = evaluator.evaluate_scenario(tech_scenario)
    
    assert result["success"], f"Scenario failed: {result.get('errors')}"
    assert result["metrics"]["completeness"] >= 60
    assert result["metrics"]["why_complete"]
    assert result["metrics"]["has_implementation_plan"]


# ==================== CI/CD Integration ====================

def run_ci_evaluation():
    """Run evaluation in CI/CD mode."""
    config = EvaluationConfig(ci_mode=True)
    evaluator = StrategyCoachEvaluator(config)
    
    try:
        results = evaluator.run_evaluation_suite()
        
        # Exit with appropriate code for CI/CD
        if results["summary"]["failed"] > 0:
            print(f"\n✗ EVALUATION FAILED: {results['summary']['failed']} scenarios failed")
            exit(1)
        else:
            print(f"\n✓ EVALUATION PASSED: All {results['summary']['total']} scenarios passed")
            exit(0)
            
    except Exception as e:
        print(f"\n✗ EVALUATION ERROR: {e}")
        exit(1)


if __name__ == "__main__":
    # Run in CI mode if CI environment variable is set
    if os.getenv("CI"):
        run_ci_evaluation()
    else:
        # Run interactively with UI automation
        config = EvaluationConfig(ci_mode=False, enable_screenshots=True)
        evaluator = StrategyCoachEvaluator(config)
        evaluator.run_evaluation_suite()