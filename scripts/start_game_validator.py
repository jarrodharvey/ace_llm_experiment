#!/usr/bin/env python3
"""
Start Game Validator
Comprehensive pre-game validation framework with root cause analysis and automated fixes.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from game_state_manager import GameStateManager
from case_config import get_config_manager

class StartGameValidator:
    """Comprehensive validation framework for game startup"""
    
    def __init__(self, case_path: str):
        self.case_path = Path(case_path)
        self.case_name = self.case_path.name
        self.config_manager = get_config_manager()
        self.validation_results = []
        self.errors = []
        self.warnings = []
        self.fixes_applied = []
        
    def run_full_validation(self) -> Dict[str, Any]:
        """Run comprehensive pre-game validation with root cause analysis"""
        print(f"🔍 Starting comprehensive validation for '{self.case_name}'...")
        
        # Phase 1: Basic Structure Validation
        print("📁 Phase 1: Validating case structure...")
        structure_valid = self._validate_case_structure()
        
        # Phase 2: File Integrity Validation  
        print("📄 Phase 2: Validating file integrity...")
        files_valid = self._validate_file_integrity()
        
        # Phase 3: Configuration Consistency
        print("⚙️  Phase 3: Validating configuration consistency...")
        config_valid = self._validate_configuration_consistency()
        
        # Phase 4: Game State Manager Validation
        print("🎮 Phase 4: Validating game state manager...")
        gsm_valid = self._validate_game_state_manager()
        
        # Phase 5: Virtual Environment Validation
        print("🐍 Phase 5: Validating virtual environment...")
        venv_valid = self._validate_virtual_environment()
        
        # Compile Results
        all_valid = all([structure_valid, files_valid, config_valid, gsm_valid, venv_valid])
        
        result = {
            "valid": all_valid,
            "case_name": self.case_name,
            "case_path": str(self.case_path),
            "validations": {
                "structure": structure_valid,
                "files": files_valid, 
                "configuration": config_valid,
                "game_state_manager": gsm_valid,
                "virtual_environment": venv_valid
            },
            "errors": self.errors,
            "warnings": self.warnings,
            "fixes_applied": self.fixes_applied,
            "next_steps": self._generate_next_steps(all_valid)
        }
        
        self._print_validation_summary(result)
        return result
    
    def _validate_case_structure(self) -> bool:
        """Validate basic case directory structure"""
        try:
            if not self.case_path.exists():
                self.errors.append(f"Case directory does not exist: {self.case_path}")
                return False
            
            if not self.case_path.is_dir():
                self.errors.append(f"Case path is not a directory: {self.case_path}")
                return False
            
            # Detect case type
            case_type = self._detect_case_type()
            
            if case_type == "simple_improvisation":
                return self._validate_simple_case_structure()
            elif case_type == "complex":
                return self._validate_complex_case_structure()
            else:
                self.errors.append(f"Unknown case type detected: {case_type}")
                return False
                
        except Exception as e:
            self.errors.append(f"Structure validation failed: {str(e)}")
            return False
    
    def _detect_case_type(self) -> str:
        """Detect case type using file structure analysis"""
        # Check for complex case structure
        backbone_dir = self.case_path / "backbone"
        if backbone_dir.exists() and (backbone_dir / "case_structure.json").exists():
            return "complex"
        
        # Check for simple improvisation structure
        real_life_file = self.case_path / "real_life_case_summary.txt"
        opening_file = self.case_path / "case_opening.txt"
        if real_life_file.exists() and opening_file.exists():
            return "simple_improvisation"
        
        # Unknown structure
        return "unknown"
    
    def _validate_simple_case_structure(self) -> bool:
        """Validate simple improvisation case structure"""
        required_files = [
            "real_life_case_summary.txt",
            "case_opening.txt"
        ]
        
        missing_files = []
        for file_name in required_files:
            file_path = self.case_path / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if missing_files:
            self.errors.append(f"Missing required files for simple improvisation case: {missing_files}")
            return False
        
        # Check for game_state directory (can auto-create if missing)
        game_state_dir = self.case_path / "game_state"
        if not game_state_dir.exists():
            self.warnings.append("game_state directory missing, will be auto-created")
            try:
                game_state_dir.mkdir(parents=True, exist_ok=True)
                self.fixes_applied.append("Created missing game_state directory")
            except Exception as e:
                self.errors.append(f"Failed to create game_state directory: {str(e)}")
                return False
        
        return True
    
    def _validate_complex_case_structure(self) -> bool:
        """Validate complex case structure"""
        required_dirs = ["backbone", "game_state"]
        required_backbone_files = [
            "case_structure.json",
            "character_facts.json", 
            "evidence_chain.json",
            "truth_timeline.json",
            "witness_testimonies.json",
            "trial_structure.json"
        ]
        
        # Check directories
        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = self.case_path / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.errors.append(f"Missing required directories: {missing_dirs}")
            return False
        
        # Check backbone files
        backbone_dir = self.case_path / "backbone"
        missing_backbone_files = []
        for file_name in required_backbone_files:
            file_path = backbone_dir / file_name
            if not file_path.exists():
                missing_backbone_files.append(file_name)
        
        if missing_backbone_files:
            self.errors.append(f"Missing backbone files: {missing_backbone_files}")
            return False
        
        return True
    
    def _validate_file_integrity(self) -> bool:
        """Validate file contents and JSON integrity"""
        try:
            case_type = self._detect_case_type()
            
            if case_type == "simple_improvisation":
                return self._validate_simple_file_integrity()
            elif case_type == "complex":
                return self._validate_complex_file_integrity()
            else:
                return False
                
        except Exception as e:
            self.errors.append(f"File integrity validation failed: {str(e)}")
            return False
    
    def _validate_simple_file_integrity(self) -> bool:
        """Validate simple case file contents"""
        # Check real_life_case_summary.txt
        summary_file = self.case_path / "real_life_case_summary.txt"
        try:
            with open(summary_file, 'r') as f:
                content = f.read().strip()
                if len(content) < 50:
                    self.warnings.append("real_life_case_summary.txt appears very short")
        except Exception as e:
            self.errors.append(f"Cannot read real_life_case_summary.txt: {str(e)}")
            return False
        
        # Check case_opening.txt
        opening_file = self.case_path / "case_opening.txt"
        try:
            with open(opening_file, 'r') as f:
                content = f.read().strip()
                if len(content) < 50:
                    self.warnings.append("case_opening.txt appears very short")
        except Exception as e:
            self.errors.append(f"Cannot read case_opening.txt: {str(e)}")
            return False
        
        return True
    
    def _validate_complex_file_integrity(self) -> bool:
        """Validate complex case JSON file integrity"""
        backbone_dir = self.case_path / "backbone"
        json_files = [
            "case_structure.json",
            "character_facts.json",
            "evidence_chain.json", 
            "truth_timeline.json",
            "witness_testimonies.json",
            "trial_structure.json"
        ]
        
        for file_name in json_files:
            file_path = backbone_dir / file_name
            try:
                with open(file_path, 'r') as f:
                    json.load(f)  # Validate JSON syntax
            except json.JSONDecodeError as e:
                self.errors.append(f"Invalid JSON in {file_name}: {str(e)}")
                return False
            except Exception as e:
                self.errors.append(f"Cannot read {file_name}: {str(e)}")
                return False
        
        return True
    
    def _validate_configuration_consistency(self) -> bool:
        """Validate configuration consistency"""
        try:
            # Check configuration loading
            config = self.config_manager.config
            if not config:
                self.errors.append("Configuration manager failed to load config")
                return False
            
            # Validate case patterns exist
            if "case_types" not in config:
                self.errors.append("Missing case_types in configuration")
                return False
            
            if "case_lengths" not in config:
                self.errors.append("Missing case_lengths in configuration")
                return False
            
            return True
            
        except Exception as e:
            self.errors.append(f"Configuration validation failed: {str(e)}")
            return False
    
    def _validate_game_state_manager(self) -> bool:
        """Validate GameStateManager can initialize properly"""
        try:
            # Attempt to initialize GameStateManager
            manager = GameStateManager(str(self.case_path))
            
            # Run validation
            validation = manager.validate_case_consistency()
            if not validation["valid"]:
                self.errors.extend([f"GameStateManager validation: {issue}" for issue in validation["issues"]])
                return False
            
            # Check basic functionality
            if not hasattr(manager, 'case_name') or not manager.case_name:
                self.errors.append("GameStateManager missing case_name")
                return False
            
            if not hasattr(manager, 'case_length') or manager.case_length < 1:
                self.errors.append("GameStateManager invalid case_length")
                return False
            
            return True
            
        except Exception as e:
            self.errors.append(f"GameStateManager initialization failed: {str(e)}")
            return False
    
    def _validate_virtual_environment(self) -> bool:
        """Validate virtual environment activation"""
        try:
            # Check if we're in a virtual environment
            venv_active = hasattr(sys, 'real_prefix') or (
                hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
            )
            
            if not venv_active:
                self.errors.append("Virtual environment not activated - run 'source venv/bin/activate' first")
                return False
            
            # Check required packages
            try:
                import wonderwords
                self.validation_results.append("wonderwords package available")
            except ImportError:
                self.warnings.append("wonderwords package not found, will use fallback inspiration")
            
            return True
            
        except Exception as e:
            self.errors.append(f"Virtual environment validation failed: {str(e)}")
            return False
    
    def _generate_next_steps(self, all_valid: bool) -> List[str]:
        """Generate actionable next steps based on validation results"""
        if all_valid:
            return [
                "✅ All validations passed - game is ready to start",
                f"Run: python3 scripts/game_state_manager.py {self.case_name} --resume",
                "Follow the forcing function requirements during gameplay"
            ]
        
        next_steps = ["❌ Validation failed - fix these issues before starting:"]
        
        # Prioritize fixes
        if any("Virtual environment not activated" in error for error in self.errors):
            next_steps.append("1. CRITICAL: Activate virtual environment with 'source venv/bin/activate'")
        
        if any("Missing required" in error for error in self.errors):
            next_steps.append("2. CRITICAL: Fix missing files/directories (see errors above)")
        
        if any("GameStateManager" in error for error in self.errors):
            next_steps.append("3. CRITICAL: Fix GameStateManager issues (see errors above)")
        
        if any("JSON" in error for error in self.errors):
            next_steps.append("4. Fix JSON syntax errors in backbone files")
        
        next_steps.append("5. Re-run validation after fixes")
        next_steps.append("6. DO NOT proceed with manual workarounds")
        
        return next_steps
    
    def _print_validation_summary(self, result: Dict[str, Any]) -> None:
        """Print comprehensive validation summary"""
        print("\n" + "="*60)
        print(f"🎮 START GAME VALIDATION REPORT: {self.case_name}")
        print("="*60)
        
        # Overall status
        if result["valid"]:
            print("🟢 OVERALL STATUS: READY TO START")
        else:
            print("🔴 OVERALL STATUS: NOT READY - ISSUES FOUND")
        
        # Validation breakdown
        print("\n📊 VALIDATION BREAKDOWN:")
        for check, status in result["validations"].items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {check.replace('_', ' ').title()}")
        
        # Errors
        if self.errors:
            print(f"\n🔴 ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        # Warnings
        if self.warnings:
            print(f"\n🟡 WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        # Fixes applied
        if self.fixes_applied:
            print(f"\n🔧 AUTOMATIC FIXES APPLIED ({len(self.fixes_applied)}):")
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"  {i}. {fix}")
        
        # Next steps
        print(f"\n📋 NEXT STEPS:")
        for step in result["next_steps"]:
            print(f"  {step}")
        
        print("\n" + "="*60)

def main():
    """Command line interface for start game validation"""
    if len(sys.argv) != 2:
        print("Usage: python3 start_game_validator.py <case_name>")
        sys.exit(1)
    
    case_name = sys.argv[1]
    validator = StartGameValidator(case_name)
    result = validator.run_full_validation()
    
    # Exit with appropriate code
    sys.exit(0 if result["valid"] else 1)

if __name__ == "__main__":
    main()