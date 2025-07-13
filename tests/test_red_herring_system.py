#!/usr/bin/env python3
"""
Unit tests for the Red Herring Classification System
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

from red_herring_system import RedHerringClassifier


class TestRedHerringSystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test case with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.case_path = Path(self.test_dir) / "test_case"
        self.case_path.mkdir(parents=True, exist_ok=True)
        (self.case_path / "game_state").mkdir(parents=True, exist_ok=True)
        
        # Create minimal case structure for CLI tests
        case_opening = self.case_path / "case_opening.txt"
        case_opening.write_text("Test case opening")
        
        # Create minimal investigation progress
        progress_file = self.case_path / "game_state" / "investigation_progress.json"
        minimal_progress = {
            "case_type": "simple_improvisation",
            "case_length": 2,
            "current_phase": "investigation",
            "current_gate": "witness_interviews",
            "investigation_gates": {"witness_interviews": {"status": "pending"}},
            "evidence_found": [],
            "character_relationships": {},
            "location_progress": {},
            "failed_attempts": [],
            "inspiration_usage": [],
            "trial_ready": False,
            "last_updated": None
        }
        progress_file.write_text(json.dumps(minimal_progress, indent=2))
        
        self.classifier = RedHerringClassifier(str(self.case_path))
    
    def tearDown(self):
        """Clean up test directory"""
        shutil.rmtree(self.test_dir)
    
    def test_deterministic_classification(self):
        """Test that the same character name always gets the same classification"""
        # Test multiple times to ensure deterministic behavior
        for _ in range(5):
            classification1 = self.classifier.classify_character("John Smith", 2)
            classification2 = self.classifier.classify_character("John Smith", 2)
            self.assertEqual(classification1, classification2)
    
    def test_case_length_probabilities(self):
        """Test that case length affects killer probabilities correctly"""
        test_characters = [f"Character{i}" for i in range(100)]
        
        # Test 1-day case (1/2 = 50% killer rate)
        day1_killers = 0
        for char in test_characters:
            if self.classifier._generate_role(char, 1) == "true_killer":
                day1_killers += 1
        day1_rate = day1_killers / len(test_characters)
        
        # Test 2-day case (1/3 = 33% killer rate)  
        day2_killers = 0
        for char in test_characters:
            if self.classifier._generate_role(char, 2) == "true_killer":
                day2_killers += 1
        day2_rate = day2_killers / len(test_characters)
        
        # Test 3-day case (1/4 = 25% killer rate)
        day3_killers = 0
        for char in test_characters:
            if self.classifier._generate_role(char, 3) == "true_killer":
                day3_killers += 1
        day3_rate = day3_killers / len(test_characters)
        
        # Verify the trend: 1-day > 2-day > 3-day killer rates
        self.assertGreater(day1_rate, day2_rate)
        self.assertGreater(day2_rate, day3_rate)
        
        # Check approximate expected values (with tolerance for randomness)
        self.assertAlmostEqual(day1_rate, 0.5, delta=0.1)
        self.assertAlmostEqual(day2_rate, 0.33, delta=0.1)
        self.assertAlmostEqual(day3_rate, 0.25, delta=0.1)
    
    def test_base64_storage(self):
        """Test that classifications are properly stored in base64 format"""
        # Classify some characters
        self.classifier.classify_character("Alice Cooper", 2)
        self.classifier.classify_character("Bob Dylan", 2)
        
        # Check that file exists and is base64 encoded
        classifications_file = self.case_path / "game_state" / "character_classifications.b64"
        self.assertTrue(classifications_file.exists())
        
        # Read file and verify it's base64 (no plain JSON)
        with open(classifications_file, 'r') as f:
            content = f.read()
        
        # Base64 content should not contain readable JSON structure
        self.assertNotIn('"Alice Cooper"', content)
        self.assertNotIn('"Bob Dylan"', content)
        self.assertNotIn('true_killer', content)
        self.assertNotIn('red_herring', content)
    
    def test_classification_persistence(self):
        """Test that classifications persist across classifier instances"""
        # Classify character with first classifier
        classification1 = self.classifier.classify_character("Persistent Person", 2)
        
        # Create new classifier instance for same case
        new_classifier = RedHerringClassifier(str(self.case_path))
        
        # Check that classification is the same
        classification2 = new_classifier.get_character_role("Persistent Person")
        self.assertEqual(classification1, classification2)
    
    def test_statistics_calculation(self):
        """Test classification statistics are calculated correctly"""
        # Create known distribution
        self.classifier.classify_character("Killer One", 1)  # Should be deterministic
        self.classifier.classify_character("Herring One", 1)
        self.classifier.classify_character("Herring Two", 1) 
        
        stats = self.classifier.get_classification_stats(1)
        
        # Verify basic stats
        self.assertEqual(stats['case_length'], 1)
        self.assertEqual(stats['total_characters'], 3)
        self.assertEqual(stats['expected_killer_rate'], 0.5)
        self.assertEqual(stats['expected_red_herring_rate'], 0.5)
    
    def test_role_lists(self):
        """Test that role lists are correctly maintained"""
        # Classify characters with known outcomes
        self.classifier.classify_character("Alice Wonder", 3)
        self.classifier.classify_character("Bob Builder", 3)
        
        killers = self.classifier.get_potential_killers()
        herrings = self.classifier.get_red_herrings()
        
        # Verify lists contain correct characters
        self.assertIsInstance(killers, list)
        self.assertIsInstance(herrings, list)
        self.assertEqual(len(killers) + len(herrings), 2)
        
        # Verify no overlap
        self.assertEqual(len(set(killers) & set(herrings)), 0)
    
    def test_spoiler_protection(self):
        """Test that classification can be hidden for spoiler protection"""
        # Classify some characters
        classification1 = self.classifier.classify_character("Secret Killer", 2)
        classification2 = self.classifier.classify_character("Red Herring Person", 2)
        
        # Test that we can retrieve classifications (for GM use)
        role1 = self.classifier.get_character_role("Secret Killer")
        role2 = self.classifier.get_character_role("Red Herring Person")
        
        self.assertEqual(role1, classification1)
        self.assertEqual(role2, classification2)
        
        # Test that the base64 storage hides the information from casual viewing
        classifications_file = self.case_path / "game_state" / "character_classifications.b64"
        with open(classifications_file, 'r') as f:
            encoded_content = f.read()
        
        # Base64 content should not contain readable classification terms
        self.assertNotIn('true_killer', encoded_content)
        self.assertNotIn('red_herring', encoded_content)
        self.assertNotIn('Secret Killer', encoded_content)
        self.assertNotIn('Red Herring Person', encoded_content)
        
        # But the decoded content should contain the actual classifications
        import base64
        decoded_content = base64.b64decode(encoded_content).decode('utf-8')
        decoded_data = json.loads(decoded_content)
        
        self.assertIn("Secret Killer", decoded_data)
        self.assertIn("Red Herring Person", decoded_data)
    
    def test_role_based_weighting(self):
        """Test that role hints affect killer probability correctly"""
        # Test high authority roles (0.3x weight)
        detective_prob = self.classifier.get_weighted_probability(2, "detective")
        self.assertAlmostEqual(detective_prob, 1/3 * 0.3, places=3)  # 33% * 0.3 = 10%
        
        judge_prob = self.classifier.get_weighted_probability(1, "judge") 
        self.assertAlmostEqual(judge_prob, 0.5 * 0.3, places=3)  # 50% * 0.3 = 15%
        
        # Test normal authority roles (1.0x weight)
        witness_prob = self.classifier.get_weighted_probability(2, "witness")
        self.assertAlmostEqual(witness_prob, 1/3 * 1.0, places=3)  # 33% * 1.0 = 33%
        
        # Test high suspicion roles (1.8x weight)
        rival_prob = self.classifier.get_weighted_probability(3, "business rival")
        self.assertAlmostEqual(rival_prob, 0.25 * 1.8, places=3)  # 25% * 1.8 = 45%
        
        guard_prob = self.classifier.get_weighted_probability(1, "security guard")
        self.assertAlmostEqual(guard_prob, 0.5 * 1.8, places=3)  # 50% * 1.8 = 90%
    
    def test_role_weight_lookup(self):
        """Test role weight lookup with various formats"""
        # Exact matches
        self.assertEqual(self.classifier._get_role_weight("detective"), 0.3)
        self.assertEqual(self.classifier._get_role_weight("witness"), 1.0)
        self.assertEqual(self.classifier._get_role_weight("security guard"), 1.8)
        
        # Case insensitive
        self.assertEqual(self.classifier._get_role_weight("DETECTIVE"), 0.3)
        self.assertEqual(self.classifier._get_role_weight("Security Guard"), 1.8)
        
        # Partial matches
        self.assertEqual(self.classifier._get_role_weight("police officer"), 0.3)  # Contains "police"
        self.assertEqual(self.classifier._get_role_weight("night security"), 1.8)  # Contains "security"
        
        # No match returns default
        self.assertEqual(self.classifier._get_role_weight("alien"), 1.0)
        self.assertEqual(self.classifier._get_role_weight(None), 1.0)
    
    def test_deterministic_with_role_weighting(self):
        """Test that role weighting maintains deterministic behavior"""
        # Same character + role should always give same result
        for _ in range(5):
            result1 = self.classifier.classify_character("Test Person", 2, "detective")
            result2 = self.classifier.classify_character("Test Person", 2, "detective")
            self.assertEqual(result1, result2)
        
        # Different roles should potentially give different results
        detective_result = self.classifier._generate_role_weighted("Same Name", 2, "detective")
        guard_result = self.classifier._generate_role_weighted("Same Name", 2, "security guard")
        
        # They might be the same due to randomness, but the weighted probabilities should differ
        detective_prob = self.classifier.get_weighted_probability(2, "detective")
        guard_prob = self.classifier.get_weighted_probability(2, "security guard")
        self.assertNotEqual(detective_prob, guard_prob)


if __name__ == '__main__':
    unittest.main()