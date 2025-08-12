import pytest
from unittest.mock import patch, MagicMock

from src.utils.prompts import (
    PromptConfig, 
    PromptTemplateManager, 
    PromptOptimizer,
    get_prompt_manager,
    get_prompt_optimizer
)


class TestPromptConfig:
    """Test the PromptConfig class functionality."""
    
    def test_prompt_config_initialization_default(self):
        """Test PromptConfig initialization with default values."""
        config = PromptConfig()
        
        assert config.prompt_version == "1.0.0"
        assert config.default_temperature == 0.7
        assert config.max_tokens == 4000
        assert config.enable_prompt_caching is True
        assert config.prompt_validation is True
        
    def test_prompt_config_methodology_settings(self):
        """Test PromptConfig methodology settings."""
        config = PromptConfig()
        
        # Check WHY agent settings
        why_settings = config.methodology_settings["why_agent"]
        assert why_settings["methodology_name"] == "Simon Sinek's Golden Circle"
        assert "purpose_discovery" in why_settings["focus_areas"]
        assert why_settings["prompt_style"] == "socratic_questioning"
        
        # Check Analogy agent settings
        analogy_settings = config.methodology_settings["analogy_agent"]
        assert analogy_settings["methodology_name"] == "Carroll & Sørensen's Analogical Reasoning"
        assert "source_identification" in analogy_settings["focus_areas"]
        assert analogy_settings["prompt_style"] == "analytical_reasoning"
        
        # Check Logic agent settings
        logic_settings = config.methodology_settings["logic_agent"]
        assert logic_settings["methodology_name"] == "Deductive Argument Validation"
        assert "argument_analysis" in logic_settings["focus_areas"]
        assert logic_settings["prompt_style"] == "logical_analysis"
        
        # Check Open Strategy agent settings
        open_strategy_settings = config.methodology_settings["open_strategy_agent"]
        assert open_strategy_settings["methodology_name"] == "Open Strategy Implementation"
        assert "stakeholder_analysis" in open_strategy_settings["focus_areas"]
        assert open_strategy_settings["prompt_style"] == "practical_planning"
    
    def test_prompt_config_agent_focus_areas(self):
        """Test that each agent has exactly 4 focus areas."""
        config = PromptConfig()
        
        for agent_type, settings in config.methodology_settings.items():
            assert len(settings["focus_areas"]) == 4, f"{agent_type} should have 4 focus areas"


