#!/usr/bin/env python3
"""
Test suite for character display functionality
"""

import unittest
import tempfile
import os
import json
from scripts.game_state_manager import GameStateManager
from scripts.test_case_manager import TestCaseManager
import subprocess

class TestCharacterDisplay(unittest.TestCase):
    
    def setUp(self):
        """Set up test case with characters"""
        self.test_manager = TestCaseManager()
        self.test_case_path = self.test_manager.create_test_case()
        self.gsm = GameStateManager(self.test_case_path)
        
        # Add sample characters
        self.gsm.update_character_trust("Alice Johnson", 5)
        self.gsm.update_character_trust("Bob Smith", -2)
        self.gsm.update_character_trust("Carol Davis", 0)
        
        # Interview some witnesses
        self.gsm.interview_witness("Alice Johnson")
        self.gsm.interview_witness("Bob Smith")
        
        # Add character facts
        if "character_facts" not in self.gsm.current_state:
            self.gsm.current_state["character_facts"] = {}
        
        self.gsm.current_state["character_facts"]["Alice Johnson"] = {
            "role": "witness",
            "occupation": "bank teller"
        }
        self.gsm.current_state["character_facts"]["Bob Smith"] = {
            "role": "suspect", 
            "occupation": "security guard"
        }
        self.gsm.save_current_state_to_file()
    
    def tearDown(self):
        """Clean up test case"""
        self.test_manager.cleanup_test_case()
    
    def test_show_characters_command_exists(self):
        """Test that --show-characters command exists in help"""
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            '--help'
        ], capture_output=True, text=True)
        
        self.assertIn('--show-characters', result.stdout)
        self.assertIn('Show all characters with trust levels and roles', result.stdout)
    
    def test_show_characters_with_characters(self):
        """Test character display with characters present"""
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            self.test_case_path, '--show-characters'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('=== Characters in Case ===', result.stdout)
        self.assertIn('Alice Johnson', result.stdout)
        self.assertIn('Bob Smith', result.stdout)
        self.assertIn('Carol Davis', result.stdout)
        self.assertIn('Trust Level: 5 😊', result.stdout)  # Alice - positive
        self.assertIn('Trust Level: -2 😠', result.stdout)  # Bob - negative
        self.assertIn('Trust Level: 0 😐', result.stdout)  # Carol - neutral
    
    def test_show_characters_without_characters(self):
        """Test character display with no characters"""
        # Create fresh test case without characters
        fresh_path = self.test_manager.create_test_case()
        
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            fresh_path, '--show-characters'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('=== Characters in Case ===', result.stdout)
        self.assertIn('No characters introduced yet.', result.stdout)
    
    def test_show_witnesses_command_exists(self):
        """Test that --show-witnesses command exists in help"""
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            '--help'
        ], capture_output=True, text=True)
        
        self.assertIn('--show-witnesses', result.stdout)
        self.assertIn('Show all interviewed witnesses', result.stdout)
    
    def test_show_witnesses_with_witnesses(self):
        """Test witness display with witnesses present"""
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            self.test_case_path, '--show-witnesses'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('=== Interviewed Witnesses ===', result.stdout)
        self.assertIn('Alice Johnson', result.stdout)
        self.assertIn('Bob Smith', result.stdout)
        self.assertNotIn('Carol Davis', result.stdout)  # Not interviewed
    
    def test_show_witnesses_without_witnesses(self):
        """Test witness display with no witnesses"""
        # Create fresh test case without witnesses
        fresh_path = self.test_manager.create_test_case()
        
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            fresh_path, '--show-witnesses'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('=== Interviewed Witnesses ===', result.stdout)
        self.assertIn('No witnesses interviewed yet.', result.stdout)
    
    def test_check_role_command_exists(self):
        """Test that --check-role command exists in help"""
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            '--help'
        ], capture_output=True, text=True)
        
        self.assertIn('--check-role', result.stdout)
        self.assertIn('Check if specific role already exists', result.stdout)
    
    def test_check_role_no_existing_role(self):
        """Test role checking when role doesn't exist"""
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            self.test_case_path, '--check-role', 'prosecutor'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('=== Role Check: prosecutor ===', result.stdout)
        self.assertIn('✅ No existing prosecutor found', result.stdout)
        self.assertIn('Safe to create new character', result.stdout)
    
    def test_character_facts_display(self):
        """Test that character facts are displayed correctly"""
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            self.test_case_path, '--show-characters'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        # Check that character facts are displayed
        self.assertIn('Role: witness', result.stdout)
        self.assertIn('Occupation: bank teller', result.stdout)
        self.assertIn('Role: suspect', result.stdout)
        self.assertIn('Occupation: security guard', result.stdout)
    
    def test_interviewed_status_display(self):
        """Test that interviewed status is shown correctly"""
        result = subprocess.run([
            'python3', 'scripts/game_state_manager.py', 
            self.test_case_path, '--show-characters'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        # Alice and Bob should show as interviewed
        lines = result.stdout.split('\n')
        alice_section = []
        bob_section = []
        carol_section = []
        
        current_section = None
        for line in lines:
            if 'Alice Johnson' in line:
                current_section = alice_section
            elif 'Bob Smith' in line:
                current_section = bob_section
            elif 'Carol Davis' in line:
                current_section = carol_section
            elif line.strip() and current_section is not None:
                if line.startswith((' ', '\t')) or '.' in line[:3]:
                    current_section.append(line)
                else:
                    current_section = None
        
        # Alice and Bob should be interviewed
        alice_text = ' '.join(alice_section)
        bob_text = ' '.join(bob_section)
        carol_text = ' '.join(carol_section)
        
        self.assertIn('✅ Interviewed', alice_text)
        self.assertIn('✅ Interviewed', bob_text)
        self.assertNotIn('✅ Interviewed', carol_text)

if __name__ == '__main__':
    unittest.main()