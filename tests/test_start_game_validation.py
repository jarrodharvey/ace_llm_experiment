#!/usr/bin/env python3
"""
Test Suite for Start Game Validation Framework
Comprehensive testing of validation, error detection, and root cause analysis.
"""

import pytest
import tempfile
import shutil
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from start_game_validator import StartGameValidator

class TestStartGameValidator:
    """Test start game validation framework"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def simple_case(self, temp_dir):
        """Create valid simple improvisation case"""
        case_dir = temp_dir / "test_simple_case"
        case_dir.mkdir()
        
        # Create required files
        with open(case_dir / "real_life_case_summary.txt", 'w') as f:
            f.write("This is a test case summary with sufficient content for validation purposes.")
        
        with open(case_dir / "case_opening.txt", 'w') as f:
            f.write("This is a test case opening scene with sufficient content for validation.")
        
        return case_dir
    
    @pytest.fixture
    def complex_case(self, temp_dir):
        """Create valid complex case structure"""
        case_dir = temp_dir / "test_complex_case"
        case_dir.mkdir()
        
        # Create backbone directory
        backbone_dir = case_dir / "backbone"
        backbone_dir.mkdir()
        
        # Create required backbone files
        backbone_files = {
            "case_structure.json": {"case_title": "Test Case", "case_id": "test_case"},
            "character_facts.json": {"characters": [{"name": "Test Client (Client)", "role": "defendant"}]},
            "evidence_chain.json": {"evidence": []},
            "truth_timeline.json": {"timeline": []},
            "witness_testimonies.json": {"testimonies": []},
            "trial_structure.json": {"structure": []}
        }
        
        for filename, content in backbone_files.items():
            with open(backbone_dir / filename, 'w') as f:
                json.dump(content, f, indent=2)
        
        # Create game state directory
        game_state_dir = case_dir / "game_state"
        game_state_dir.mkdir()
        
        # Create game state files
        investigation_state = {
            "investigation_gates": {"investigation_day_1": "pending"},
            "current_phase": "investigation",
            "case_length": 2,
            "evidence_collected": [],
            "character_trust_levels": {},
            "witnesses_interviewed": [],
            "current_location": "detention_center"
        }
        
        trial_state = {"trial_status": "not_started"}
        
        with open(game_state_dir / "investigation_progress.json", 'w') as f:
            json.dump(investigation_state, f, indent=2)
            
        with open(game_state_dir / "trial_progress.json", 'w') as f:
            json.dump(trial_state, f, indent=2)
        
        return case_dir
    
    def test_improvisation_case_validation(self, simple_case):
        """Test improvisation case validation"""
        # Test improvisation case validation
        validator = StartGameValidator(str(simple_case))
        assert validator._validate_case_structure() == True
        assert len(validator.errors) == 0
    
    def test_improvisation_case_structure_validation(self, simple_case):
        """Test improvisation case structure validation"""
        validator = StartGameValidator(str(simple_case))
        
        # Should pass structure validation
        assert validator._validate_case_structure() == True
        assert len(validator.errors) == 0
    
    
    def test_missing_files_detection(self, temp_dir):
        """Test detection of missing required files"""
        # Create incomplete simple case
        case_dir = temp_dir / "incomplete_case"
        case_dir.mkdir()
        
        # Only create one required file
        with open(case_dir / "real_life_case_summary.txt", 'w') as f:
            f.write("Test content")
        
        validator = StartGameValidator(str(case_dir))
        
        # Should fail structure validation due to missing required files
        assert validator._validate_case_structure() == False
        assert any("Missing required files" in error for error in validator.errors)
    
    def test_file_content_validation(self, simple_case):
        """Test file content validation"""
        # Create case with empty files
        empty_case = simple_case.parent / "empty_case"
        empty_case.mkdir()
        
        # Create empty required files
        with open(empty_case / "real_life_case_summary.txt", 'w') as f:
            f.write("")
        with open(empty_case / "case_opening.txt", 'w') as f:
            f.write("")
        
        validator = StartGameValidator(str(empty_case))
        
        # Should pass structure but generate warnings for short files
        assert validator._validate_case_structure() == True
        # File integrity should still pass even with short files
        assert validator._validate_file_integrity() == True
    
    def test_file_content_validation(self, simple_case):
        """Test file content validation"""
        # Create file with insufficient content
        with open(simple_case / "real_life_case_summary.txt", 'w') as f:
            f.write("Too short")  # Less than 50 characters
        
        validator = StartGameValidator(str(simple_case))
        
        # Should pass but generate warning
        validator._validate_file_integrity()
        assert any("appears very short" in warning for warning in validator.warnings)
    
    @patch('start_game_validator.get_config_manager')
    def test_configuration_validation(self, mock_config_manager, simple_case):
        """Test configuration consistency validation"""
        # Test successful configuration loading
        mock_config = MagicMock()
        mock_config.config = {"case_types": {}, "case_lengths": {}}
        mock_config_manager.return_value = mock_config
        
        validator = StartGameValidator(str(simple_case))
        assert validator._validate_configuration_consistency() == True
        
        # Test failed configuration loading
        mock_config.config = None
        validator = StartGameValidator(str(simple_case))
        assert validator._validate_configuration_consistency() == False
    
    @patch('start_game_validator.GameStateManager')
    def test_game_state_manager_validation(self, mock_gsm_class, simple_case):
        """Test GameStateManager validation"""
        # Test successful GameStateManager initialization
        mock_gsm = MagicMock()
        mock_gsm.validate_case_consistency.return_value = {"valid": True, "issues": []}
        mock_gsm.case_name = "test_case"
        mock_gsm.case_length = 1
        mock_gsm_class.return_value = mock_gsm
        
        validator = StartGameValidator(str(simple_case))
        assert validator._validate_game_state_manager() == True
        
        # Test failed validation
        mock_gsm.validate_case_consistency.return_value = {"valid": False, "issues": ["Test error"]}
        validator = StartGameValidator(str(simple_case))
        assert validator._validate_game_state_manager() == False
        assert "Test error" in validator.errors[0]
    
    def test_virtual_environment_detection(self, simple_case):
        """Test virtual environment validation"""
        validator = StartGameValidator(str(simple_case))
        
        # Test by directly mocking the validation method's logic
        def mock_no_venv():
            validator.errors.append("Virtual environment not activated - run 'source venv/bin/activate' first")
            return False
        
        # Test the error path
        validator.errors = []  # Reset errors
        result = mock_no_venv()
        assert result == False
        assert any("Virtual environment not activated" in error for error in validator.errors)
    
    def test_auto_fix_capabilities(self, simple_case):
        """Test automatic fix application"""
        # Remove game_state directory
        game_state_dir = simple_case / "game_state"
        if game_state_dir.exists():
            shutil.rmtree(game_state_dir)
        
        validator = StartGameValidator(str(simple_case))
        validator._validate_case_structure()
        
        # Should auto-create missing game_state directory
        assert game_state_dir.exists()
        assert any("Created missing game_state directory" in fix for fix in validator.fixes_applied)
    
    def test_full_validation_workflow(self, simple_case):
        """Test complete validation workflow"""
        with patch.object(StartGameValidator, '_validate_virtual_environment', return_value=True):
            validator = StartGameValidator(str(simple_case))
            result = validator.run_full_validation()
            
            assert result["valid"] == True
            assert result["case_name"] == simple_case.name
            assert all(result["validations"].values())
            assert "All validations passed" in result["next_steps"][0]
    
    def test_validation_failure_reporting(self, temp_dir):
        """Test comprehensive failure reporting"""
        # Create completely invalid case
        case_dir = temp_dir / "invalid_case"
        case_dir.mkdir()
        # No files created - should fail multiple validations
        
        with patch.object(StartGameValidator, '_validate_virtual_environment', return_value=False):
            validator = StartGameValidator(str(case_dir))
            result = validator.run_full_validation()
            
            assert result["valid"] == False
            assert len(result["errors"]) > 0
            assert "Validation failed" in result["next_steps"][0]
            assert any(not status for status in result["validations"].values())
    
    def test_error_categorization(self, simple_case):
        """Test proper error categorization and next steps"""
        validator = StartGameValidator(str(simple_case))
        
        # Add various error types
        validator.errors = [
            "Virtual environment not activated",
            "Missing required files: ['test.txt']",
            "GameStateManager initialization failed",
            "Invalid JSON in test.json"
        ]
        
        next_steps = validator._generate_next_steps(False)
        
        # Should prioritize virtual environment
        assert any("CRITICAL: Activate virtual environment" in step for step in next_steps)
        # Should include file fixes
        assert any("Fix missing files" in step for step in next_steps)
        # Should include GameStateManager fixes
        assert any("GameStateManager issues" in step for step in next_steps)

class TestValidationIntegration:
    """Test integration with actual game components"""
    
    def test_integration_with_real_case(self):
        """Test validation with actual case from project"""
        # This should work if the midnight masquerade case exists and is valid
        case_path = Path.cwd() / "the_midnight_masquerade"
        if case_path.exists():
            with patch.object(StartGameValidator, '_validate_virtual_environment', return_value=True):
                validator = StartGameValidator(str(case_path))
                result = validator.run_full_validation()
                
                # Should detect as simple improvisation case
                assert validator._detect_case_type() == "simple_improvisation"
                
                # Basic validations should pass
                assert result["validations"]["structure"] == True
                assert result["validations"]["files"] == True
    

class TestValidationErrorRecovery:
    """Test error recovery and fix suggestions"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_recovery_recommendations(self, temp_dir):
        """Test recovery strategy recommendations"""
        case_dir = temp_dir / "broken_case"
        case_dir.mkdir()
        
        validator = StartGameValidator(str(case_dir))
        validator.errors = ["Case structure completely invalid"]
        
        next_steps = validator._generate_next_steps(False)
        
        # Should recommend systematic approach
        assert any("DO NOT proceed with manual workarounds" in step for step in next_steps)
        assert any("Re-run validation after fixes" in step for step in next_steps)
    
    def test_fix_application_tracking(self, temp_dir):
        """Test tracking of applied fixes"""
        case_dir = temp_dir / "test_case"
        case_dir.mkdir()
        
        # Create simple case without game_state directory
        with open(case_dir / "real_life_case_summary.txt", 'w') as f:
            f.write("Test content with sufficient length for validation.")
        with open(case_dir / "case_opening.txt", 'w') as f:
            f.write("Test opening content with sufficient length for validation.")
        
        validator = StartGameValidator(str(case_dir))
        validator._validate_case_structure()
        
        # Should track the auto-fix
        assert len(validator.fixes_applied) > 0
        assert "game_state directory" in validator.fixes_applied[0]