class TestPromptTemplateManager:
    """Test the PromptTemplateManager class functionality."""
    
    def test_prompt_manager_initialization_default(self):
        """Test PromptTemplateManager initialization with default config."""
        manager = PromptTemplateManager()
        
        assert manager.config is not None
        assert isinstance(manager.config, PromptConfig)
        assert len(manager.templates) > 0
    
    def test_prompt_manager_initialization_custom_config(self):
        """Test PromptTemplateManager initialization with custom config."""
        custom_config = PromptConfig()
        custom_config.max_tokens = 6000
        manager = PromptTemplateManager(config=custom_config)
        
        assert manager.config == custom_config
        assert manager.config.max_tokens == 6000
    
    def test_get_why_agent_prompts(self):
        """Test WHY Agent prompt retrieval."""
        manager = PromptTemplateManager()
        
        # Test all WHY Agent prompts exist
        purpose_discovery = manager.get_template("why_agent", "purpose_discovery")
        belief_exploration = manager.get_template("why_agent", "belief_exploration")
        values_integration = manager.get_template("why_agent", "values_integration")
        synthesis = manager.get_template("why_agent", "synthesis")
        
        assert purpose_discovery is not None
        assert belief_exploration is not None
        assert values_integration is not None
        assert synthesis is not None
        
        # Verify prompts contain expected methodology keywords
        assert "Golden Circle" in purpose_discovery.template
        assert "Simon Sinek" in purpose_discovery.template
        assert "WHY" in purpose_discovery.template
    
    def test_get_analogy_agent_prompts(self):
        """Test Analogy Agent prompt retrieval."""
        manager = PromptTemplateManager()
        
        # Test all Analogy Agent prompts exist
        source_identification = manager.get_prompt("analogy_agent", "source_identification")
        structural_mapping = manager.get_prompt("analogy_agent", "structural_mapping")
        evaluation = manager.get_prompt("analogy_agent", "evaluation")
        integration = manager.get_prompt("analogy_agent", "integration")
        
        assert source_identification is not None
        assert structural_mapping is not None
        assert evaluation is not None
        assert integration is not None
        
        # Verify prompts contain expected methodology keywords
        assert "analogical reasoning" in source_identification.template
        assert "Carroll" in source_identification.template
        assert "Sørensen" in source_identification.template
    
    def test_get_logic_agent_prompts(self):
        """Test Logic Agent prompt retrieval."""
        manager = PromptTemplateManager()
        
        # Test all Logic Agent prompts exist
        argument_analysis = manager.get_prompt("logic_agent", "argument_analysis")
        validity_assessment = manager.get_prompt("logic_agent", "validity_assessment")
        soundness_evaluation = manager.get_prompt("logic_agent", "soundness_evaluation")
        framework_construction = manager.get_prompt("logic_agent", "framework_construction")
        
        assert argument_analysis is not None
        assert validity_assessment is not None
        assert soundness_evaluation is not None
        assert framework_construction is not None
        
        # Verify prompts contain expected methodology keywords
        assert "deductive" in argument_analysis.template
        assert "logical" in argument_analysis.template
        assert "premises" in argument_analysis.template
    
    def test_get_open_strategy_agent_prompts(self):
        """Test Open Strategy Agent prompt retrieval."""
        manager = PromptTemplateManager()
        
        # Test all Open Strategy Agent prompts exist
        stakeholder_analysis = manager.get_prompt("open_strategy_agent", "stakeholder_analysis")
        process_design = manager.get_prompt("open_strategy_agent", "process_design")
        resource_planning = manager.get_prompt("open_strategy_agent", "resource_planning")
        implementation_roadmap = manager.get_prompt("open_strategy_agent", "implementation_roadmap")
        
        assert stakeholder_analysis is not None
        assert process_design is not None
        assert resource_planning is not None
        assert implementation_roadmap is not None
        
        # Verify prompts contain expected methodology keywords
        assert "stakeholder" in stakeholder_analysis.template
        assert "implementation" in stakeholder_analysis.template
        assert "open strategy" in stakeholder_analysis.template
    
    def test_get_shared_prompts(self):
        """Test shared prompt templates."""
        manager = PromptTemplateManager()
        
        # Test shared prompts exist
        fallback = manager.get_prompt("shared", "fallback_response")
        context_extraction = manager.get_prompt("shared", "context_extraction")
        error_recovery = manager.get_prompt("shared", "error_recovery")
        
        assert fallback is not None
        assert context_extraction is not None
        assert error_recovery is not None
        
        # Verify shared prompts are generic
        assert "strategy" in fallback.template
        assert "conversation" in context_extraction.template
    
    def test_get_prompt_invalid_agent(self):
        """Test getting prompt for invalid agent."""
        manager = PromptTemplateManager()
        
        prompt = manager.get_prompt("invalid_agent", "some_stage")
        assert prompt is None
    
    def test_get_prompt_invalid_stage(self):
        """Test getting prompt for invalid stage."""
        manager = PromptTemplateManager()
        
        prompt = manager.get_prompt("why_agent", "invalid_stage")
        assert prompt is None
    
    def test_list_agents(self):
        """Test listing available agents."""
        manager = PromptTemplateManager()
        
        agents = manager.list_agents()
        
        expected_agents = ["why_agent", "analogy_agent", "logic_agent", "open_strategy_agent", "shared"]
        for agent in expected_agents:
            assert agent in agents
    
    def test_list_stages_for_agent(self):
        """Test listing stages for specific agents."""
        manager = PromptTemplateManager()
        
        # Test WHY Agent stages
        why_stages = manager.list_stages("why_agent")
        expected_why_stages = ["purpose_discovery", "purpose_clarification", "purpose_validation", "purpose_integration"]
        for stage in expected_why_stages:
            assert stage in why_stages
        
        # Test Analogy Agent stages
        analogy_stages = manager.list_stages("analogy_agent")
        expected_analogy_stages = ["source_identification", "structural_mapping", "evaluation", "integration"]
        for stage in expected_analogy_stages:
            assert stage in analogy_stages
        
        # Test Logic Agent stages
        logic_stages = manager.list_stages("logic_agent")
        expected_logic_stages = ["argument_analysis", "validity_assessment", "soundness_evaluation", "framework_construction"]
        for stage in expected_logic_stages:
            assert stage in logic_stages
        
        # Test Open Strategy Agent stages
        open_strategy_stages = manager.list_stages("open_strategy_agent")
        expected_open_strategy_stages = ["stakeholder_analysis", "process_design", "resource_planning", "implementation_roadmap"]
        for stage in expected_open_strategy_stages:
            assert stage in open_strategy_stages
    
    def test_list_stages_invalid_agent(self):
        """Test listing stages for invalid agent."""
        manager = PromptTemplateManager()
        
        stages = manager.list_stages("invalid_agent")
        assert stages == []
    
    def test_update_config(self):
        """Test updating configuration."""
        manager = PromptTemplateManager()
        
        original_style = manager.config.response_style
        
        new_config = PromptConfig(response_style="casual", use_examples=False)
        manager.update_config(new_config)
        
        assert manager.config.response_style == "casual"
        assert manager.config.use_examples is False
        assert manager.config.response_style != original_style
    
    def test_prompt_template_formatting(self):
        """Test that prompts can be formatted with variables."""
        manager = PromptTemplateManager()
        
        why_prompt = manager.get_prompt("why_agent", "purpose_discovery")
        
        # Test that prompt template has expected input variables
        expected_variables = ["conversation_context", "user_input", "strategic_context"]
        for var in expected_variables:
            assert var in why_prompt.input_variables
        
        # Test formatting the prompt
        formatted = why_prompt.format(
            conversation_context="Test conversation",
            user_input="What is our purpose?",
            strategic_context="Technology company"
        )
        
        assert "Test conversation" in formatted
        assert "What is our purpose?" in formatted
        assert "Technology company" in formatted


