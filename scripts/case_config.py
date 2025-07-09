#!/usr/bin/env python3
"""
Case Configuration Manager
Provides centralized configuration management for all case creation and game state scripts.
Ensures loose coupling and consistent behavior across the system.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

class CaseConfigManager:
    """Centralized configuration manager for case creation system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with config file path"""
        if config_path is None:
            # Default to config/case_patterns.json relative to this script
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / "config" / "case_patterns.json"
        
        self.config_path = Path(config_path)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def reload_config(self) -> None:
        """Reload configuration from file"""
        self.config = self.load_config()
    
    # Case Length Management
    
    def get_case_lengths(self) -> Dict[str, Dict[str, Any]]:
        """Get all available case length configurations"""
        return self.config.get("case_lengths", {})
    
    def get_case_length_config(self, length: int) -> Dict[str, Any]:
        """Get configuration for specific case length"""
        case_lengths = self.get_case_lengths()
        return case_lengths.get(str(length), {})
    
    def get_gates_for_case_length(self, length: int) -> List[str]:
        """Get gate list for specific case length"""
        config = self.get_case_length_config(length)
        return config.get("gates", [])
    
    def get_trial_trigger_point(self, length: int) -> int:
        """Get trial trigger point for specific case length"""
        config = self.get_case_length_config(length)
        return config.get("trial_trigger_point", 0)
    
    def get_investigation_gate_count(self, length: int) -> int:
        """Get number of investigation gates for case length"""
        config = self.get_case_length_config(length)
        return config.get("investigation_gates", 0)
    
    def detect_case_length_from_gates(self, gates: List[str]) -> int:
        """Detect case length from gate list"""
        gate_count = len(gates)
        
        # Check exact matches first
        for length_str, config in self.get_case_lengths().items():
            if set(gates) == set(config.get("gates", [])):
                return int(length_str)
        
        # Fall back to count-based detection
        if gate_count == 3:
            return 1
        elif gate_count == 4:
            return 2
        elif gate_count == 6:
            return 3
        
        # Apply fallback rules from config
        fallback_rules = self.config.get("validation_rules", {}).get("case_length_detection", {}).get("fallback_rules", [])
        
        # Check for trial-only pattern
        if any("trial" in gate for gate in gates) and not any(self.is_investigation_gate(gate) for gate in gates):
            return 1
        
        # Check for multi-day pattern
        if any("day_1" in gate and "day_2" in gate for gate in gates):
            return 3
        
        # Default to 2-day
        return 2
    
    # Gate Classification
    
    def get_gate_classifications(self) -> Dict[str, List[str]]:
        """Get gate type classifications"""
        return self.config.get("gate_classifications", {})
    
    def is_investigation_gate(self, gate_name: str) -> bool:
        """Check if gate is an investigation gate"""
        investigation_gates = self.get_gate_classifications().get("investigation", [])
        return gate_name in investigation_gates
    
    def is_trial_gate(self, gate_name: str) -> bool:
        """Check if gate is a trial gate"""
        trial_gates = self.get_gate_classifications().get("trial", [])
        return gate_name in trial_gates
    
    def classify_gate(self, gate_name: str) -> str:
        """Classify gate as 'investigation', 'trial', or 'unknown'"""
        if self.is_investigation_gate(gate_name):
            return "investigation"
        elif self.is_trial_gate(gate_name):
            return "trial"
        else:
            return "unknown"
    
    # Inspiration Management
    
    def get_inspiration_categories(self) -> List[str]:
        """Get list of inspiration categories"""
        return self.config.get("inspiration_categories", [])
    
    def get_inspiration_settings(self) -> Dict[str, Any]:
        """Get inspiration pool settings"""
        return self.config.get("validation_rules", {}).get("inspiration_pool", {})
    
    def get_words_per_category(self) -> int:
        """Get number of words per inspiration category"""
        return self.get_inspiration_settings().get("words_per_category", 10)
    
    # File Structure Management
    
    def get_mandatory_files(self) -> Dict[str, List[str]]:
        """Get mandatory file structure"""
        return self.config.get("case_structure_requirements", {}).get("mandatory_files", {})
    
    def get_optional_files(self) -> Dict[str, List[str]]:
        """Get optional file structure"""
        return self.config.get("case_structure_requirements", {}).get("optional_files", {})
    
    def get_required_directories(self) -> List[str]:
        """Get list of required directories"""
        mandatory = self.get_mandatory_files()
        optional = self.get_optional_files()
        return list(set(list(mandatory.keys()) + list(optional.keys())))
    
    def validate_case_structure(self, case_path: Path) -> Dict[str, Any]:
        """Validate case directory structure against requirements"""
        issues = []
        warnings = []
        
        # Check mandatory directories and files
        mandatory_files = self.get_mandatory_files()
        for directory, files in mandatory_files.items():
            dir_path = case_path / directory
            if not dir_path.exists():
                issues.append(f"Missing mandatory directory: {directory}")
                continue
            
            for file in files:
                file_path = dir_path / file
                if not file_path.exists():
                    issues.append(f"Missing mandatory file: {directory}/{file}")
        
        # Check optional directories (warn if missing)
        optional_files = self.get_optional_files()
        for directory, files in optional_files.items():
            dir_path = case_path / directory
            if not dir_path.exists():
                warnings.append(f"Optional directory not found: {directory}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    # Validation Rules
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get all validation rules"""
        return self.config.get("validation_rules", {})
    
    def validate_gate_structure(self, gates: List[str]) -> Dict[str, Any]:
        """Validate gate structure against rules"""
        rules = self.get_validation_rules().get("gate_structure", {})
        issues = []
        
        # Check gate count limits
        max_gates = rules.get("max_gates_per_case", 10)
        min_gates = rules.get("min_gates_per_case", 3)
        
        if len(gates) > max_gates:
            issues.append(f"Too many gates: {len(gates)} > {max_gates}")
        if len(gates) < min_gates:
            issues.append(f"Too few gates: {len(gates)} < {min_gates}")
        
        # Check required gate types
        required_types = rules.get("required_gate_types", [])
        found_types = set()
        
        for gate in gates:
            gate_type = self.classify_gate(gate)
            if gate_type != "unknown":
                found_types.add(gate_type)
        
        for required_type in required_types:
            if required_type not in found_types:
                issues.append(f"Missing required gate type: {required_type}")
        
        # Check gate name pattern (if specified)
        import re
        name_pattern = rules.get("gate_name_pattern")
        if name_pattern:
            pattern = re.compile(name_pattern)
            for gate in gates:
                if not pattern.match(gate):
                    issues.append(f"Gate name '{gate}' doesn't match pattern: {name_pattern}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    # Default Settings
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default settings for case creation and game state"""
        return self.config.get("default_settings", {})
    
    def get_case_creation_settings(self) -> Dict[str, Any]:
        """Get case creation default settings"""
        return self.get_default_settings().get("case_creation", {})
    
    def get_game_state_settings(self) -> Dict[str, Any]:
        """Get game state default settings"""
        return self.get_default_settings().get("game_state", {})
    
    # Utility Methods
    
    def get_case_length_summary(self) -> Dict[str, str]:
        """Get summary of all case lengths"""
        summary = {}
        for length_str, config in self.get_case_lengths().items():
            name = config.get("name", f"{length_str}-day case")
            description = config.get("description", "")
            gate_count = len(config.get("gates", []))
            time_estimate = config.get("estimated_time", "unknown")
            
            summary[length_str] = f"{name}: {gate_count} gates, {time_estimate} ({description})"
        
        return summary
    
    def create_case_length_config(self, length: int, name: str, gates: List[str], 
                                 investigation_gates: int, description: str = "", 
                                 estimated_time: str = "unknown") -> Dict[str, Any]:
        """Create a new case length configuration"""
        return {
            "name": name,
            "description": description,
            "gates": gates,
            "investigation_gates": investigation_gates,
            "trial_trigger_point": investigation_gates,
            "estimated_time": estimated_time
        }
    
    def add_case_length(self, length: int, config: Dict[str, Any]) -> None:
        """Add a new case length configuration"""
        self.config["case_lengths"][str(length)] = config
    
    def add_inspiration_category(self, category: str) -> None:
        """Add a new inspiration category"""
        categories = self.config.get("inspiration_categories", [])
        if category not in categories:
            categories.append(category)
            self.config["inspiration_categories"] = categories
    
    def save_config(self) -> None:
        """Save current configuration back to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

# Global instance for easy access
_config_manager = None

def get_config_manager(config_path: Optional[str] = None) -> CaseConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = CaseConfigManager(config_path)
    return _config_manager

# Convenience functions
def get_case_lengths() -> Dict[str, Dict[str, Any]]:
    """Convenience function to get case lengths"""
    return get_config_manager().get_case_lengths()

def get_gates_for_case_length(length: int) -> List[str]:
    """Convenience function to get gates for case length"""
    return get_config_manager().get_gates_for_case_length(length)

def get_trial_trigger_point(length: int) -> int:
    """Convenience function to get trial trigger point"""
    return get_config_manager().get_trial_trigger_point(length)

def detect_case_length_from_gates(gates: List[str]) -> int:
    """Convenience function to detect case length from gates"""
    return get_config_manager().detect_case_length_from_gates(gates)

def is_investigation_gate(gate_name: str) -> bool:
    """Convenience function to check if gate is investigation"""
    return get_config_manager().is_investigation_gate(gate_name)

def is_trial_gate(gate_name: str) -> bool:
    """Convenience function to check if gate is trial"""
    return get_config_manager().is_trial_gate(gate_name)

def get_inspiration_categories() -> List[str]:
    """Convenience function to get inspiration categories"""
    return get_config_manager().get_inspiration_categories()

def main():
    """Command line interface for configuration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage case configuration')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--show-lengths', action='store_true', help='Show all case lengths')
    parser.add_argument('--show-gates', type=int, metavar='LENGTH', help='Show gates for case length')
    parser.add_argument('--show-categories', action='store_true', help='Show inspiration categories')
    parser.add_argument('--validate-structure', help='Validate case structure at path')
    parser.add_argument('--detect-length', nargs='+', help='Detect case length from gate names')
    
    args = parser.parse_args()
    
    try:
        config_manager = get_config_manager(args.config)
        
        if args.show_lengths:
            print("=== Case Length Configurations ===")
            summary = config_manager.get_case_length_summary()
            for length, info in summary.items():
                print(f"{length}-day: {info}")
        
        if args.show_gates:
            gates = config_manager.get_gates_for_case_length(args.show_gates)
            trigger_point = config_manager.get_trial_trigger_point(args.show_gates)
            print(f"=== {args.show_gates}-Day Case Gates ===")
            for i, gate in enumerate(gates):
                gate_type = config_manager.classify_gate(gate)
                marker = "🚨" if i == trigger_point else "📍"
                print(f"{marker} {gate} ({gate_type})")
        
        if args.show_categories:
            categories = config_manager.get_inspiration_categories()
            print("=== Inspiration Categories ===")
            for category in categories:
                print(f"- {category}")
        
        if args.validate_structure:
            validation = config_manager.validate_case_structure(Path(args.validate_structure))
            print(f"=== Structure Validation: {args.validate_structure} ===")
            if validation["valid"]:
                print("✅ Structure is valid")
            else:
                print("❌ Structure has issues:")
                for issue in validation["issues"]:
                    print(f"  - {issue}")
            
            if validation["warnings"]:
                print("⚠️  Warnings:")
                for warning in validation["warnings"]:
                    print(f"  - {warning}")
        
        if args.detect_length:
            detected_length = config_manager.detect_case_length_from_gates(args.detect_length)
            print(f"=== Length Detection ===")
            print(f"Gates: {args.detect_length}")
            print(f"Detected length: {detected_length} days")
            
            # Show expected structure
            expected_gates = config_manager.get_gates_for_case_length(detected_length)
            print(f"Expected gates for {detected_length}-day case: {expected_gates}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())