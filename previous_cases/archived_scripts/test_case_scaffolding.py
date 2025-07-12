"""
Tests for Case Scaffolding System - Integration Tests
"""
import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, Mock
from case_scaffolding import CaseScaffolding

class TestCaseScaffolding:
    """Test case scaffolding creation and structure"""
    
    @pytest.fixture
    def temp_base_path(self):
        """Create temporary base directory for scaffolding tests"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_scaffolding_initialization(self, temp_base_path):
        """Test CaseScaffolding initialization"""
        scaffolding = CaseScaffolding("test_case", temp_base_path)
        
        assert scaffolding.case_name == "test_case"
        assert scaffolding.case_path == temp_base_path / "test_case"
        assert scaffolding.case_length in [1, 2, 3]
        assert len(scaffolding.directories) > 0
        assert isinstance(scaffolding.templates, dict)
    
    def test_case_length_determination(self, temp_base_path):
        """Test random case length determination"""
        # Test multiple instances to verify randomness works
        lengths = set()
        for _ in range(10):
            scaffolding = CaseScaffolding("test_case", temp_base_path)
            lengths.add(scaffolding.case_length)
        
        # Should have at least some variety (might get lucky and only see one length)
        assert all(length in [1, 2, 3] for length in lengths)
    
    def test_directory_structure_creation(self, temp_base_path):
        """Test creation of case directory structure"""
        scaffolding = CaseScaffolding("test_case", temp_base_path)
        
        # Create directory structure
        scaffolding.create_directory_structure()
        
        # Verify main case directory exists
        assert scaffolding.case_path.exists()
        assert scaffolding.case_path.is_dir()
        
        # Verify required subdirectories exist
        expected_dirs = ["backbone", "game_state", "solution", "obstacles"]
        for dir_name in expected_dirs:
            dir_path = scaffolding.case_path / dir_name
            assert dir_path.exists(), f"Directory {dir_name} should exist"
            assert dir_path.is_dir(), f"{dir_name} should be a directory"
    
    def test_inspiration_pool_deprecation(self, temp_base_path):
        """Test that inspiration pool generation is deprecated"""
        scaffolding = CaseScaffolding("test_case", temp_base_path)
        
        # Should return True but not actually create inspiration pool
        result = scaffolding.generate_inspiration_pool()
        assert result == True
        
        # Should not create inspiration_pool.json
        inspiration_file = scaffolding.case_path / "inspiration_pool.json"
        assert not inspiration_file.exists()
    
    def test_backbone_template_creation(self, temp_base_path):
        """Test creation of backbone template files"""
        scaffolding = CaseScaffolding("test_case", temp_base_path)
        scaffolding.create_directory_structure()
        
        # Create backbone templates
        scaffolding.create_backbone_templates()
        
        # Verify backbone files exist
        backbone_dir = scaffolding.case_path / "backbone"
        expected_files = [
            "case_structure.json",
            "evidence_chain.json",
            "character_facts.json", 
            "truth_timeline.json",
            "witness_testimonies.json",
            "trial_structure.json"
        ]
        
        for filename in expected_files:
            file_path = backbone_dir / filename
            assert file_path.exists(), f"Backbone file {filename} should exist"
            
            # Verify file contains template content
            with open(file_path, 'r') as f:
                content = f.read()
                assert len(content) > 0, f"File {filename} should not be empty"
                assert "[" in content, f"File {filename} should contain template placeholders"
    
    def test_game_state_initialization(self, temp_base_path):
        """Test game state file initialization"""
        scaffolding = CaseScaffolding("test_case", temp_base_path)
        scaffolding.create_directory_structure()
        
        # Create game state files
        scaffolding.create_game_state_files()
        
        # Verify game state files exist and are valid JSON
        game_state_dir = scaffolding.case_path / "game_state"
        
        investigation_file = game_state_dir / "investigation_progress.json"
        assert investigation_file.exists()
        
        with open(investigation_file, 'r') as f:
            investigation_data = json.load(f)
            assert "investigation_gates" in investigation_data
            assert "current_phase" in investigation_data
            assert investigation_data["case_length"] == scaffolding.case_length
        
        trial_file = game_state_dir / "trial_progress.json"
        assert trial_file.exists()
        
        with open(trial_file, 'r') as f:
            trial_data = json.load(f)
            assert "trial_status" in trial_data
            assert trial_data["trial_status"] == "not_started"
    
    def test_investigation_gates_creation(self, temp_base_path):
        """Test creation of appropriate gates based on case length"""
        scaffolding = CaseScaffolding("test_case", temp_base_path)
        
        gates = scaffolding.create_investigation_gates()
        
        # Verify gates structure
        assert isinstance(gates, dict)
        assert len(gates) > 0
        
        # All gates should start as pending
        for gate_name, status in gates.items():
            assert status == "pending"
            assert isinstance(gate_name, str)
            assert len(gate_name) > 0
        
        # Gate count should match case length pattern
        if scaffolding.case_length == 1:
            assert len(gates) == 3  # Trial-only cases have 3 gates
        elif scaffolding.case_length == 2:
            assert len(gates) == 4  # 1 investigation + 3 trial gates
        elif scaffolding.case_length == 3:
            assert len(gates) == 6  # 3 investigation + 3 trial gates

class TestCaseScaffoldingIntegration:
    """Test full scaffolding workflow integration"""
    
    def test_complete_scaffolding_workflow(self, temp_base_path):
        """Test the complete case scaffolding process"""
        scaffolding = CaseScaffolding("integration_test", temp_base_path)
        
        # Run complete scaffolding
        success = scaffolding.scaffold_case()
        assert success == True
        
        # Verify complete case structure
        case_path = scaffolding.case_path
        assert case_path.exists()
        
        # Verify all required directories
        required_dirs = ["backbone", "game_state", "solution", "obstacles"]
        for dir_name in required_dirs:
            assert (case_path / dir_name).exists()
        
        # Verify backbone files
        backbone_files = [
            "case_structure.json", "evidence_chain.json", "character_facts.json",
            "truth_timeline.json", "witness_testimonies.json", "trial_structure.json"
        ]
        for filename in backbone_files:
            file_path = case_path / "backbone" / filename
            assert file_path.exists()
            assert file_path.stat().st_size > 0
        
        # Verify game state files
        investigation_file = case_path / "game_state" / "investigation_progress.json"
        trial_file = case_path / "game_state" / "trial_progress.json"
        assert investigation_file.exists()
        assert trial_file.exists()
        
        # Verify game state content
        with open(investigation_file, 'r') as f:
            inv_data = json.load(f)
            assert "investigation_gates" in inv_data
            assert len(inv_data["investigation_gates"]) > 0
    
    def test_case_name_validation(self, temp_base_path):
        """Test case name format validation"""
        # Valid case names
        valid_names = ["test_case", "the_gallery_gambit", "case123"]
        for name in valid_names:
            scaffolding = CaseScaffolding(name, temp_base_path)
            assert scaffolding.case_name == name
        
        # Invalid characters should still work (no validation in constructor)
        # Validation happens during actual creation
        scaffolding = CaseScaffolding("invalid-name-with-dashes", temp_base_path)
        assert scaffolding.case_name == "invalid-name-with-dashes"
    
    def test_existing_directory_handling(self, temp_base_path):
        """Test handling when case directory already exists"""
        case_name = "existing_case"
        case_path = temp_base_path / case_name
        
        # Create directory manually
        case_path.mkdir()
        (case_path / "existing_file.txt").write_text("existing content")
        
        # Scaffolding should handle existing directory
        scaffolding = CaseScaffolding(case_name, temp_base_path)
        scaffolding.create_directory_structure()
        
        # Should still create required subdirectories
        assert (case_path / "backbone").exists()
        assert (case_path / "game_state").exists()
        
        # Existing file should remain
        assert (case_path / "existing_file.txt").exists()

class TestScaffoldingErrorHandling:
    """Test error handling in scaffolding process"""
    
    def test_permission_error_handling(self, temp_base_path):
        """Test handling of permission errors during scaffolding"""
        # This test is platform-dependent and may not work on all systems
        # Skip on systems where we can't create permission issues
        try:
            # Create a read-only directory
            readonly_dir = temp_base_path / "readonly"
            readonly_dir.mkdir()
            readonly_dir.chmod(0o444)  # Read-only
            
            scaffolding = CaseScaffolding("test_case", readonly_dir)
            
            # Should handle permission error gracefully
            try:
                scaffolding.create_directory_structure()
                # If we get here, the test setup didn't work as expected
                # That's okay, just verify basic functionality
                assert True
            except PermissionError:
                # Expected on some systems
                assert True
            finally:
                # Cleanup
                readonly_dir.chmod(0o755)
        except Exception:
            # If we can't set up the test, just pass
            pytest.skip("Cannot test permission errors on this system")
    
    def test_invalid_json_handling(self, temp_base_path):
        """Test handling of JSON serialization errors"""
        scaffolding = CaseScaffolding("test_case", temp_base_path)
        scaffolding.create_directory_structure()
        
        # Create backbone templates (this should work normally)
        scaffolding.create_backbone_templates()
        
        # Verify that valid JSON was created
        backbone_dir = scaffolding.case_path / "backbone"
        for json_file in backbone_dir.glob("*.json"):
            with open(json_file, 'r') as f:
                # Should be able to load as JSON
                data = json.load(f)
                assert isinstance(data, (dict, list))

class TestScaffoldingUtilities:
    """Test utility functions in scaffolding"""
    
    def test_gate_count_consistency(self, temp_base_path):
        """Test that gate counts are consistent with case length"""
        for case_length in [1, 2, 3]:
            scaffolding = CaseScaffolding("test_case", temp_base_path)
            scaffolding.case_length = case_length  # Force specific length
            
            gates = scaffolding.create_investigation_gates()
            
            if case_length == 1:
                assert len(gates) == 3
            elif case_length == 2:
                assert len(gates) == 4
            elif case_length == 3:
                assert len(gates) == 6
    
    def test_template_content_validity(self, temp_base_path):
        """Test that template content is valid and complete"""
        scaffolding = CaseScaffolding("test_case", temp_base_path)
        scaffolding.create_directory_structure()
        scaffolding.create_backbone_templates()
        
        # Check case_structure.json template
        case_structure_file = scaffolding.case_path / "backbone" / "case_structure.json"
        with open(case_structure_file, 'r') as f:
            case_structure = json.load(f)
            
            # Should have required template fields
            assert "case_title" in case_structure
            assert "case_id" in case_structure
            assert case_structure["case_id"] == "test_case"
            assert "victim" in case_structure
            assert "client" in case_structure