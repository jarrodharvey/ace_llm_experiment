#!/usr/bin/env python3
"""
Unit tests for the Test Case Manager
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os
import json

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from test_case_manager import TestCaseManager, setup_test_case


class TestTestCaseManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir)
        
        # Create a mock real case for testing
        self.real_case_dir = self.project_root / "mock_real_case"
        self.real_case_dir.mkdir()
        
        # Create required structure
        (self.real_case_dir / "case_opening.txt").write_text("Mock case opening")
        (self.real_case_dir / "game_state").mkdir()
        (self.real_case_dir / "saves").mkdir()
        (self.real_case_dir / "narrative_saves").mkdir()
        
        # Create game state files
        investigation_state = {
            "case_type": "simple_improvisation",
            "case_length": 2,
            "current_phase": "investigation",
            "evidence_collected": [{"name": "Test Evidence", "description": "Test"}],
            "character_trust_levels": {"Test Character": 0},
            "inspiration_log": [{"word": "test", "context": "testing"}]
        }
        
        with open(self.real_case_dir / "game_state" / "investigation_progress.json", 'w') as f:
            json.dump(investigation_state, f)
        
        with open(self.real_case_dir / "game_state" / "trial_progress.json", 'w') as f:
            json.dump({"trial_started": False}, f)
        
        with open(self.real_case_dir / "game_state" / "dice_rolls.json", 'w') as f:
            json.dump({"rolls": [{"result": 15}]}, f)
        
        # Create a classification file to test sanitization
        with open(self.real_case_dir / "game_state" / "character_classifications.b64", 'w') as f:
            f.write("dGVzdA==")  # base64 encoded "test"
        
        # Create save files to test cleanup
        (self.real_case_dir / "saves" / "test_save.json").write_text('{"test": "data"}')
        (self.real_case_dir / "narrative_saves" / "test_narrative.json").write_text('{"narrative": "data"}')
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_manager_initialization(self):
        """Test TestCaseManager initialization"""
        manager = TestCaseManager(str(self.project_root))
        
        self.assertEqual(manager.project_root, self.project_root)
        self.assertEqual(manager.test_case_dir, self.project_root / "tests" / "test_case")
    
    def test_find_suitable_source_case(self):
        """Test finding suitable source case"""
        manager = TestCaseManager(str(self.project_root))
        
        source_case = manager.find_suitable_source_case()
        self.assertIsNotNone(source_case)
        self.assertEqual(source_case.name, "mock_real_case")
    
    def test_valid_case_structure_detection(self):
        """Test case structure validation"""
        manager = TestCaseManager(str(self.project_root))
        
        # Valid case
        self.assertTrue(manager._is_valid_case_structure(self.real_case_dir))
        
        # Invalid case (missing required files)
        invalid_case = self.project_root / "invalid_case"
        invalid_case.mkdir()
        self.assertFalse(manager._is_valid_case_structure(invalid_case))
    
    def test_complete_structure_detection(self):
        """Test complete structure detection"""
        manager = TestCaseManager(str(self.project_root))
        
        # Complete structure
        self.assertTrue(manager._has_complete_structure(self.real_case_dir))
        
        # Incomplete structure
        incomplete_case = self.project_root / "incomplete_case"
        incomplete_case.mkdir()
        (incomplete_case / "case_opening.txt").write_text("test")
        (incomplete_case / "game_state").mkdir()
        self.assertFalse(manager._has_complete_structure(incomplete_case))
    
    def test_create_test_case(self):
        """Test test case creation"""
        manager = TestCaseManager(str(self.project_root))
        
        test_case_path = manager.create_test_case("mock_real_case")
        
        # Verify test case was created
        self.assertTrue(test_case_path.exists())
        self.assertEqual(test_case_path.name, "test_case")
        
        # Verify structure was copied
        self.assertTrue((test_case_path / "case_opening.txt").exists())
        self.assertTrue((test_case_path / "game_state").exists())
        self.assertTrue((test_case_path / "saves").exists())
        self.assertTrue((test_case_path / "narrative_saves").exists())
    
    def test_test_case_sanitization(self):
        """Test that test case is properly sanitized"""
        manager = TestCaseManager(str(self.project_root))
        
        test_case_path = manager.create_test_case("mock_real_case")
        
        # Check case opening was updated
        case_opening = (test_case_path / "case_opening.txt").read_text()
        self.assertIn("automated test case", case_opening)
        self.assertIn("testing purposes", case_opening)
        
        # Check game state was reset
        with open(test_case_path / "game_state" / "investigation_progress.json") as f:
            investigation_state = json.load(f)
        
        self.assertEqual(investigation_state["evidence_collected"], [])
        self.assertEqual(investigation_state["inspiration_log"], [])
        self.assertEqual(investigation_state["current_phase"], "investigation")
        
        # Check classification files were removed
        self.assertFalse((test_case_path / "game_state" / "character_classifications.b64").exists())
        
        # Check save files were removed
        self.assertEqual(len(list((test_case_path / "saves").glob("*.json"))), 0)
        self.assertEqual(len(list((test_case_path / "narrative_saves").glob("*.json"))), 0)
    
    def test_path_isolation_validation(self):
        """Test that path isolation validation works"""
        manager = TestCaseManager(str(self.project_root))
        
        test_case_path = manager.create_test_case("mock_real_case")
        
        # Should recognize test case path
        self.assertTrue(manager.is_test_case_path(str(test_case_path)))
        
        # Should not recognize real case path
        self.assertFalse(manager.is_test_case_path(str(self.real_case_dir)))
    
    def test_cleanup_test_case(self):
        """Test test case cleanup"""
        manager = TestCaseManager(str(self.project_root))
        
        test_case_path = manager.create_test_case("mock_real_case")
        self.assertTrue(test_case_path.exists())
        
        manager.cleanup_test_case()
        self.assertFalse(test_case_path.exists())
    
    def test_setup_test_case_convenience_function(self):
        """Test the convenience function"""
        test_case_path = setup_test_case("mock_real_case", str(self.project_root))
        
        self.assertTrue(Path(test_case_path).exists())
        self.assertEqual(Path(test_case_path).name, "test_case")
    
    def test_error_handling_invalid_source(self):
        """Test error handling for invalid source case"""
        manager = TestCaseManager(str(self.project_root))
        
        with self.assertRaises(RuntimeError):
            manager.create_test_case("nonexistent_case")
    
    def test_error_handling_no_suitable_cases(self):
        """Test error handling when no suitable cases are found"""
        empty_project = Path(tempfile.mkdtemp())
        manager = TestCaseManager(str(empty_project))
        
        with self.assertRaises(RuntimeError):
            manager.create_test_case()
        
        shutil.rmtree(empty_project)


if __name__ == '__main__':
    unittest.main()