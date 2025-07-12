"""
Tests for Case Configuration System
"""
import pytest
from case_config import get_config_manager

class TestCaseConfigManager:
    """Test the shared configuration system"""
    
    def test_config_manager_initialization(self, config_manager):
        """Test configuration manager loads successfully"""
        assert config_manager is not None
        assert hasattr(config_manager, 'config')
        assert 'case_lengths' in config_manager.config
        assert 'gate_structures' in config_manager.config
    
    def test_case_length_detection(self, config_manager):
        """Test case length detection from gate structures"""
        # Test 1-day case gates
        gates_1day = ["trial_opening", "first_witness_battle", "final_revelation"]
        detected_length = config_manager.detect_case_length_from_gates(gates_1day)
        assert detected_length == 1
        
        # Test 2-day case gates
        gates_2day = ["investigation_start", "trial_opening", "witness_confrontation", "final_revelation"]
        detected_length = config_manager.detect_case_length_from_gates(gates_2day)
        assert detected_length == 2
        
        # Test 3-day case gates
        gates_3day = ["crime_scene_analysis", "witness_interviews", "evidence_breakthrough", 
                     "trial_opening", "cross_examination_battle", "final_revelation"]
        detected_length = config_manager.detect_case_length_from_gates(gates_3day)
        assert detected_length == 3
    
    def test_gate_structure_retrieval(self, config_manager):
        """Test getting gate structures for different case lengths"""
        # Test 1-day case gates
        gates_1day = config_manager.get_gates_for_case_length(1)
        assert isinstance(gates_1day, list)
        assert len(gates_1day) == 3
        assert "trial_opening" in gates_1day
        
        # Test 2-day case gates
        gates_2day = config_manager.get_gates_for_case_length(2)
        assert isinstance(gates_2day, list)
        assert len(gates_2day) == 4
        
        # Test 3-day case gates
        gates_3day = config_manager.get_gates_for_case_length(3)
        assert isinstance(gates_3day, list)
        assert len(gates_3day) == 6
    
    def test_trial_trigger_points(self, config_manager):
        """Test trial trigger point calculation"""
        # 1-day case: trial ready immediately (0 investigation gates)
        trigger_1day = config_manager.get_trial_trigger_point(1)
        assert trigger_1day == 0
        
        # 2-day case: trial ready after 1 investigation gate
        trigger_2day = config_manager.get_trial_trigger_point(2)
        assert trigger_2day == 1
        
        # 3-day case: trial ready after 3 investigation gates
        trigger_3day = config_manager.get_trial_trigger_point(3)
        assert trigger_3day == 3
    
    def test_case_length_availability(self, config_manager):
        """Test available case lengths"""
        case_lengths = config_manager.get_case_lengths()
        assert isinstance(case_lengths, dict)
        assert "1" in case_lengths
        assert "2" in case_lengths
        assert "3" in case_lengths
    
    def test_mandatory_files_structure(self, config_manager):
        """Test mandatory file structure requirements"""
        mandatory_files = config_manager.get_mandatory_files()
        assert isinstance(mandatory_files, dict)
        
        # Should include key directories
        assert "game_state" in mandatory_files
    
    def test_optional_files_structure(self, config_manager):
        """Test optional file structure"""
        optional_files = config_manager.get_optional_files()
        assert isinstance(optional_files, dict)
        
        # Should include optional directories
        assert "saves" in optional_files
        assert "evidence" in optional_files
    
    def test_inspiration_categories(self, config_manager):
        """Test inspiration category configuration"""
        categories = config_manager.get_inspiration_categories()
        assert isinstance(categories, list)
        
        # Should include standard categories for legacy support
        expected_categories = ["character_motivations", "relationship_dynamics", "evidence_obstacles", "witness_behaviors"]
        for category in expected_categories:
            assert category in categories
    
    def test_invalid_case_length_handling(self, config_manager):
        """Test handling of invalid case lengths"""
        # Test invalid case length
        gates_invalid = config_manager.get_gates_for_case_length(5)  # Invalid length
        assert gates_invalid is None or gates_invalid == []
        
        # Test trial trigger for invalid length
        trigger_invalid = config_manager.get_trial_trigger_point(5)
        assert trigger_invalid == 0  # Should have safe default
    
    def test_empty_gates_detection(self, config_manager):
        """Test case length detection with empty or invalid gates"""
        # Empty gates list
        detected_length = config_manager.detect_case_length_from_gates([])
        assert detected_length == 2  # Should default to 2-day case
        
        # Unrecognized gates
        unknown_gates = ["unknown_gate1", "unknown_gate2"]
        detected_length = config_manager.detect_case_length_from_gates(unknown_gates)
        assert detected_length == 2  # Should default to 2-day case

class TestConfigurationValidation:
    """Test configuration validation and consistency"""
    
    def test_gate_structure_consistency(self, config_manager):
        """Test that gate structures are consistent across case lengths"""
        # Each case length should have unique gate count
        gates_1 = config_manager.get_gates_for_case_length(1)
        gates_2 = config_manager.get_gates_for_case_length(2)
        gates_3 = config_manager.get_gates_for_case_length(3)
        
        assert len(gates_1) < len(gates_2) < len(gates_3)
    
    def test_trial_trigger_logic_consistency(self, config_manager):
        """Test that trial trigger points make logical sense"""
        trigger_1 = config_manager.get_trial_trigger_point(1)
        trigger_2 = config_manager.get_trial_trigger_point(2)
        trigger_3 = config_manager.get_trial_trigger_point(3)
        
        # Trial triggers should increase with case length
        assert trigger_1 <= trigger_2 <= trigger_3
        
        # Triggers should be reasonable compared to total gates
        gates_1 = config_manager.get_gates_for_case_length(1)
        gates_2 = config_manager.get_gates_for_case_length(2)
        gates_3 = config_manager.get_gates_for_case_length(3)
        
        assert trigger_1 <= len(gates_1)
        assert trigger_2 <= len(gates_2)
        assert trigger_3 <= len(gates_3)
    
    def test_file_structure_completeness(self, config_manager):
        """Test that file structure includes all necessary components"""
        mandatory = config_manager.get_mandatory_files()
        optional = config_manager.get_optional_files()
        
        # Should have game state files
        assert "game_state" in mandatory
        game_state_files = mandatory["game_state"]
        assert "investigation_progress.json" in game_state_files
        assert "trial_progress.json" in game_state_files

class TestConfigurationEdgeCases:
    """Test edge cases and error handling in configuration"""
    
    def test_configuration_robustness(self, config_manager):
        """Test configuration handles edge cases gracefully"""
        # Test with None input - should handle gracefully
        try:
            result = config_manager.detect_case_length_from_gates(None)
            assert result == 2  # Should default safely
        except TypeError:
            # Expected behavior - None input should be handled
            pass
        
        # Test with very large gate list
        large_gates = [f"gate_{i}" for i in range(100)]
        result = config_manager.detect_case_length_from_gates(large_gates)
        assert result in [1, 2, 3]  # Should still return valid case length
    
    def test_config_singleton_behavior(self):
        """Test that config manager behaves as singleton"""
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        
        # Should be the same instance
        assert manager1 is manager2
        assert manager1.config is manager2.config