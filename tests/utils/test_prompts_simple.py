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
    
    def test_prompt_config_initialization(self):
        """Test PromptConfig initialization."""
        config = PromptConfig()
        
        assert config.prompt_version == "1.0.0"
        assert config.default_temperature == 0.7
        assert config.max_tokens == 4000
        assert config.enable_prompt_caching is True
        assert config.prompt_validation is True
        
    def test_methodology_settings_exist(self):
        """Test that methodology settings exist for all agents."""
        config = PromptConfig()
        
        expected_agents = ["why_agent", "analogy_agent", "logic_agent", "open_strategy_agent"]
        for agent in expected_agents:
            assert agent in config.methodology_settings
            settings = config.methodology_settings[agent]
            assert "methodology_name" in settings
            assert "focus_areas" in settings
            assert "prompt_style" in settings
            assert len(settings["focus_areas"]) == 4


class TestPromptTemplateManager:
    """Test the PromptTemplateManager class functionality."""
    
    def test_template_manager_initialization(self):
        """Test PromptTemplateManager initialization."""
        manager = PromptTemplateManager()
        
        assert manager.config is not None
        assert isinstance(manager.config, PromptConfig)
        assert len(manager.templates) > 0
    
    def test_get_template_why_agent(self):
        """Test getting WHY Agent templates."""
        manager = PromptTemplateManager()
        
        # Test that WHY agent templates exist
        stages = ["purpose_discovery", "belief_exploration", "values_integration", "synthesis"]
        
        for stage in stages:
            template = manager.get_template("why_agent", stage)
            assert template is not None
            assert hasattr(template, 'template')
            assert hasattr(template, 'input_variables')
            assert "Golden Circle" in template.template
    
    def test_get_template_analogy_agent(self):
        """Test getting Analogy Agent templates."""
        manager = PromptTemplateManager()
        
        stages = ["source_identification", "structural_mapping", "evaluation_adaptation", "strategic_integration"]
        
        for stage in stages:
            template = manager.get_template("analogy_agent", stage)
            assert template is not None
            assert "analogical" in template.template.lower()
    
    def test_get_template_logic_agent(self):
        """Test getting Logic Agent templates."""
        manager = PromptTemplateManager()
        
        stages = ["argument_analysis", "validity_assessment", "soundness_evaluation", "framework_construction"]
        
        for stage in stages:
            template = manager.get_template("logic_agent", stage)
            assert template is not None
            assert "logical" in template.template.lower() or "argument" in template.template.lower()
    
    def test_get_template_open_strategy_agent(self):
        """Test getting Open Strategy Agent templates."""
        manager = PromptTemplateManager()
        
        stages = ["stakeholder_analysis", "process_design", "resource_planning", "implementation_roadmap"]
        
        for stage in stages:
            template = manager.get_template("open_strategy_agent", stage)
            assert template is not None
            assert "implementation" in template.template.lower() or "stakeholder" in template.template.lower()
    
    def test_get_template_invalid_agent(self):
        """Test getting template for invalid agent raises KeyError."""
        manager = PromptTemplateManager()
        
        with pytest.raises(KeyError):
            manager.get_template("invalid_agent", "some_stage")
    
    def test_get_template_invalid_stage(self):
        """Test getting template for invalid stage raises KeyError."""
        manager = PromptTemplateManager()
        
        with pytest.raises(KeyError):
            manager.get_template("why_agent", "invalid_stage")
    
    def test_get_methodology_info(self):
        """Test getting methodology information."""
        manager = PromptTemplateManager()
        
        why_info = manager.get_methodology_info("why_agent")
        assert "methodology_name" in why_info
        assert why_info["methodology_name"] == "Simon Sinek's Golden Circle"
        
        analogy_info = manager.get_methodology_info("analogy_agent")
        assert "methodology_name" in analogy_info
        assert "Carroll" in analogy_info["methodology_name"]
    
    def test_validate_template(self):
        """Test template validation."""
        manager = PromptTemplateManager()
        
        template = manager.get_template("why_agent", "purpose_discovery")
        
        # Should validate successfully with required variables
        required_vars = ["conversation_context", "user_input"]
        is_valid = manager.validate_template(template, required_vars)
        assert is_valid is True
        
        # Should fail validation with missing variables
        missing_vars = ["non_existent_variable"]
        is_valid = manager.validate_template(template, missing_vars)
        assert is_valid is False


class TestPromptOptimizer:
    """Test the PromptOptimizer class functionality."""
    
    def test_optimizer_initialization(self):
        """Test PromptOptimizer initialization."""
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        assert optimizer.template_manager == manager
        assert hasattr(optimizer, 'performance_metrics')
    
    def test_test_prompt_completeness(self):
        """Test prompt completeness checking."""
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        # Test WHY agent completeness
        why_results = optimizer.test_prompt_completeness("why_agent")
        expected_stages = ["purpose_discovery", "belief_exploration", "values_integration", "synthesis"]
        
        for stage in expected_stages:
            assert stage in why_results
            assert why_results[stage] is True
    
    def test_validate_prompt_variables(self):
        """Test prompt variable validation."""
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        # Test valid variables
        is_valid = optimizer.validate_prompt_variables("why_agent", "purpose_discovery", ["conversation_context"])
        assert is_valid is True
        
        # Test invalid variables
        is_valid = optimizer.validate_prompt_variables("why_agent", "purpose_discovery", ["non_existent_var"])
        assert is_valid is False
        
        # Test invalid agent/stage
        is_valid = optimizer.validate_prompt_variables("invalid_agent", "invalid_stage", ["any_var"])
        assert is_valid is False
    
    def test_get_prompt_statistics(self):
        """Test getting prompt statistics."""
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer(manager)
        
        stats = optimizer.get_prompt_statistics()
        
        assert "total_templates" in stats
        assert "templates_by_agent" in stats
        assert "methodologies" in stats
        
        assert stats["total_templates"] > 0
        assert len(stats["methodologies"]) == 4  # 4 agent types


