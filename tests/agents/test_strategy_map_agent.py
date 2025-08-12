import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.agents.strategy_map_agent import StrategyMapAgent, create_strategy_map_node
from src.models.state import initialize_agent_state, StrategyMapState


class TestStrategyMapAgent:
    """Test the Strategy Map Agent functionality."""
    
    def test_strategy_map_agent_initialization(self):
        """Test that Strategy Map Agent initializes successfully."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            
            agent = StrategyMapAgent()
            
            assert len(agent.value_components) == 6
            assert len(agent.perspectives) == 4
            assert "financial_capital" in agent.value_components
            assert "stakeholder_customer" in agent.perspectives
    
    def test_create_empty_strategy_map(self):
        """Test creation of empty strategy map with full structure."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            strategy_map = agent.create_empty_strategy_map("test_session_123")
            
            # Check metadata
            assert strategy_map["session_id"] == "test_session_123"
            assert strategy_map["version"] == 1
            assert "created_at" in strategy_map
            assert "updated_at" in strategy_map
            
            # Check core sections exist
            assert "why" in strategy_map
            assert "stakeholder_customer" in strategy_map
            assert "internal_processes" in strategy_map
            assert "learning_growth" in strategy_map
            assert "value_creation" in strategy_map
            
            # Check Six Value Components structure
            stakeholder = strategy_map["stakeholder_customer"]
            assert "financial_capital" in stakeholder
            assert "social_relationship_capital" in stakeholder
            
            internal = strategy_map["internal_processes"]
            assert "manufactured_capital" in internal
            assert "natural_capital" in internal
            
            learning = strategy_map["learning_growth"]
            assert "human_capital" in learning
            assert "intellectual_capital" in learning
            
            # Check progress tracking
            assert strategy_map["completed_sections"] == []
            assert strategy_map["completeness_percentage"] == 0.0
    
    def test_save_and_load_strategy_map(self):
        """Test saving and loading strategy map from JSON file."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            # Create test strategy map
            strategy_map = agent.create_empty_strategy_map("test_session")
            strategy_map["why"]["purpose"] = "Test purpose statement"
            strategy_map["completed_sections"] = ["why"]
            
            # Test saving
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                temp_path = f.name
            
            try:
                # Save the strategy map
                success = agent.save_strategy_map(strategy_map, temp_path)
                assert success is True
                assert os.path.exists(temp_path)
                
                # Load the strategy map
                loaded_map = agent.load_strategy_map(temp_path)
                assert loaded_map is not None
                assert loaded_map["session_id"] == "test_session"
                assert loaded_map["why"]["purpose"] == "Test purpose statement"
                assert "why" in loaded_map["completed_sections"]
                
                # Version should be incremented
                assert loaded_map["version"] == 2  # Incremented during save
                
            finally:
                # Cleanup
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    def test_load_nonexistent_file(self):
        """Test loading strategy map from non-existent file."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            result = agent.load_strategy_map("/nonexistent/path/file.json")
            assert result is None
    
    def test_load_invalid_json(self):
        """Test loading strategy map from invalid JSON file."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            # Create invalid JSON file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                f.write("invalid json content {")
                temp_path = f.name
            
            try:
                result = agent.load_strategy_map(temp_path)
                assert result is None
            finally:
                os.unlink(temp_path)
    
    def test_get_or_create_strategy_map_existing(self):
        """Test get_or_create_strategy_map with existing file."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            # Create and save a strategy map
            original_map = agent.create_empty_strategy_map("existing_session")
            original_map["why"]["purpose"] = "Existing purpose"
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                temp_path = f.name
            
            try:
                agent.save_strategy_map(original_map, temp_path)
                
                # Get existing map
                result_map = agent.get_or_create_strategy_map("existing_session", temp_path)
                assert result_map["why"]["purpose"] == "Existing purpose"
                assert result_map["session_id"] == "existing_session"
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    def test_get_or_create_strategy_map_new(self):
        """Test get_or_create_strategy_map with non-existing file."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            temp_path = "/tmp/test_new_strategy_map.json"
            
            try:
                # Should create new map
                result_map = agent.get_or_create_strategy_map("new_session", temp_path)
                assert result_map["session_id"] == "new_session"
                assert result_map["why"]["purpose"] == ""
                assert os.path.exists(temp_path)
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)


class TestStrategyMapUpdates:
    """Test strategy map update methods."""
    
    def test_update_why_insights(self):
        """Test updating strategy map with WHY insights."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            strategy_map = agent.create_empty_strategy_map("test_session")
            
            why_insights = {
                "purpose": "To empower people through innovation",
                "beliefs": ["Everyone has potential", "Innovation drives progress"],
                "values": ["Integrity", "Excellence", "Innovation"]
            }
            
            updated_map = agent.update_why_insights(strategy_map, why_insights)
            
            assert updated_map["why"]["purpose"] == "To empower people through innovation"
            assert len(updated_map["why"]["beliefs"]) == 2
            assert len(updated_map["why"]["values"]) == 3
            assert updated_map["why"]["golden_circle_complete"] is True
            assert "why" in updated_map["completed_sections"]
    
    def test_update_analogy_insights(self):
        """Test updating strategy map with Analogy insights."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            strategy_map = agent.create_empty_strategy_map("test_session")
            
            analogy_insights = {
                "source_domains": ["Tesla", "Apple"],
                "structural_mappings": ["Innovation pattern", "Customer focus"],
                "strategic_insights": ["Customer-centric innovation", "Vertical integration"],
                "analogical_framework": "Innovation-driven growth model"
            }
            
            updated_map = agent.update_analogy_insights(strategy_map, analogy_insights)
            
            assert updated_map["analogy_analysis"]["source_domains"] == ["Tesla", "Apple"]
            assert len(updated_map["analogy_analysis"]["strategic_insights"]) == 2
            assert updated_map["analogy_analysis"]["analogical_framework"] == "Innovation-driven growth model"
            assert "analogy_analysis" in updated_map["completed_sections"]
            assert "completed_at" in updated_map["analogy_analysis"]
    
    def test_update_logic_insights(self):
        """Test updating strategy map with Logic insights."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            strategy_map = agent.create_empty_strategy_map("test_session")
            
            logic_insights = {
                "argument_structure": "Premise-based strategic reasoning",
                "validity_assessment": "Conclusions follow logically from premises",
                "soundness_evaluation": "Evidence supports key assumptions",
                "logical_framework": "Deductive strategic framework"
            }
            
            updated_map = agent.update_logic_insights(strategy_map, logic_insights)
            
            assert updated_map["logical_structure"]["argument_structure"] == "Premise-based strategic reasoning"
            assert updated_map["logical_structure"]["validity_assessment"] == "Conclusions follow logically from premises"
            assert updated_map["logical_structure"]["logical_framework"] == "Deductive strategic framework"
            assert "logical_structure" in updated_map["completed_sections"]
    
    def test_update_implementation_insights(self):
        """Test updating strategy map with Implementation insights."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            strategy_map = agent.create_empty_strategy_map("test_session")
            
            implementation_insights = {
                "stakeholder_analysis": ["Employees", "Customers", "Partners"],
                "process_design": ["Governance", "Decision workflows"],
                "resource_planning": {
                    "budget": "100K investment",
                    "timeline": "6 month implementation"
                },
                "implementation_roadmap": ["Phase 1", "Phase 2", "Phase 3"]
            }
            
            updated_map = agent.update_implementation_insights(strategy_map, implementation_insights)
            
            assert len(updated_map["implementation_plan"]["stakeholder_analysis"]) == 3
            assert len(updated_map["implementation_plan"]["process_design"]) == 2
            assert updated_map["implementation_plan"]["resource_planning"]["budget"] == "100K investment"
            assert len(updated_map["implementation_plan"]["implementation_roadmap"]) == 3
            assert "implementation_plan" in updated_map["completed_sections"]


class TestStrategyMapValidation:
    """Test strategy map validation methods."""
    
    def test_validate_empty_strategy_map(self):
        """Test validation of empty strategy map."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            strategy_map = agent.create_empty_strategy_map("test_session")
            validation = agent.validate_strategy_map(strategy_map)
            
            assert validation["is_valid"] is True  # Empty map is still valid
            assert validation["consistency_score"] == 0.0  # No content yet
            assert len(validation["recommendations"]) > 0
            assert "Complete the WHY discovery" in validation["recommendations"][0]
    
    def test_validate_complete_strategy_map(self):
        """Test validation of complete strategy map."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            strategy_map = agent.create_empty_strategy_map("test_session")
            
            # Fill in all sections
            strategy_map["why"]["purpose"] = "To innovate for customer success"
            strategy_map["why"]["beliefs"] = ["Innovation matters"]
            strategy_map["why"]["golden_circle_complete"] = True
            
            strategy_map["analogy_analysis"] = {"source_domains": ["Tesla"]}
            strategy_map["logical_structure"] = {"argument_structure": "Valid reasoning"}
            strategy_map["implementation_plan"] = {"stakeholder_analysis": ["Teams"]}
            
            strategy_map["completed_sections"] = [
                "why", "stakeholder_customer", "internal_processes", 
                "learning_growth", "value_creation"
            ]
            
            validation = agent.validate_strategy_map(strategy_map)
            
            assert validation["is_valid"] is True
            assert validation["consistency_score"] > 50.0  # Should have decent score
            assert len(validation["errors"]) == 0
    
    def test_validate_invalid_strategy_map(self):
        """Test validation of invalid strategy map."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            # Create invalid strategy map
            invalid_map = {}  # Missing required fields
            
            validation = agent.validate_strategy_map(invalid_map)
            
            assert validation["is_valid"] is False
            assert len(validation["errors"]) > 0
            assert "Missing session_id" in validation["errors"]
    
    def test_validate_why_section_inconsistent(self):
        """Test validation of inconsistent WHY section."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            strategy_map = agent.create_empty_strategy_map("test_session")
            
            # Mark WHY as complete but leave purpose empty
            strategy_map["why"]["golden_circle_complete"] = True
            strategy_map["why"]["purpose"] = ""  # Missing purpose
            
            validation = agent.validate_strategy_map(strategy_map)
            
            assert "WHY marked complete but missing purpose statement" in validation["errors"]
    
    def test_calculate_completeness_percentage(self):
        """Test completeness percentage calculation."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            strategy_map = agent.create_empty_strategy_map("test_session")
            
            # Test empty map
            completeness = agent._calculate_completeness(strategy_map)
            assert completeness == 0.0
            
            # Add WHY completion
            strategy_map["completed_sections"] = ["why"]
            completeness = agent._calculate_completeness(strategy_map)
            assert completeness > 0.0
            
            # Add all sections
            strategy_map["completed_sections"] = [
                "why", "stakeholder_customer", "internal_processes", 
                "learning_growth", "value_creation", "analogy_analysis",
                "logical_structure", "implementation_plan"
            ]
            completeness = agent._calculate_completeness(strategy_map)
            assert completeness >= 90.0  # Should be nearly complete


