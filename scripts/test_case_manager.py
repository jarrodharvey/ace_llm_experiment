#!/usr/bin/env python3
"""
Test Case Manager
Provides automated test case setup and isolation to prevent testing on real cases.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Optional, List
import tempfile

class TestCaseManager:
    """Manages isolated test case environments for testing.
    
    Note: This is not a test class - it's a utility class for managing test cases.
    """
    
    def __init__(self, project_root: str = None):
        """Initialize test case manager.
        
        Args:
            project_root: Root directory of the project. If None, auto-detect.
        """
        if project_root is None:
            # Auto-detect project root from script location
            script_dir = Path(__file__).parent
            self.project_root = script_dir.parent
        else:
            self.project_root = Path(project_root)
        
        self.test_case_dir = self.project_root / "tests" / "test_case"
        
    def find_suitable_source_case(self) -> Optional[Path]:
        """Find a suitable existing case to clone for testing.
        
        Returns:
            Path to a suitable case directory, or None if none found
        """
        # Look for existing real cases in the project root
        potential_cases = []
        
        for item in self.project_root.iterdir():
            if item.is_dir() and item.name not in ['tests', 'scripts', 'docs', 'venv', '.git', '__pycache__']:
                # Check if it has the basic case structure
                if self._is_valid_case_structure(item):
                    potential_cases.append(item)
        
        if not potential_cases:
            return None
            
        # Prefer cases with complete structure
        for case in potential_cases:
            if self._has_complete_structure(case):
                return case
                
        # Fall back to any valid case
        return potential_cases[0] if potential_cases else None
    
    def _is_valid_case_structure(self, case_dir: Path) -> bool:
        """Check if directory has valid case structure.
        
        Args:
            case_dir: Directory to check
            
        Returns:
            True if valid case structure
        """
        required_files = ['case_opening.txt']
        required_dirs = ['game_state']
        
        for file in required_files:
            if not (case_dir / file).exists():
                return False
                
        for dir in required_dirs:
            if not (case_dir / dir).is_dir():
                return False
                
        return True
    
    def _has_complete_structure(self, case_dir: Path) -> bool:
        """Check if case has complete structure including optional directories.
        
        Args:
            case_dir: Directory to check
            
        Returns:
            True if complete structure
        """
        optional_dirs = ['saves', 'narrative_saves']
        
        for dir in optional_dirs:
            if not (case_dir / dir).exists():
                return False
                
        return True
    
    def create_test_case(self, source_case: str = None, clean: bool = True) -> Path:
        """Create isolated test case by cloning existing case.
        
        Args:
            source_case: Name of case to clone. If None, auto-select.
            clean: If True, remove existing test case first
            
        Returns:
            Path to created test case directory
            
        Raises:
            RuntimeError: If no suitable source case found or creation fails
        """
        # Clean existing test case if requested
        if clean and self.test_case_dir.exists():
            shutil.rmtree(self.test_case_dir)
        
        # Find source case
        if source_case:
            source_path = self.project_root / source_case
            if not source_path.exists() or not self._is_valid_case_structure(source_path):
                raise RuntimeError(f"Source case '{source_case}' not found or invalid structure")
        else:
            source_path = self.find_suitable_source_case()
            if not source_path:
                raise RuntimeError("No suitable source case found for cloning")
        
        # Create tests directory if it doesn't exist
        self.test_case_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Clone the source case
        shutil.copytree(source_path, self.test_case_dir)
        
        # Sanitize the test case
        self._sanitize_test_case()
        
        return self.test_case_dir
    
    def _sanitize_test_case(self):
        """Clean up test case to remove any sensitive or gameplay-specific data."""
        # Clear game state files
        game_state_dir = self.test_case_dir / "game_state"
        if game_state_dir.exists():
            for file in game_state_dir.glob("*.json"):
                self._reset_json_file(file)
            
            # Remove classification files
            for file in game_state_dir.glob("*.b64"):
                file.unlink(missing_ok=True)
        
        # Clear saves
        saves_dir = self.test_case_dir / "saves"
        if saves_dir.exists():
            for file in saves_dir.glob("*.json"):
                file.unlink()
        
        # Clear narrative saves
        narrative_saves_dir = self.test_case_dir / "narrative_saves"
        if narrative_saves_dir.exists():
            for file in narrative_saves_dir.glob("*.json"):
                file.unlink()
        
        # Update case opening to indicate test case
        case_opening = self.test_case_dir / "case_opening.txt"
        if case_opening.exists():
            with open(case_opening, 'w') as f:
                f.write("TITLE: Test Case Opening\n\n")
                f.write("This is an automated test case created for testing purposes.\n")
                f.write("Do not use this case for actual gameplay.\n\n")
                f.write("Type 'next' to continue\n")
    
    def _reset_json_file(self, file_path: Path):
        """Reset JSON file to default state."""
        filename = file_path.name
        
        default_content = {}
        
        if filename == "investigation_progress.json":
            default_content = {
                "case_type": "simple_improvisation",
                "case_length": 1,
                "current_phase": "investigation",
                "current_gate": None,
                "investigation_gates": {},
                "evidence_found": [],
                "character_relationships": {},
                "location_progress": {},
                "failed_attempts": [],
                "inspiration_usage": [],
                "trial_ready": False,
                "last_updated": None,
                "inspiration_log": [],
                "evidence_collected": []
            }
        elif filename == "trial_progress.json":
            default_content = {
                "trial_started": False,
                "current_witness": None,
                "cross_examination_active": False,
                "witness_statements": {},
                "penalties": 0,
                "victory_achieved": False
            }
        elif filename == "dice_rolls.json":
            default_content = {
                "rolls": [],
                "action_checks": []
            }
        
        with open(file_path, 'w') as f:
            json.dump(default_content, f, indent=2)
    
    def get_test_case_path(self) -> Path:
        """Get path to test case directory.
        
        Returns:
            Path to test case directory
        """
        return self.test_case_dir
    
    def cleanup_test_case(self):
        """Remove test case directory."""
        if self.test_case_dir.exists():
            shutil.rmtree(self.test_case_dir)
    
    def is_test_case_path(self, path: str) -> bool:
        """Check if given path is the test case directory.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is test case directory
        """
        return Path(path).resolve() == self.test_case_dir.resolve()


def setup_test_case(source_case: str = None, project_root: str = None) -> str:
    """Convenience function to set up test case.
    
    Args:
        source_case: Name of case to clone. If None, auto-select.
        project_root: Root directory of project. If None, auto-detect.
        
    Returns:
        String path to test case directory
        
    Raises:
        RuntimeError: If test case setup fails
    """
    manager = TestCaseManager(project_root)
    test_case_path = manager.create_test_case(source_case)
    return str(test_case_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage test case isolation")
    parser.add_argument('--create', action='store_true', help='Create test case')
    parser.add_argument('--cleanup', action='store_true', help='Remove test case')
    parser.add_argument('--source', help='Source case to clone')
    parser.add_argument('--project-root', help='Project root directory')
    
    args = parser.parse_args()
    
    manager = TestCaseManager(args.project_root)
    
    if args.create:
        try:
            test_case_path = manager.create_test_case(args.source)
            print(f"✅ Test case created at: {test_case_path}")
        except RuntimeError as e:
            print(f"❌ Failed to create test case: {e}")
            exit(1)
    
    if args.cleanup:
        manager.cleanup_test_case()
        print("✅ Test case cleaned up")