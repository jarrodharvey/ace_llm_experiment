#!/usr/bin/env python3
"""
Test suite for evidence display functionality
"""

import unittest
import tempfile
import os
import json
from scripts.game_state_manager import GameStateManager
from scripts.test_case_manager import TestCaseManager
import subprocess

class TestEvidenceDisplay(unittest.TestCase):
    
    def setUp(self):
        """Set up test case with evidence"""
        self.test_manager = TestCaseManager()
        self.test_case_path = self.test_manager.create_test_case()
        self.gsm = GameStateManager(self.test_case_path)
        
        # Add sample evidence
        self.sample_evidence = [
            ("DNA Sample", "Blood evidence from crime scene"),
            ("Witness Statement", "Testimony from key witness"),
            ("Physical Evidence", "Weapon recovered at scene")
        ]
        
        for name, description in self.sample_evidence:
            self.gsm.add_evidence(name, description)
    
    def tearDown(self):
        """Clean up test case"""
        self.test_manager.cleanup_test_case()
    
    def test_show_evidence_command_exists(self):
        """Test that --show-evidence command exists in help"""
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            '--help'
        ], capture_output=True, text=True)
        
        self.assertIn('--show-evidence', result.stdout)
        self.assertIn('Show all collected evidence with descriptions', result.stdout)
    
    def test_show_evidence_with_evidence(self):
        """Test evidence display with evidence present"""
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            self.test_case_path, '--show-evidence'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('=== Evidence Collected ===', result.stdout)
        self.assertIn('DNA Sample', result.stdout)
        self.assertIn('Blood evidence from crime scene', result.stdout)
        self.assertIn('Witness Statement', result.stdout)
        self.assertIn('Physical Evidence', result.stdout)
    
    def test_show_evidence_without_evidence(self):
        """Test evidence display with no evidence"""
        # Create fresh test case without evidence
        fresh_path = self.test_manager.create_test_case()
        
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            fresh_path, '--show-evidence'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('=== Evidence Collected ===', result.stdout)
        self.assertIn('No evidence collected yet.', result.stdout)
    
    def test_evidence_display_format(self):
        """Test that evidence is displayed in correct format"""
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            self.test_case_path, '--show-evidence'
        ], capture_output=True, text=True)
        
        # Check format: number, name, description, discovered at
        lines = result.stdout.split('\n')
        evidence_lines = [line for line in lines if 'DNA Sample' in line]
        self.assertTrue(any('1. DNA Sample' in line for line in evidence_lines))
        
        desc_lines = [line for line in lines if 'Description:' in line]
        self.assertTrue(len(desc_lines) >= 3)  # At least 3 evidence pieces
        
        location_lines = [line for line in lines if 'Discovered at:' in line]
        self.assertTrue(len(location_lines) >= 3)  # At least 3 evidence pieces
    
    def test_evidence_state_consistency(self):
        """Test that evidence display matches stored state"""
        # Get evidence from display command
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            self.test_case_path, '--show-evidence'
        ], capture_output=True, text=True)
        
        # Get evidence from state file
        state_file = os.path.join(self.test_case_path, 'game_state', 'investigation_progress.json')
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        evidence_list = state.get('evidence_collected', [])
        
        # Verify counts match
        evidence_count = len(evidence_list)
        self.assertEqual(evidence_count, 3)
        
        # Verify each evidence item appears in display
        for evidence in evidence_list:
            self.assertIn(evidence['name'], result.stdout)
            self.assertIn(evidence['description'], result.stdout)

if __name__ == '__main__':
    unittest.main()