class TestInsightExtraction:
    """Test insight extraction methods."""
    
    def test_extract_why_insights_with_llm(self):
        """Test WHY insight extraction using LLM."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_response = MagicMock()
            mock_response.content = '''
            {
                "purpose": "To empower innovation",
                "beliefs": ["People matter", "Innovation drives success"],
                "values": ["Integrity", "Excellence"]
            }
            '''
            mock_llm.return_value.invoke.return_value = mock_response
            
            agent = StrategyMapAgent()
            
            agent_output = "Our purpose is to empower innovation through people."
            insights = agent._extract_why_insights(agent_output)
            
            assert insights["purpose"] == "To empower innovation"
            assert len(insights["beliefs"]) == 2
            assert "Integrity" in insights["values"]
    
    def test_extract_why_insights_fallback(self):
        """Test WHY insight extraction with LLM error fallback."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            # Mock LLM error
            mock_llm.return_value.invoke.side_effect = Exception("LLM error")
            
            agent = StrategyMapAgent()
            
            agent_output = """
            Purpose: To create innovative solutions
            Our core beliefs include: customer first, quality matters
            Values: integrity, excellence, innovation
            """
            
            insights = agent._extract_why_insights(agent_output)
            
            # Should use fallback extraction
            assert insights["purpose"] != ""
            assert isinstance(insights["beliefs"], list)
            assert isinstance(insights["values"], list)
    
    def test_extract_text_after(self):
        """Test text extraction helper method."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            text = "Purpose: To innovate for customers. Mission: Create value."
            
            result = agent._extract_text_after(text, ["purpose"])
            assert "To innovate for customers" in result
            
            result = agent._extract_text_after(text, ["mission"])
            assert "Create value" in result
            
            result = agent._extract_text_after(text, ["nonexistent"])
            assert result == ""
    
    def test_extract_list_items(self):
        """Test list item extraction helper method."""
        with patch('src.agents.strategy_map_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = StrategyMapAgent()
            
            text = """
            • Company Tesla is innovative
            • Organization Apple focuses on design
            - Example Google shows data-driven approach
            Company Microsoft demonstrates enterprise value
            """
            
            items = agent._extract_list_items(text, ["company", "organization"])
            
            assert len(items) > 0
            assert any("Tesla" in item for item in items)
            assert any("Apple" in item for item in items)


class TestStrategyMapNode:
    """Test the Strategy Map Node for LangGraph integration."""
    
    @patch('src.agents.strategy_map_agent.get_llm_client')
    def test_create_strategy_map_node(self, mock_llm_client):
        """Test creation of strategy map node function."""
        mock_llm_client.return_value = MagicMock()
        
        node_function = create_strategy_map_node()
        assert callable(node_function)
    
    @patch('src.agents.strategy_map_agent.get_llm_client')
    def test_strategy_map_node_execution(self, mock_llm_client):
        """Test strategy map node execution."""
        mock_llm_client.return_value = MagicMock()
        
        node_function = create_strategy_map_node()
        
        # Create test state
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            state = initialize_agent_state("test_session", temp_path)
            state["current_agent"] = "why_agent"
            state["agent_output"] = "Purpose: To innovate for customers"
            
            # Execute node
            result_state = node_function(state)
            
            # Should return updated state
            assert result_state["session_id"] == "test_session"
            assert result_state["strategy_map_path"] == temp_path
            
            # Should have created strategy map file
            assert os.path.exists(temp_path)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @patch('src.agents.strategy_map_agent.get_llm_client')
    def test_strategy_map_node_error_handling(self, mock_llm_client):
        """Test strategy map node error handling."""
        mock_llm_client.return_value = MagicMock()
        
        node_function = create_strategy_map_node()
        
        # Create state with invalid path
        state = initialize_agent_state("test_session", "/invalid/path/strategy.json")
        
        # Should not crash on error
        result_state = node_function(state)
        assert result_state["session_id"] == "test_session"


@pytest.mark.integration
class TestStrategyMapIntegration:
    """Integration tests for Strategy Map Agent."""
    
    @patch('src.agents.strategy_map_agent.get_llm_client')
    def test_full_strategy_development_cycle(self, mock_llm_client):
        """Test complete strategy development cycle."""
        mock_llm_client.return_value = MagicMock()
        
        agent = StrategyMapAgent()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            # 1. Create initial strategy map
            strategy_map = agent.get_or_create_strategy_map("integration_test", temp_path)
            assert strategy_map["completeness_percentage"] == 0.0
            
            # 2. Add WHY insights
            why_insights = {
                "purpose": "To transform industry through innovation",
                "beliefs": ["Customer success drives everything"],
                "values": ["Innovation", "Integrity", "Excellence"]
            }
            strategy_map = agent.update_why_insights(strategy_map, why_insights)
            agent.save_strategy_map(strategy_map, temp_path)
            
            # 3. Add Analogy insights
            analogy_insights = {
                "source_domains": ["Tesla", "Apple"],
                "strategic_insights": ["Vertical integration benefits", "Customer experience focus"]
            }
            strategy_map = agent.update_analogy_insights(strategy_map, analogy_insights)
            agent.save_strategy_map(strategy_map, temp_path)
            
            # 4. Add Logic insights
            logic_insights = {
                "argument_structure": "Innovation-driven competitive advantage",
                "logical_framework": "Customer value through innovation"
            }
            strategy_map = agent.update_logic_insights(strategy_map, logic_insights)
            agent.save_strategy_map(strategy_map, temp_path)
            
            # 5. Add Implementation insights
            impl_insights = {
                "stakeholder_analysis": ["Engineering teams", "Product managers", "Customers"],
                "implementation_roadmap": ["Discovery", "Development", "Launch"]
            }
            strategy_map = agent.update_implementation_insights(strategy_map, impl_insights)
            agent.save_strategy_map(strategy_map, temp_path)
            
            # 6. Validate final strategy map
            validation = agent.validate_strategy_map(strategy_map)
            assert validation["is_valid"] is True
            assert strategy_map["completeness_percentage"] > 30.0  # Should show progress
            
            # 7. Verify persistence
            loaded_map = agent.load_strategy_map(temp_path)
            assert loaded_map["why"]["purpose"] == "To transform industry through innovation"
            assert loaded_map["analogy_analysis"]["source_domains"] == ["Tesla", "Apple"]
            assert loaded_map["logical_structure"]["argument_structure"] == "Innovation-driven competitive advantage"
            assert len(loaded_map["implementation_plan"]["stakeholder_analysis"]) == 3
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)