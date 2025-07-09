"""
Tests for GameStateManager - Core Business Logic
"""
import pytest
import json
from unittest.mock import patch, Mock
from game_state_manager import GameStateManager

class TestGameStateManager:
    """Test core game state management functionality"""
    
    def test_initialization(self, minimal_case_structure):
        """Test GameStateManager initialization"""
        manager = GameStateManager(str(minimal_case_structure))
        
        assert manager.case_name == "test_case"
        assert manager.case_length == 1
        assert len(manager.gates) == 3
        assert manager.current_state["current_phase"] == "investigation"
    
    def test_gate_transitions(self, minimal_case_structure):
        """Test gate state transitions: pending -> in_progress -> completed"""
        manager = GameStateManager(str(minimal_case_structure))
        
        # Test starting a gate
        assert manager.start_gate("gate1") == True
        assert manager.current_state["investigation_gates"]["gate1"] == "in_progress"
        
        # Test completing a gate
        assert manager.complete_gate("gate1") == True
        assert manager.current_state["investigation_gates"]["gate1"] == "completed"
        
        # Test trying to start already completed gate
        assert manager.start_gate("gate1") == False
        
        # Test trying to complete already completed gate
        assert manager.complete_gate("gate1") == False
    
    def test_invalid_gate_operations(self, minimal_case_structure):
        """Test error handling for invalid gate operations"""
        manager = GameStateManager(str(minimal_case_structure))
        
        # Test invalid gate name
        with pytest.raises(ValueError, match="Gate 'invalid_gate' not found"):
            manager.start_gate("invalid_gate")
            
        with pytest.raises(ValueError, match="Gate 'invalid_gate' not found"):
            manager.complete_gate("invalid_gate")
    
    def test_evidence_management(self, minimal_case_structure):
        """Test evidence addition and retrieval"""
        manager = GameStateManager(str(minimal_case_structure))
        
        # Test adding evidence
        assert manager.add_evidence("test_evidence", "A test piece of evidence") == True
        evidence_list = manager.current_state["evidence_collected"]
        assert len(evidence_list) == 1
        assert evidence_list[0]["name"] == "test_evidence"
        assert evidence_list[0]["description"] == "A test piece of evidence"
        
        # Test adding duplicate evidence
        assert manager.add_evidence("test_evidence", "Duplicate") == False
        assert len(manager.current_state["evidence_collected"]) == 1
    
    def test_character_trust_management(self, minimal_case_structure):
        """Test character trust level updates and bounds"""
        manager = GameStateManager(str(minimal_case_structure))
        
        # Test initial trust (default 5)
        trust = manager.update_character_trust("witness1", 0)
        assert trust == 5
        
        # Test trust increase
        trust = manager.update_character_trust("witness1", 3)
        assert trust == 8
        
        # Test trust decrease
        trust = manager.update_character_trust("witness1", -5)
        assert trust == 3
        
        # Test bounds (0-10)
        trust = manager.update_character_trust("witness1", -10)
        assert trust == 0  # Lower bound
        
        trust = manager.update_character_trust("witness1", 15)
        assert trust == 10  # Upper bound
    
    def test_trial_trigger_logic(self, minimal_case_structure):
        """Test trial trigger based on case length and completed gates"""
        manager = GameStateManager(str(minimal_case_structure))
        
        # 1-day case should be trial ready immediately (0 investigation gates required)
        assert manager.is_trial_ready() == True
        
        # Simulate 3-day case by updating case_length
        manager.case_length = 3
        manager.current_state["case_length"] = 3
        
        # Should not be trial ready with 0 completed gates
        assert manager.is_trial_ready() == False
        
        # Complete 3 gates (trigger point for 3-day case)
        manager.complete_gate("gate1")
        manager.complete_gate("gate2") 
        manager.complete_gate("gate3")
        
        # Now should be trial ready
        assert manager.is_trial_ready() == True
    
    def test_save_restore_functionality(self, minimal_case_structure):
        """Test save point creation and restoration"""
        manager = GameStateManager(str(minimal_case_structure))
        
        # Make some changes
        manager.start_gate("gate1")
        manager.add_evidence("save_test", "Evidence before save")
        manager.update_character_trust("witness1", 2)
        
        # Create save point
        assert manager.create_save_point("test_save") == True
        
        # Make more changes
        manager.complete_gate("gate1")
        manager.add_evidence("after_save", "Evidence after save")
        
        # Verify changes
        assert manager.current_state["investigation_gates"]["gate1"] == "completed"
        assert len(manager.current_state["evidence_collected"]) == 2
        
        # Restore save point
        assert manager.restore_save_point("test_save") == True
        
        # Verify restoration
        assert manager.current_state["investigation_gates"]["gate1"] == "in_progress"
        assert len(manager.current_state["evidence_collected"]) == 1
        assert manager.current_state["character_trust_levels"]["witness1"] == 7
    
    def test_progress_calculation(self, minimal_case_structure):
        """Test progress percentage calculation"""
        manager = GameStateManager(str(minimal_case_structure))
        
        # 0 completed gates
        assert manager.get_progress_percentage() == 0.0
        
        # 1 completed gate (1/3)
        manager.complete_gate("gate1")
        assert abs(manager.get_progress_percentage() - 33.33333333333333) < 0.1
        
        # 2 completed gates (2/3)
        manager.complete_gate("gate2")
        assert abs(manager.get_progress_percentage() - 66.66666666666666) < 0.1
        
        # 3 completed gates (3/3)
        manager.complete_gate("gate3")
        assert manager.get_progress_percentage() == 100.0