class TestPromptManagerIntegration:
    """Integration tests for prompt management system."""
    
    def test_get_prompt_manager_factory(self):
        """Test get_prompt_manager factory function."""
        manager = get_prompt_manager()
        
        assert isinstance(manager, PromptTemplateManager)
        assert len(manager.templates) > 0
    
    def test_get_prompt_optimizer_factory(self):
        """Test get_prompt_optimizer factory function."""
        optimizer = get_prompt_optimizer()
        
        assert isinstance(optimizer, PromptOptimizer)
        assert isinstance(optimizer.template_manager, PromptTemplateManager)
    
    def test_all_agent_templates_exist(self):
        """Test that all required agent templates exist."""
        manager = get_prompt_manager()
        
        agents_and_stages = {
            "why_agent": ["purpose_discovery", "belief_exploration", "values_integration", "synthesis"],
            "analogy_agent": ["source_identification", "structural_mapping", "evaluation_adaptation", "strategic_integration"],
            "logic_agent": ["argument_analysis", "validity_assessment", "soundness_evaluation", "framework_construction"],
            "open_strategy_agent": ["stakeholder_analysis", "process_design", "resource_planning", "implementation_roadmap"]
        }
        
        for agent, stages in agents_and_stages.items():
            for stage in stages:
                template = manager.get_template(agent, stage)
                assert template is not None
                assert len(template.input_variables) > 0
    
    def test_template_consistency(self):
        """Test that templates have consistent structure."""
        manager = get_prompt_manager()
        
        # Common variables that should appear in most templates
        common_vars = ["conversation_context", "user_input"]
        
        agents = ["why_agent", "analogy_agent", "logic_agent", "open_strategy_agent"]
        
        for agent in agents:
            methodology_info = manager.get_methodology_info(agent)
            stages = methodology_info.get("focus_areas", [])
            
            for stage in stages:
                template = manager.get_template(agent, stage)
                
                # Check that at least one common variable is used
                has_common_var = any(var in template.input_variables for var in common_vars)
                assert has_common_var, f"Template {agent}.{stage} missing common variables"
                
                # Check template is not empty
                assert len(template.template) > 100, f"Template {agent}.{stage} seems too short"
                
                # Check methodology is referenced
                methodology_name = methodology_info.get("methodology_name", "")
                if methodology_name:
                    # At least some reference to the methodology should exist
                    template_lower = template.template.lower()
                    assert any(word.lower() in template_lower for word in methodology_name.split()), \
                        f"Template {agent}.{stage} doesn't reference methodology"


@pytest.mark.integration
class TestPromptSystemEnd2End:
    """End-to-end tests for the prompt management system."""
    
    def test_complete_prompt_workflow(self):
        """Test complete workflow from manager creation to template usage."""
        # Initialize system
        manager = get_prompt_manager()
        optimizer = get_prompt_optimizer(manager)
        
        # Test each agent type
        agents = ["why_agent", "analogy_agent", "logic_agent", "open_strategy_agent"]
        
        for agent in agents:
            # Get methodology info
            methodology_info = manager.get_methodology_info(agent)
            assert methodology_info is not None
            
            # Check completeness
            completeness = optimizer.test_prompt_completeness(agent)
            for stage, complete in completeness.items():
                assert complete is True, f"{agent}.{stage} template missing"
            
            # Test each stage
            for stage in methodology_info["focus_areas"]:
                template = manager.get_template(agent, stage)
                assert template is not None
                
                # Validate template structure
                assert len(template.input_variables) > 0
                assert len(template.template) > 0
        
        # Get overall statistics
        stats = optimizer.get_prompt_statistics()
        assert stats["total_templates"] >= 16  # At least 4 agents × 4 stages each
    
    def test_template_formatting_works(self):
        """Test that templates can be properly formatted."""
        manager = get_prompt_manager()
        
        # Test a representative template from each agent
        test_cases = [
            ("why_agent", "purpose_discovery", {
                "conversation_context": "Previous discussion about company goals",
                "user_input": "What is our core purpose?",
                "company_context": "Tech startup in AI space"
            }),
            ("analogy_agent", "source_identification", {
                "conversation_context": "Discussing strategic challenges", 
                "user_input": "How do other industries handle this?",
                "purpose_context": "Innovation in AI",
                "company_context": "Small tech company"
            }),
            ("logic_agent", "argument_analysis", {
                "conversation_context": "Strategic discussion",
                "user_input": "Does our strategy make sense?",
                "strategic_content": "Focus on AI innovation",
                "context_info": "Technology industry"
            }),
            ("open_strategy_agent", "stakeholder_analysis", {
                "conversation_context": "Implementation planning",
                "user_input": "Who needs to be involved?",
                "strategic_foundation": "AI innovation strategy",
                "context_info": "Tech startup context"
            })
        ]
        
        for agent, stage, variables in test_cases:
            template = manager.get_template(agent, stage)
            
            # Should be able to format without errors
            try:
                formatted = template.format(**variables)
                assert len(formatted) > len(template.template)  # Should be expanded
                
                # Check that variables were substituted
                for var, value in variables.items():
                    if var in template.input_variables:
                        assert value in formatted, f"Variable {var} not substituted in {agent}.{stage}"
                        
            except KeyError as e:
                pytest.fail(f"Template {agent}.{stage} failed to format: missing variable {e}")
            except Exception as e:
                pytest.fail(f"Template {agent}.{stage} failed to format: {e}")