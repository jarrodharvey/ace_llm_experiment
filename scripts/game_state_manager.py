#!/usr/bin/env python3
"""
Game State Manager
Provides dynamic state management for Ace Attorney cases with automatic structure detection.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from case_config import get_config_manager

class GameStateManager:
    def __init__(self, case_path: str):
        self.case_path = Path(case_path)
        self.case_name = self.case_path.name
        
        # Load shared configuration
        self.config_manager = get_config_manager()
        
        # Load case structure dynamically
        self.case_structure = self.load_case_structure()
        self.current_state = self.load_current_state()
        self.trial_state = self.load_trial_state()
        
        # Auto-detect case characteristics
        self.case_length = self.detect_case_length()
        self.gates = list(self.current_state.get("investigation_gates", {}).keys())
        self.total_gates = len(self.gates)
        
        # Load inspiration pool for entropy prevention
        self.inspiration_pool = self.load_inspiration_pool()
        
    def load_case_structure(self) -> Dict[str, Any]:
        """Load the basic case structure from backbone files"""
        structure_file = self.case_path / "backbone" / "case_structure.json"
        if not structure_file.exists():
            raise FileNotFoundError(f"Case structure not found: {structure_file}")
        
        with open(structure_file, 'r') as f:
            return json.load(f)
    
    def load_current_state(self) -> Dict[str, Any]:
        """Load current investigation progress"""
        progress_file = self.case_path / "game_state" / "investigation_progress.json"
        if not progress_file.exists():
            raise FileNotFoundError(f"Investigation progress not found: {progress_file}")
        
        with open(progress_file, 'r') as f:
            return json.load(f)
    
    def load_trial_state(self) -> Dict[str, Any]:
        """Load current trial progress"""
        trial_file = self.case_path / "game_state" / "trial_progress.json"
        if not trial_file.exists():
            raise FileNotFoundError(f"Trial progress not found: {trial_file}")
        
        with open(trial_file, 'r') as f:
            return json.load(f)
    
    def detect_case_length(self) -> int:
        """Auto-detect case length from structure using shared configuration"""
        # Check if case_length is explicitly stored
        if "case_length" in self.current_state:
            return self.current_state["case_length"]
        
        # Use configuration manager to detect from gates
        gates = list(self.current_state.get("investigation_gates", {}).keys())
        return self.config_manager.detect_case_length_from_gates(gates)
    
    # Removed load_gate_patterns - now using shared configuration
    
    def load_inspiration_pool(self) -> Dict[str, Any]:
        """Load inspiration pool for entropy prevention"""
        inspiration_file = self.case_path / "inspiration_pool.json"
        if not inspiration_file.exists():
            return {}
        
        with open(inspiration_file, 'r') as f:
            return json.load(f)
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get comprehensive current status"""
        return {
            "case_name": self.case_name,
            "case_length": self.case_length,
            "total_gates": self.total_gates,
            "current_phase": self.current_state.get("current_phase", "unknown"),
            "gates_completed": self.get_completed_gates(),
            "gates_pending": self.get_pending_gates(),
            "progress_percentage": self.get_progress_percentage(),
            "trial_ready": self.is_trial_ready(),
            "current_location": self.current_state.get("current_location", "unknown"),
            "evidence_collected": len(self.current_state.get("evidence_collected", [])),
            "witnesses_interviewed": len(self.current_state.get("witnesses_interviewed", []))
        }
    
    def get_completed_gates(self) -> List[str]:
        """Get list of completed gates"""
        gates = self.current_state.get("investigation_gates", {})
        return [gate for gate, status in gates.items() if status == "completed"]
    
    def get_pending_gates(self) -> List[str]:
        """Get list of pending gates"""
        gates = self.current_state.get("investigation_gates", {})
        return [gate for gate, status in gates.items() if status == "pending"]
    
    def get_in_progress_gates(self) -> List[str]:
        """Get list of in-progress gates"""
        gates = self.current_state.get("investigation_gates", {})
        return [gate for gate, status in gates.items() if status == "in_progress"]
    
    def get_progress_percentage(self) -> float:
        """Calculate overall progress percentage"""
        if self.total_gates == 0:
            return 0.0
        
        completed = len(self.get_completed_gates())
        return (completed / self.total_gates) * 100
    
    def complete_gate(self, gate_name: str) -> bool:
        """Complete a specific gate with validation"""
        # Validate gate exists
        if gate_name not in self.gates:
            raise ValueError(f"Gate '{gate_name}' not found in case structure. Available gates: {self.gates}")
        
        # Check current status
        current_status = self.current_state["investigation_gates"].get(gate_name)
        if current_status == "completed":
            return False  # Already completed
        
        # Update state
        self.current_state["investigation_gates"][gate_name] = "completed"
        
        # Save changes
        self.save_current_state()
        
        return True
    
    def start_gate(self, gate_name: str) -> bool:
        """Mark a gate as in progress"""
        if gate_name not in self.gates:
            raise ValueError(f"Gate '{gate_name}' not found in case structure. Available gates: {self.gates}")
        
        current_status = self.current_state["investigation_gates"].get(gate_name)
        if current_status in ["completed", "in_progress"]:
            return False  # Already started or completed
        
        # Update state
        self.current_state["investigation_gates"][gate_name] = "in_progress"
        
        # Save changes
        self.save_current_state()
        
        return True
    
    def is_trial_ready(self) -> bool:
        """Determine if trial should be triggered based on case pattern"""
        completed_count = len(self.get_completed_gates())
        trigger_point = self.config_manager.get_trial_trigger_point(self.case_length)
        
        return completed_count >= trigger_point
    
    def get_next_gate(self) -> Optional[str]:
        """Get the next gate that should be worked on"""
        # Check for in-progress gates first
        in_progress = self.get_in_progress_gates()
        if in_progress:
            return in_progress[0]
        
        # Otherwise, return first pending gate
        pending = self.get_pending_gates()
        if pending:
            return pending[0]
        
        return None
    
    def save_current_state(self) -> None:
        """Save current state back to file"""
        progress_file = self.case_path / "game_state" / "investigation_progress.json"
        with open(progress_file, 'w') as f:
            json.dump(self.current_state, f, indent=2)
    
    def add_evidence(self, evidence_name: str, description: str) -> bool:
        """Add evidence to collection"""
        evidence_list = self.current_state.get("evidence_collected", [])
        
        # Check if evidence already exists
        for evidence in evidence_list:
            if isinstance(evidence, dict) and evidence.get("name") == evidence_name:
                return False  # Already exists
            elif isinstance(evidence, str) and evidence == evidence_name:
                return False  # Already exists
        
        # Add new evidence
        evidence_entry = {
            "name": evidence_name,
            "description": description,
            "discovered_at": f"Gate: {self.get_next_gate() or 'unknown'}"
        }
        evidence_list.append(evidence_entry)
        
        self.current_state["evidence_collected"] = evidence_list
        self.save_current_state()
        
        return True
    
    def update_character_trust(self, character_name: str, change: int) -> int:
        """Update character trust level"""
        trust_levels = self.current_state.get("character_trust_levels", {})
        current_trust = trust_levels.get(character_name, 5)  # Default to 5
        
        new_trust = max(0, min(10, current_trust + change))  # Clamp to 0-10
        trust_levels[character_name] = new_trust
        
        self.current_state["character_trust_levels"] = trust_levels
        self.save_current_state()
        
        return new_trust
    
    def set_location(self, location_name: str) -> bool:
        """Update current location"""
        available_locations = self.current_state.get("available_locations", [])
        
        if location_name not in available_locations:
            return False  # Invalid location
        
        self.current_state["current_location"] = location_name
        self.save_current_state()
        
        return True
    
    def add_investigation_note(self, note: str) -> None:
        """Add investigation note"""
        notes = self.current_state.get("investigation_notes", [])
        notes.append({
            "note": note,
            "gate": self.get_next_gate() or "unknown"
        })
        
        self.current_state["investigation_notes"] = notes
        self.save_current_state()
    
    # Phase 2: Advanced Features
    
    def validate_case_consistency(self) -> Dict[str, Any]:
        """Validate current state against case structure and expected patterns"""
        issues = []
        warnings = []
        
        # Check gate structure consistency
        expected_gates = self.config_manager.get_gates_for_case_length(self.case_length)
        actual_gates = self.gates
        
        if expected_gates and set(actual_gates) != set(expected_gates):
            issues.append(f"Gate structure mismatch. Expected: {expected_gates}, Got: {actual_gates}")
        
        # Check trial trigger logic
        completed_count = len(self.get_completed_gates())
        trigger_point = self.config_manager.get_trial_trigger_point(self.case_length)
        
        if completed_count > trigger_point and not self.is_trial_ready():
            issues.append(f"Trial should be ready at {trigger_point} gates, but isn't at {completed_count} gates")
        
        # Check evidence count vs. progress
        evidence_count = len(self.current_state.get("evidence_collected", []))
        if completed_count > 0 and evidence_count == 0:
            warnings.append("Gates completed but no evidence collected")
        
        # Check character trust levels
        trust_levels = self.current_state.get("character_trust_levels", {})
        if any(trust < 0 or trust > 10 for trust in trust_levels.values()):
            issues.append("Character trust levels outside valid range (0-10)")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def get_evidence_by_gate(self, gate_name: str) -> List[Dict[str, Any]]:
        """Get all evidence collected during a specific gate"""
        evidence_list = self.current_state.get("evidence_collected", [])
        return [e for e in evidence_list if e.get("discovered_at") == f"Gate: {gate_name}"]
    
    def get_evidence_summary(self) -> Dict[str, Any]:
        """Get comprehensive evidence summary"""
        evidence_list = self.current_state.get("evidence_collected", [])
        
        summary = {
            "total_evidence": len(evidence_list),
            "by_gate": {},
            "recent_evidence": evidence_list[-3:] if len(evidence_list) >= 3 else evidence_list
        }
        
        # Group by gate
        for evidence in evidence_list:
            gate = evidence.get("discovered_at", "unknown")
            if gate not in summary["by_gate"]:
                summary["by_gate"][gate] = []
            summary["by_gate"][gate].append(evidence)
        
        return summary
    
    def get_character_relationships(self) -> Dict[str, Any]:
        """Get character relationship analysis"""
        trust_levels = self.current_state.get("character_trust_levels", {})
        
        relationships = {
            "hostile": [],      # trust <= 3
            "neutral": [],      # trust 4-6
            "friendly": [],     # trust 7-10
            "suspicious": []    # trust changed significantly
        }
        
        for character, trust in trust_levels.items():
            if trust <= 3:
                relationships["hostile"].append(character)
            elif trust <= 6:
                relationships["neutral"].append(character)
            else:
                relationships["friendly"].append(character)
        
        return relationships
    
    def predict_trial_readiness(self) -> Dict[str, Any]:
        """Predict when trial will be ready and what's needed"""
        completed_count = len(self.get_completed_gates())
        trigger_point = self.config_manager.get_trial_trigger_point(self.case_length)
        
        if completed_count >= trigger_point:
            return {
                "ready": True,
                "message": "Trial ready now!",
                "gates_remaining": 0
            }
        else:
            gates_needed = trigger_point - completed_count
            next_gates = self.get_pending_gates()[:gates_needed]
            return {
                "ready": False,
                "message": f"Trial will be ready after {gates_needed} more gate(s)",
                "gates_remaining": gates_needed,
                "next_gates": next_gates
            }
    
    def get_investigation_summary(self) -> Dict[str, Any]:
        """Get comprehensive investigation summary"""
        return {
            "progress": self.get_progress_percentage(),
            "current_phase": self.current_state.get("current_phase", "unknown"),
            "gates": {
                "completed": self.get_completed_gates(),
                "in_progress": self.get_in_progress_gates(),
                "pending": self.get_pending_gates()
            },
            "evidence": self.get_evidence_summary(),
            "characters": self.get_character_relationships(),
            "trial_prediction": self.predict_trial_readiness(),
            "location": self.current_state.get("current_location", "unknown"),
            "notes_count": len(self.current_state.get("investigation_notes", []))
        }
    
    def start_trial(self) -> bool:
        """Initiate trial phase with validation"""
        if not self.is_trial_ready():
            return False
        
        # Update trial state
        self.trial_state["trial_status"] = "in_progress"
        self.trial_state["trial_day"] = 1
        
        # Update investigation state
        self.current_state["current_phase"] = "trial"
        
        # Save both states
        self.save_current_state()
        self.save_trial_state()
        
        return True
    
    def save_trial_state(self) -> None:
        """Save trial state back to file"""
        trial_file = self.case_path / "game_state" / "trial_progress.json"
        with open(trial_file, 'w') as f:
            json.dump(self.trial_state, f, indent=2)
    
    def interview_witness(self, witness_name: str) -> bool:
        """Record witness interview"""
        interviewed = self.current_state.get("witnesses_interviewed", [])
        
        if witness_name not in interviewed:
            interviewed.append(witness_name)
            self.current_state["witnesses_interviewed"] = interviewed
            self.save_current_state()
            return True
        
        return False  # Already interviewed
    
    def update_location_availability(self, location: str, available: bool = True) -> None:
        """Update which locations are available"""
        locations = self.current_state.get("available_locations", [])
        
        if available and location not in locations:
            locations.append(location)
        elif not available and location in locations:
            locations.remove(location)
        
        self.current_state["available_locations"] = locations
        self.save_current_state()
    
    def get_available_actions(self) -> List[str]:
        """Get context-appropriate available actions"""
        actions = []
        
        # Always available
        actions.append("Check current status")
        
        # Gate-specific actions
        next_gate = self.get_next_gate()
        if next_gate:
            actions.append(f"Work on {next_gate}")
        
        # Location-based actions
        current_location = self.current_state.get("current_location", "")
        available_locations = self.current_state.get("available_locations", [])
        
        for location in available_locations:
            if location != current_location:
                actions.append(f"Go to {location}")
        
        # Evidence-based actions
        evidence_count = len(self.current_state.get("evidence_collected", []))
        if evidence_count > 0:
            actions.append("Review evidence")
        
        # Character-based actions
        trust_levels = self.current_state.get("character_trust_levels", {})
        for character, trust in trust_levels.items():
            if trust > 3:  # Only suggest friendly/neutral characters
                actions.append(f"Talk to {character}")
        
        # Trial actions
        if self.is_trial_ready():
            actions.append("Start trial")
        
        return actions
    
    # Phase 3: Resume/Restore Functionality
    
    def create_save_point(self, save_name: str) -> bool:
        """Create a save point for the current state"""
        saves_dir = self.case_path / "saves"
        saves_dir.mkdir(exist_ok=True)
        
        save_data = {
            "save_name": save_name,
            "timestamp": self.get_current_timestamp(),
            "investigation_state": self.current_state.copy(),
            "trial_state": self.trial_state.copy(),
            "case_structure": self.case_structure.copy(),
            "case_length": self.case_length,
            "gates": self.gates.copy()
        }
        
        save_file = saves_dir / f"{save_name}.json"
        with open(save_file, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        return True
    
    def list_save_points(self) -> List[Dict[str, Any]]:
        """List all available save points"""
        saves_dir = self.case_path / "saves"
        if not saves_dir.exists():
            return []
        
        saves = []
        for save_file in saves_dir.glob("*.json"):
            try:
                with open(save_file, 'r') as f:
                    save_data = json.load(f)
                saves.append({
                    "name": save_data.get("save_name", save_file.stem),
                    "timestamp": save_data.get("timestamp", "unknown"),
                    "progress": self.calculate_progress_from_state(save_data.get("investigation_state", {})),
                    "phase": save_data.get("investigation_state", {}).get("current_phase", "unknown"),
                    "file": save_file
                })
            except Exception:
                continue  # Skip corrupted saves
        
        return sorted(saves, key=lambda x: x["timestamp"], reverse=True)
    
    def restore_save_point(self, save_name: str) -> bool:
        """Restore state from a save point"""
        saves_dir = self.case_path / "saves"
        save_file = saves_dir / f"{save_name}.json"
        
        if not save_file.exists():
            return False
        
        try:
            with open(save_file, 'r') as f:
                save_data = json.load(f)
            
            # Restore states
            self.current_state = save_data["investigation_state"]
            self.trial_state = save_data["trial_state"]
            self.case_structure = save_data["case_structure"]
            self.case_length = save_data["case_length"]
            self.gates = save_data["gates"]
            
            # Save restored states to main files
            self.save_current_state()
            self.save_trial_state()
            
            return True
            
        except Exception:
            return False
    
    def get_resume_context(self) -> Dict[str, Any]:
        """Get context needed to resume gameplay"""
        return {
            "case_info": {
                "name": self.case_name,
                "length": self.case_length,
                "current_phase": self.current_state.get("current_phase", "unknown"),
                "progress": self.get_progress_percentage()
            },
            "current_situation": {
                "location": self.current_state.get("current_location", "unknown"),
                "day": self.current_state.get("day", 1),
                "time_until_trial": self.current_state.get("time_until_trial", "unknown")
            },
            "recent_progress": {
                "last_completed_gate": self.get_last_completed_gate(),
                "current_gate": self.get_next_gate(),
                "recent_evidence": self.get_recent_evidence(3),
                "recent_notes": self.get_recent_notes(3)
            },
            "current_status": {
                "trial_ready": self.is_trial_ready(),
                "available_actions": self.get_available_actions()[:5],  # Top 5 actions
                "key_characters": self.get_key_character_status()
            }
        }
    
    def get_last_completed_gate(self) -> Optional[str]:
        """Get the most recently completed gate"""
        completed = self.get_completed_gates()
        if completed:
            # Return the last one in the original gate order
            for gate in self.gates:
                if gate in completed:
                    last_gate = gate
            return last_gate
        return None
    
    def get_recent_evidence(self, count: int) -> List[Dict[str, Any]]:
        """Get most recent evidence"""
        evidence = self.current_state.get("evidence_collected", [])
        return evidence[-count:] if evidence else []
    
    def get_recent_notes(self, count: int) -> List[Dict[str, Any]]:
        """Get most recent investigation notes"""
        notes = self.current_state.get("investigation_notes", [])
        return notes[-count:] if notes else []
    
    def get_key_character_status(self) -> Dict[str, Any]:
        """Get status of key characters"""
        trust_levels = self.current_state.get("character_trust_levels", {})
        interviewed = self.current_state.get("witnesses_interviewed", [])
        
        key_chars = {}
        for char, trust in trust_levels.items():
            status = "hostile" if trust <= 3 else "neutral" if trust <= 6 else "friendly"
            key_chars[char] = {
                "trust": trust,
                "status": status,
                "interviewed": char in interviewed
            }
        
        return key_chars
    
    def generate_resume_summary(self) -> str:
        """Generate a natural language summary for resuming gameplay"""
        context = self.get_resume_context()
        
        # Build summary
        summary = f"**{context['case_info']['name']}** ({context['case_info']['length']}-day case)\n\n"
        
        # Progress
        progress = context['case_info']['progress']
        phase = context['case_info']['current_phase']
        summary += f"**Current Status:** {progress:.1f}% complete, {phase} phase\n"
        
        # Location and timing
        location = context['current_situation']['location']
        day = context['current_situation']['day']
        time_left = context['current_situation']['time_until_trial']
        summary += f"**Location:** {location.replace('_', ' ').title()}\n"
        summary += f"**Day {day}** - {time_left} until trial\n\n"
        
        # Recent progress
        last_gate = context['recent_progress']['last_completed_gate']
        current_gate = context['recent_progress']['current_gate']
        if last_gate:
            summary += f"**Last Completed:** {last_gate.replace('_', ' ').title()}\n"
        if current_gate:
            summary += f"**Current Focus:** {current_gate.replace('_', ' ').title()}\n\n"
        
        # Recent evidence
        recent_evidence = context['recent_progress']['recent_evidence']
        if recent_evidence:
            summary += "**Recent Evidence:**\n"
            for evidence in recent_evidence[-2:]:  # Show last 2
                summary += f"  - {evidence['name']}: {evidence['description']}\n"
            summary += "\n"
        
        # Trial status
        if context['current_status']['trial_ready']:
            summary += "**🚨 TRIAL READY!** You have enough evidence to proceed to trial.\n\n"
        
        # Available actions
        actions = context['current_status']['available_actions']
        if actions:
            summary += "**Available Actions:**\n"
            for action in actions[:3]:  # Show top 3
                summary += f"  - {action}\n"
        
        return summary
    
    def calculate_progress_from_state(self, state: Dict[str, Any]) -> float:
        """Calculate progress percentage from a state dict"""
        gates = state.get("investigation_gates", {})
        if not gates:
            return 0.0
        
        completed = sum(1 for status in gates.values() if status == "completed")
        return (completed / len(gates)) * 100
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp for saves"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def backup_current_state(self) -> bool:
        """Create automatic backup of current state"""
        timestamp = self.get_current_timestamp().replace(':', '-').replace('.', '-')
        backup_name = f"auto_backup_{timestamp}"
        return self.create_save_point(backup_name)
    
    def cleanup_old_saves(self, keep_count: int = 10) -> int:
        """Clean up old save files, keeping only the most recent"""
        saves = self.list_save_points()
        if len(saves) <= keep_count:
            return 0
        
        deleted = 0
        for save in saves[keep_count:]:  # Keep first keep_count, delete rest
            try:
                save["file"].unlink()
                deleted += 1
            except Exception:
                continue
        
        return deleted
    
    # Inspiration Pool Integration for Entropy Prevention
    
    def get_inspiration(self, category: str) -> Dict[str, Any]:
        """Get random inspiration from specified category"""
        import random
        
        if category not in self.inspiration_pool:
            return {
                "error": f"Category '{category}' not found in inspiration pool",
                "available_categories": list(self.inspiration_pool.keys())
            }
        
        words = self.inspiration_pool[category]
        if not words:
            return {
                "error": f"Category '{category}' is empty",
                "available_categories": list(self.inspiration_pool.keys())
            }
        
        random_word = random.choice(words)
        return {
            "category": category,
            "word": random_word,
            "instruction": f"Use A-to-C process: Current situation (A) + '{random_word}' (B) → Creative solution (C)"
        }
    
    def get_random_inspiration(self) -> Dict[str, Any]:
        """Get random inspiration from random category"""
        import random
        
        if not self.inspiration_pool:
            return {"error": "No inspiration pool available"}
        
        categories = list(self.inspiration_pool.keys())
        random_category = random.choice(categories)
        return self.get_inspiration(random_category)
    
    def get_contextual_inspiration(self) -> Dict[str, Any]:
        """Get inspiration based on current game context"""
        # Analyze current situation for best inspiration category
        current_gate = self.get_next_gate()
        current_location = self.current_state.get("current_location", "")
        
        # Choose category based on context (using config categories)
        available_categories = self.config_manager.get_inspiration_categories()
        
        if current_gate and "character" in current_gate.lower() and "character_motivations" in available_categories:
            category = "character_motivations"
        elif current_gate and "evidence" in current_gate.lower() and "evidence_obstacles" in available_categories:
            category = "evidence_obstacles"
        elif current_location and "trial" in current_location.lower() and "witness_behaviors" in available_categories:
            category = "witness_behaviors"
        else:
            # Default to relationship dynamics for general interactions
            category = "relationship_dynamics" if "relationship_dynamics" in available_categories else available_categories[0]
        
        inspiration = self.get_inspiration(category)
        if "error" in inspiration:
            # Fallback to random if context category not available
            return self.get_random_inspiration()
        
        inspiration["context"] = f"Selected {category} based on current situation"
        return inspiration
    
    def log_inspiration_usage(self, inspiration: Dict[str, Any], usage_context: str) -> None:
        """Log inspiration usage for tracking"""
        if "word" not in inspiration:
            return
        
        notes = self.current_state.get("inspiration_log", [])
        notes.append({
            "word": inspiration["word"],
            "category": inspiration["category"],
            "usage_context": usage_context,
            "gate": self.get_next_gate() or "unknown",
            "location": self.current_state.get("current_location", "unknown")
        })
        
        self.current_state["inspiration_log"] = notes
        self.save_current_state()
    
    def get_inspiration_history(self) -> List[Dict[str, Any]]:
        """Get history of inspiration usage"""
        return self.current_state.get("inspiration_log", [])
    
    def must_use_inspiration(self, context: str) -> Dict[str, Any]:
        """FORCING FUNCTION: Must use inspiration for off-script responses"""
        inspiration = self.get_contextual_inspiration()
        if "error" not in inspiration:
            self.log_inspiration_usage(inspiration, context)
        return inspiration

def main():
    """Command line interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage game state for Ace Attorney cases')
    parser.add_argument('case_path', help='Path to case directory')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--complete-gate', help='Complete specified gate')
    parser.add_argument('--start-gate', help='Start specified gate')
    parser.add_argument('--add-evidence', nargs=2, metavar=('NAME', 'DESCRIPTION'), help='Add evidence')
    parser.add_argument('--summary', action='store_true', help='Show detailed investigation summary')
    parser.add_argument('--validate', action='store_true', help='Validate case consistency')
    parser.add_argument('--actions', action='store_true', help='Show available actions')
    parser.add_argument('--start-trial', action='store_true', help='Start trial phase')
    parser.add_argument('--interview', help='Record witness interview')
    parser.add_argument('--trust', nargs=2, metavar=('CHARACTER', 'CHANGE'), help='Update character trust')
    parser.add_argument('--location', help='Update current location')
    parser.add_argument('--save', help='Create save point with given name')
    parser.add_argument('--restore', help='Restore from save point')
    parser.add_argument('--list-saves', action='store_true', help='List all save points')
    parser.add_argument('--resume', action='store_true', help='Show resume context')
    parser.add_argument('--backup', action='store_true', help='Create automatic backup')
    parser.add_argument('--cleanup', type=int, metavar='COUNT', help='Clean up old saves (keep COUNT most recent)')
    parser.add_argument('--inspire', help='Get inspiration from specific category')
    parser.add_argument('--inspire-random', action='store_true', help='Get random inspiration')
    parser.add_argument('--inspire-contextual', action='store_true', help='Get contextual inspiration based on current situation')
    parser.add_argument('--must-inspire', help='FORCING FUNCTION: Must use inspiration for off-script response')
    parser.add_argument('--inspiration-history', action='store_true', help='Show inspiration usage history')
    
    args = parser.parse_args()
    
    try:
        manager = GameStateManager(args.case_path)
        
        if args.status:
            status = manager.get_current_status()
            print(f"\n=== {status['case_name']} Status ===")
            print(f"Case Length: {status['case_length']} days")
            print(f"Progress: {status['progress_percentage']:.1f}% ({len(status['gates_completed'])}/{status['total_gates']} gates)")
            print(f"Current Phase: {status['current_phase']}")
            print(f"Trial Ready: {status['trial_ready']}")
            print(f"Current Location: {status['current_location']}")
            print(f"Evidence Collected: {status['evidence_collected']}")
            print(f"Witnesses Interviewed: {status['witnesses_interviewed']}")
            
            if status['gates_completed']:
                print(f"\nCompleted Gates: {', '.join(status['gates_completed'])}")
            if status['gates_pending']:
                print(f"Pending Gates: {', '.join(status['gates_pending'])}")
            
            next_gate = manager.get_next_gate()
            if next_gate:
                print(f"\nNext Gate: {next_gate}")
        
        if args.complete_gate:
            if manager.complete_gate(args.complete_gate):
                print(f"✅ Completed gate: {args.complete_gate}")
            else:
                print(f"❌ Gate already completed: {args.complete_gate}")
        
        if args.start_gate:
            if manager.start_gate(args.start_gate):
                print(f"🎯 Started gate: {args.start_gate}")
            else:
                print(f"❌ Gate already started or completed: {args.start_gate}")
        
        if args.add_evidence:
            name, description = args.add_evidence
            if manager.add_evidence(name, description):
                print(f"🔍 Added evidence: {name}")
            else:
                print(f"❌ Evidence already exists: {name}")
        
        if args.summary:
            summary = manager.get_investigation_summary()
            print(f"\n=== {manager.case_name} Investigation Summary ===")
            print(f"Progress: {summary['progress']:.1f}%")
            print(f"Current Phase: {summary['current_phase']}")
            print(f"Location: {summary['location']}")
            print(f"Evidence: {summary['evidence']['total_evidence']} pieces")
            print(f"Notes: {summary['notes_count']}")
            
            print(f"\nGates:")
            if summary['gates']['completed']:
                print(f"  ✅ Completed: {', '.join(summary['gates']['completed'])}")
            if summary['gates']['in_progress']:
                print(f"  🎯 In Progress: {', '.join(summary['gates']['in_progress'])}")
            if summary['gates']['pending']:
                print(f"  ⏳ Pending: {', '.join(summary['gates']['pending'])}")
            
            print(f"\nCharacter Relationships:")
            chars = summary['characters']
            if chars['hostile']:
                print(f"  😠 Hostile: {', '.join(chars['hostile'])}")
            if chars['neutral']:
                print(f"  😐 Neutral: {', '.join(chars['neutral'])}")
            if chars['friendly']:
                print(f"  😊 Friendly: {', '.join(chars['friendly'])}")
            
            trial_pred = summary['trial_prediction']
            print(f"\nTrial Status: {trial_pred['message']}")
        
        if args.validate:
            validation = manager.validate_case_consistency()
            print(f"\n=== Case Validation ===")
            if validation['valid']:
                print("✅ Case structure is valid")
            else:
                print("❌ Case structure has issues:")
                for issue in validation['issues']:
                    print(f"  - {issue}")
            
            if validation['warnings']:
                print("⚠️  Warnings:")
                for warning in validation['warnings']:
                    print(f"  - {warning}")
        
        if args.actions:
            actions = manager.get_available_actions()
            print(f"\n=== Available Actions ===")
            for i, action in enumerate(actions, 1):
                print(f"{i}. {action}")
        
        if args.start_trial:
            if manager.start_trial():
                print("⚖️  Trial started!")
            else:
                print("❌ Trial not ready yet. Complete more investigation gates first.")
        
        if args.interview:
            if manager.interview_witness(args.interview):
                print(f"🎤 Interviewed witness: {args.interview}")
            else:
                print(f"❌ Already interviewed: {args.interview}")
        
        if args.trust:
            character, change_str = args.trust
            try:
                change = int(change_str)
                new_trust = manager.update_character_trust(character, change)
                print(f"👥 Updated {character} trust: {new_trust}")
            except ValueError:
                print(f"❌ Invalid trust change: {change_str}")
        
        if args.location:
            if manager.set_location(args.location):
                print(f"📍 Moved to: {args.location}")
            else:
                print(f"❌ Cannot access location: {args.location}")
        
        if args.save:
            if manager.create_save_point(args.save):
                print(f"💾 Created save point: {args.save}")
            else:
                print(f"❌ Failed to create save point: {args.save}")
        
        if args.restore:
            if manager.restore_save_point(args.restore):
                print(f"🔄 Restored from save point: {args.restore}")
            else:
                print(f"❌ Failed to restore save point: {args.restore}")
        
        if args.list_saves:
            saves = manager.list_save_points()
            if saves:
                print(f"\n=== Available Save Points ===")
                for save in saves:
                    print(f"📁 {save['name']}")
                    print(f"   Time: {save['timestamp']}")
                    print(f"   Progress: {save['progress']:.1f}%")
                    print(f"   Phase: {save['phase']}")
                    print()
            else:
                print("No save points found.")
        
        if args.resume:
            summary = manager.generate_resume_summary()
            print(f"\n=== Resume Context ===")
            print(summary)
        
        if args.backup:
            if manager.backup_current_state():
                print("🔄 Automatic backup created")
            else:
                print("❌ Failed to create backup")
        
        if args.cleanup:
            deleted = manager.cleanup_old_saves(args.cleanup)
            print(f"🗑️  Cleaned up {deleted} old save files")
        
        if args.inspire:
            inspiration = manager.get_inspiration(args.inspire)
            if "error" in inspiration:
                print(f"❌ {inspiration['error']}")
                if "available_categories" in inspiration:
                    print(f"Available categories: {', '.join(inspiration['available_categories'])}")
            else:
                print(f"🎲 Inspiration from {inspiration['category']}: {inspiration['word']}")
                print(f"📝 {inspiration['instruction']}")
        
        if args.inspire_random:
            inspiration = manager.get_random_inspiration()
            if "error" in inspiration:
                print(f"❌ {inspiration['error']}")
            else:
                print(f"🎲 Random inspiration from {inspiration['category']}: {inspiration['word']}")
                print(f"📝 {inspiration['instruction']}")
        
        if args.inspire_contextual:
            inspiration = manager.get_contextual_inspiration()
            if "error" in inspiration:
                print(f"❌ {inspiration['error']}")
            else:
                print(f"🎯 Contextual inspiration from {inspiration['category']}: {inspiration['word']}")
                print(f"📝 {inspiration['instruction']}")
                if "context" in inspiration:
                    print(f"🔍 Context: {inspiration['context']}")
        
        if args.must_inspire:
            inspiration = manager.must_use_inspiration(args.must_inspire)
            if "error" in inspiration:
                print(f"❌ {inspiration['error']}")
            else:
                print(f"⚡ FORCED INSPIRATION for '{args.must_inspire}'")
                print(f"🎯 Category: {inspiration['category']}")
                print(f"🎲 Word: {inspiration['word']}")
                print(f"📝 {inspiration['instruction']}")
                if "context" in inspiration:
                    print(f"🔍 Context: {inspiration['context']}")
                print(f"✅ Logged to inspiration history")
        
        if args.inspiration_history:
            history = manager.get_inspiration_history()
            if history:
                print(f"\n=== Inspiration Usage History ===")
                for i, entry in enumerate(history, 1):
                    print(f"{i}. {entry['word']} ({entry['category']})")
                    print(f"   Context: {entry['usage_context']}")
                    print(f"   Gate: {entry['gate']}")
                    print(f"   Location: {entry['location']}")
                    print()
            else:
                print("No inspiration usage history found.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())