class TestInspirationSystem:
    """Test the pure random inspiration system"""
    
    def test_pure_random_inspiration(self, minimal_case_structure):
        """Test pure random inspiration for cases without inspiration pool"""
        manager = GameStateManager(str(minimal_case_structure))
        
        # Should use pure random since no inspiration_pool.json
        inspiration = manager.must_use_inspiration("test context")
        
        assert inspiration["category"] == "pure_random"
        assert "word" in inspiration
        assert len(inspiration["word"]) >= 3
        assert "instruction" in inspiration
        assert "context" in inspiration
    
    def test_legacy_inspiration_pool(self, case_with_inspiration_pool):
        """Test legacy inspiration system for cases with inspiration pool"""
        manager = GameStateManager(str(case_with_inspiration_pool))
        
        # Should use legacy system since inspiration_pool.json exists
        inspiration = manager.must_use_inspiration("test context")
        
        # Should select from one of the legacy categories
        assert inspiration["category"] in ["character_motivations", "relationship_dynamics", "evidence_obstacles"]
        assert "word" in inspiration
        assert "instruction" in inspiration
    
    def test_wonderwords_fallback(self, minimal_case_structure):
        """Test fallback when wonderwords package fails"""
        manager = GameStateManager(str(minimal_case_structure))
        
        # Test the fallback by temporarily hiding wonderwords
        with patch.dict('sys.modules', {'wonderwords': None}):
            inspiration = manager.get_pure_random_inspiration("test context")
            
            assert inspiration["category"] == "pure_random"
            assert inspiration["source"] == "fallback"
            assert inspiration["word"] in [
                "anchor", "bridge", "cascade", "deliberate", "echo", "fragment", "gravity",
                "hollow", "intricate", "journey", "kindle", "labyrinth", "momentum", "nebula",
                "obscure", "pivot", "quench", "radiant", "spiral", "turbulent", "unveil",
                "vibrant", "whisper", "xenial", "yearning", "zenith"
            ]
    
    def test_inspiration_logging(self, minimal_case_structure):
        """Test inspiration usage logging"""
        manager = GameStateManager(str(minimal_case_structure))
        
        # Use inspiration
        inspiration = manager.must_use_inspiration("test logging")
        
        # Check that it was logged
        history = manager.get_inspiration_history()
        assert len(history) == 1
        assert history[0]["word"] == inspiration["word"]
        assert history[0]["usage_context"] == "test logging"
        assert history[0]["category"] == "pure_random"

class TestCaseValidation:
    """Test case consistency validation"""
    
    def test_valid_case_structure(self, minimal_case_structure):
        """Test validation of a properly structured case"""
        manager = GameStateManager(str(minimal_case_structure))
        
        validation = manager.validate_case_consistency()
        assert validation["valid"] == True
        assert len(validation["issues"]) == 0
    
    def test_character_trust_bounds_validation(self, minimal_case_structure):
        """Test validation catches invalid trust levels"""
        manager = GameStateManager(str(minimal_case_structure))
        
        # Manually set invalid trust level
        manager.current_state["character_trust_levels"] = {"test_char": 15}  # Invalid: > 10
        
        validation = manager.validate_case_consistency()
        assert validation["valid"] == False
        assert any("trust levels outside valid range" in issue for issue in validation["issues"])

class TestUtilityFunctions:
    """Test utility and helper functions"""
    
    def test_get_available_actions(self, minimal_case_structure):
        """Test context-appropriate action generation"""
        manager = GameStateManager(str(minimal_case_structure))
        
        actions = manager.get_available_actions()
        
        # Should always include basic actions
        assert "Check current status" in actions
        
        # Should include next gate action
        assert any("Work on" in action for action in actions)
        
        # Should include trial action for 1-day case (trial ready immediately)
        assert "Start trial" in actions
    
    def test_get_current_status(self, minimal_case_structure):
        """Test status information generation"""
        manager = GameStateManager(str(minimal_case_structure))
        
        status = manager.get_current_status()
        
        assert status["case_name"] == "test_case"
        assert status["case_length"] == 1
        assert status["total_gates"] == 3
        assert status["progress_percentage"] == 0.0
        assert status["trial_ready"] == True
        assert status["evidence_collected"] == 0
        assert status["witnesses_interviewed"] == 0
    
    def test_resume_context_generation(self, minimal_case_structure):
        """Test resume context for continuing gameplay"""
        manager = GameStateManager(str(minimal_case_structure))
        
        # Make some progress
        manager.start_gate("gate1")
        manager.add_evidence("resume_test", "Test evidence")
        
        summary = manager.generate_resume_summary()
        
        assert "test_case" in summary
        assert "1-day case" in summary
        assert "Gate 1" in summary or "gate1" in summary
        assert "resume_test" in summary
        assert "TRIAL READY" in summary  # 1-day case is always trial ready