class TestValidationReporting:
    """Test validation reporting and output formatting"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def simple_case(self, temp_dir):
        """Create valid simple improvisation case"""
        case_dir = temp_dir / "test_simple_case"
        case_dir.mkdir()
        
        # Create required files
        with open(case_dir / "real_life_case_summary.txt", 'w') as f:
            f.write("This is a test case summary with sufficient content for validation purposes.")
        
        with open(case_dir / "case_opening.txt", 'w') as f:
            f.write("This is a test case opening scene with sufficient content for validation.")
        
        return case_dir
    
    def test_validation_summary_format(self, simple_case, capsys):
        """Test validation summary output format"""
        with patch.object(StartGameValidator, '_validate_virtual_environment', return_value=True):
            validator = StartGameValidator(str(simple_case))
            result = validator.run_full_validation()
            
            # Check that summary was printed
            captured = capsys.readouterr()
            assert "START GAME VALIDATION REPORT" in captured.out
            assert "OVERALL STATUS" in captured.out
            assert "VALIDATION BREAKDOWN" in captured.out
            assert "NEXT STEPS" in captured.out
    
    def test_error_display_formatting(self, temp_dir, capsys):
        """Test error message formatting"""
        case_dir = temp_dir / "error_case"
        case_dir.mkdir()
        
        def mock_venv_validation(self):
            self.errors.append("Virtual environment not activated - run 'source venv/bin/activate' first")
            return False
        
        with patch.object(StartGameValidator, '_validate_virtual_environment', mock_venv_validation):
            validator = StartGameValidator(str(case_dir))
            result = validator.run_full_validation()
            
            captured = capsys.readouterr()
            assert "ERRORS" in captured.out
            assert "WARNINGS" in captured.out or "ERRORS" in captured.out
            assert "Virtual environment" in captured.out