class TestPromptOptimizer:
    """Test the PromptOptimizer class functionality."""
    
    def test_prompt_optimizer_initialization(self):
        """Test PromptOptimizer initialization."""
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        assert optimizer.prompt_manager == manager
        assert hasattr(optimizer, 'test_scenarios')
        assert len(optimizer.test_scenarios) > 0
    
    def test_validate_prompt_structure(self):
        """Test prompt structure validation."""
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        # Test valid prompt
        why_prompt = manager.get_prompt("why_agent", "purpose_discovery")
        is_valid, issues = optimizer.validate_prompt_structure(why_prompt)
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_validate_prompt_structure_invalid(self):
        """Test prompt structure validation with invalid prompt."""
        from langchain.prompts import PromptTemplate
        
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        # Create invalid prompt (no input variables)
        invalid_prompt = PromptTemplate(
            input_variables=[],
            template="This is a static template with no variables"
        )
        
        is_valid, issues = optimizer.validate_prompt_structure(invalid_prompt)
        
        assert is_valid is False
        assert len(issues) > 0
        assert "No input variables defined" in issues[0]
    
    def test_get_test_scenarios(self):
        """Test getting test scenarios for agents."""
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        # Test getting scenarios for WHY agent
        why_scenarios = optimizer.get_test_scenarios("why_agent")
        assert len(why_scenarios) > 0
        assert "purpose_discovery" in why_scenarios[0]
        
        # Test getting scenarios for Analogy agent
        analogy_scenarios = optimizer.get_test_scenarios("analogy_agent")
        assert len(analogy_scenarios) > 0
        assert "source_identification" in analogy_scenarios[0]
    
    def test_get_test_scenarios_invalid_agent(self):
        """Test getting test scenarios for invalid agent."""
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        scenarios = optimizer.get_test_scenarios("invalid_agent")
        assert scenarios == []
    
    @patch('src.utils.llm_client.get_llm_client')
    def test_test_prompt_with_scenario(self, mock_llm_client):
        """Test testing a prompt with a scenario."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "This is a test response from the LLM"
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        # Get a prompt and scenario
        why_prompt = manager.get_prompt("why_agent", "purpose_discovery")
        scenarios = optimizer.get_test_scenarios("why_agent")
        test_scenario = scenarios[0]
        
        # Test the prompt
        result = optimizer.test_prompt_with_scenario(why_prompt, test_scenario)
        
        assert result is not None
        assert "response" in result
        assert "scenario" in result
        assert result["response"] == "This is a test response from the LLM"
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
    
    @patch('src.utils.llm_client.get_llm_client')
    def test_test_prompt_with_scenario_llm_error(self, mock_llm_client):
        """Test testing a prompt when LLM fails."""
        # Mock LLM to raise an error
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM connection failed")
        mock_llm_client.return_value = mock_llm
        
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        why_prompt = manager.get_prompt("why_agent", "purpose_discovery")
        scenarios = optimizer.get_test_scenarios("why_agent")
        test_scenario = scenarios[0]
        
        result = optimizer.test_prompt_with_scenario(why_prompt, test_scenario)
        
        assert result is not None
        assert "error" in result
        assert "Exception" in result["error"]
    
    def test_analyze_prompt_performance(self):
        """Test prompt performance analysis."""
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        # Create mock test results
        test_results = [
            {
                "scenario": {"stage": "purpose_discovery", "context": "startup"},
                "response": "Good response about purpose discovery",
                "response_length": 45
            },
            {
                "scenario": {"stage": "purpose_discovery", "context": "enterprise"},
                "response": "Another good response",
                "response_length": 25
            }
        ]
        
        analysis = optimizer.analyze_prompt_performance(test_results)
        
        assert "total_tests" in analysis
        assert "avg_response_length" in analysis
        assert "successful_tests" in analysis
        assert analysis["total_tests"] == 2
        assert analysis["avg_response_length"] == 35.0
        assert analysis["successful_tests"] == 2
    
    def test_analyze_prompt_performance_with_errors(self):
        """Test prompt performance analysis with errors."""
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        # Create test results with errors
        test_results = [
            {
                "scenario": {"stage": "purpose_discovery"},
                "response": "Good response",
                "response_length": 15
            },
            {
                "scenario": {"stage": "purpose_discovery"},
                "error": "LLM failed"
            }
        ]
        
        analysis = optimizer.analyze_prompt_performance(test_results)
        
        assert analysis["total_tests"] == 2
        assert analysis["successful_tests"] == 1
        assert analysis["failed_tests"] == 1
        assert analysis["avg_response_length"] == 15.0


class TestPromptManagerIntegration:
    """Integration tests for prompt management system."""
    
    def test_get_prompt_manager_singleton(self):
        """Test that get_prompt_manager returns a singleton instance."""
        manager1 = get_prompt_manager()
        manager2 = get_prompt_manager()
        
        assert manager1 is manager2
        assert isinstance(manager1, PromptTemplateManager)
    
    def test_full_workflow_why_agent(self):
        """Test complete workflow for WHY Agent prompts."""
        manager = get_prompt_manager()
        
        # Get all WHY Agent prompts
        stages = manager.list_stages("why_agent")
        assert len(stages) == 4
        
        for stage in stages:
            prompt = manager.get_prompt("why_agent", stage)
            assert prompt is not None
            assert len(prompt.input_variables) > 0
            assert "Golden Circle" in prompt.template
    
    def test_full_workflow_analogy_agent(self):
        """Test complete workflow for Analogy Agent prompts."""
        manager = get_prompt_manager()
        
        # Get all Analogy Agent prompts
        stages = manager.list_stages("analogy_agent")
        assert len(stages) == 4
        
        for stage in stages:
            prompt = manager.get_prompt("analogy_agent", stage)
            assert prompt is not None
            assert len(prompt.input_variables) > 0
            assert "analogical reasoning" in prompt.template.lower()
    
    def test_full_workflow_logic_agent(self):
        """Test complete workflow for Logic Agent prompts."""
        manager = get_prompt_manager()
        
        # Get all Logic Agent prompts
        stages = manager.list_stages("logic_agent")
        assert len(stages) == 4
        
        for stage in stages:
            prompt = manager.get_prompt("logic_agent", stage)
            assert prompt is not None
            assert len(prompt.input_variables) > 0
            assert any(keyword in prompt.template.lower() for keyword in ["deductive", "logical", "argument"])
    
    def test_full_workflow_open_strategy_agent(self):
        """Test complete workflow for Open Strategy Agent prompts."""
        manager = get_prompt_manager()
        
        # Get all Open Strategy Agent prompts
        stages = manager.list_stages("open_strategy_agent")
        assert len(stages) == 4
        
        for stage in stages:
            prompt = manager.get_prompt("open_strategy_agent", stage)
            assert prompt is not None
            assert len(prompt.input_variables) > 0
            assert any(keyword in prompt.template.lower() for keyword in ["implementation", "stakeholder", "strategy"])
    
    def test_prompt_consistency_across_agents(self):
        """Test that prompts are consistent across different agents."""
        manager = get_prompt_manager()
        
        agents = ["why_agent", "analogy_agent", "logic_agent", "open_strategy_agent"]
        
        for agent in agents:
            stages = manager.list_stages(agent)
            assert len(stages) == 4  # Each agent should have 4 stages
            
            for stage in stages:
                prompt = manager.get_prompt(agent, stage)
                assert prompt is not None
                
                # All prompts should have certain basic variables
                assert "conversation_context" in prompt.input_variables or "user_input" in prompt.input_variables
                
                # Templates should contain agent methodology references
                if agent == "why_agent":
                    assert "Golden Circle" in prompt.template
                elif agent == "analogy_agent":
                    assert "analogical" in prompt.template.lower()
                elif agent == "logic_agent":
                    assert "logical" in prompt.template.lower()
                elif agent == "open_strategy_agent":
                    assert "implementation" in prompt.template.lower()


@pytest.mark.integration
class TestPromptSystemIntegration:
    """Integration tests for the complete prompt management system."""
    
    @patch('src.utils.llm_client.get_llm_client')
    def test_end_to_end_prompt_testing(self, mock_llm_client):
        """Test end-to-end prompt testing workflow."""
        # Mock LLM
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Comprehensive test response for prompt validation"
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        # Initialize system
        manager = get_prompt_manager()
        optimizer = PromptOptimizer(manager)
        
        # Test all agents
        agents = ["why_agent", "analogy_agent", "logic_agent", "open_strategy_agent"]
        
        for agent in agents:
            stages = manager.list_stages(agent)
            
            for stage in stages:
                # Get prompt
                prompt = manager.get_prompt(agent, stage)
                assert prompt is not None
                
                # Validate structure
                is_valid, issues = optimizer.validate_prompt_structure(prompt)
                assert is_valid is True, f"Prompt validation failed for {agent}.{stage}: {issues}"
                
                # Test with scenarios
                scenarios = optimizer.get_test_scenarios(agent)
                if scenarios:
                    test_result = optimizer.test_prompt_with_scenario(prompt, scenarios[0])
                    assert "response" in test_result or "error" in test_result
    
    def test_prompt_template_variable_consistency(self):
        """Test that prompt templates use consistent variable names."""
        manager = get_prompt_manager()
        
        # Common variables that should appear across prompts
        common_vars = ["conversation_context", "user_input"]
        
        agents = ["why_agent", "analogy_agent", "logic_agent", "open_strategy_agent"]
        
        for agent in agents:
            stages = manager.list_stages(agent)
            
            for stage in stages:
                prompt = manager.get_prompt(agent, stage)
                
                # Check that at least one common variable is used
                has_common_var = any(var in prompt.input_variables for var in common_vars)
                assert has_common_var, f"Prompt {agent}.{stage} missing common variables"
                
                # Check that all variables in template are declared
                template_vars = set()
                import re
                # Find all {variable} patterns in template
                for match in re.finditer(r'\{(\w+)\}', prompt.template):
                    template_vars.add(match.group(1))
                
                declared_vars = set(prompt.input_variables)
                undeclared = template_vars - declared_vars
                
                assert len(undeclared) == 0, f"Prompt {agent}.{stage} has undeclared variables: {undeclared}"