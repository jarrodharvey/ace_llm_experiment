"""
Core Game Engine with Event Sourcing

Manages game state through immutable events, preventing corruption
and enabling perfect audit trails and state reconstruction.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

from state import EventStore, GameState
from plugins.evidence import EvidencePlugin
from plugins.characters import CharacterPlugin
from plugins.dice import DicePlugin
from plugins.trial import TrialPlugin


class CourtRoomEngine:
    """Main game engine coordinating all game systems"""
    
    def __init__(self):
        self.cases_dir = Path("cases")
        self.cases_dir.mkdir(exist_ok=True)
        
        # Core systems
        self.event_store: Optional[EventStore] = None
        self.game_state: Optional[GameState] = None
        self.current_case_id: Optional[str] = None
        
        # Game mechanic plugins
        self.evidence = EvidencePlugin()
        self.characters = CharacterPlugin()
        self.dice = DicePlugin()
        self.trial = TrialPlugin()
    
    def create_case(self, case_name: str, test_mode: bool = False) -> str:
        """Create a new mystery case with real-world inspiration"""
        
        # Generate case ID from name
        case_id = self._generate_case_id(case_name)
        
        # Create case directory
        case_dir = self.cases_dir / case_id
        if case_dir.exists():
            raise ValueError(f"Case already exists: {case_id}")
        
        case_dir.mkdir(parents=True)
        
        # Initialize event store
        event_store = EventStore(case_dir / "events.json")
        
        # Create initial case event
        initial_event = {
            "type": "case_created",
            "data": {
                "case_name": case_name,
                "case_id": case_id,
                "test_mode": test_mode,
                "created_by": "courtroom_cli",
                "game_version": "2.0"
            }
        }
        
        event_store.add_event(initial_event)
        
        # Generate real-world inspiration
        self._generate_case_inspiration(case_dir, case_name)
        
        # Generate opening scene
        self._generate_opening_scene(case_dir, case_name)
        
        # Initialize game state
        game_state = GameState(event_store)
        
        # Add case initialization event
        init_event = {
            "type": "case_initialized",
            "data": {
                "phase": "investigation",
                "status": "ready_to_play",
                "gates": self._get_default_gates(),
                "current_location": "law_office"
            }
        }
        
        event_store.add_event(init_event)
        
        return case_id
    
    def _generate_case_id(self, case_name: str) -> str:
        """Generate URL-safe case ID from case name"""
        # Convert to lowercase and replace spaces/special chars with underscores
        case_id = re.sub(r'[^a-zA-Z0-9]+', '_', case_name.lower())
        case_id = re.sub(r'_+', '_', case_id)  # Remove multiple underscores
        case_id = case_id.strip('_')  # Remove leading/trailing underscores
        
        # Ensure it's not empty
        if not case_id:
            case_id = f"case_{uuid.uuid4().hex[:8]}"
        
        return case_id
    
    def _generate_case_inspiration(self, case_dir: Path, case_name: str) -> None:
        """Generate real-world legal case inspiration"""
        # This would integrate with the real-world inspiration system
        # For now, create placeholder
        inspiration_content = f"""# Real-World Case Inspiration

Case Name: {case_name}
Generated: {datetime.now().isoformat()}

This case draws inspiration from real legal proceedings, adapted for interactive gameplay.
The AI director will use this as thematic foundation for improvised investigation and trial.

Key Themes:
- Legal procedure and evidence presentation
- Character motivation and credibility assessment  
- Logical deduction and puzzle-solving
- Dramatic courtroom confrontation

Crime Type: [To be determined during gameplay]
Setting: Modern legal system with Ace Attorney-inspired dramatic elements
"""
        
        (case_dir / "inspiration.txt").write_text(inspiration_content)
    
    def _generate_opening_scene(self, case_dir: Path, case_name: str) -> None:
        """Generate dramatic opening scene"""
        # This would integrate with ChatGPT for opening generation
        # For now, create template
        opening_content = f"""# {case_name}

*You are a defense attorney in a world where the legal system operates with dramatic flair.*

The morning light streams through your law office windows as you review case files. Your assistant bursts through the door with urgent news about a new case that demands immediate attention.

This is the beginning of {case_name} - a mystery that will test your skills in investigation, evidence gathering, and courtroom battle.

The facts are still emerging, but one thing is certain: someone needs your help, and the truth must be uncovered through careful investigation and dramatic legal confrontation.

Your journey begins now."""
        
        (case_dir / "opening.txt").write_text(opening_content)
    
    def _get_default_gates(self) -> List[Dict[str, Any]]:
        """Get default investigation gates for new cases"""
        return [
            {
                "id": "initial_investigation",
                "name": "Initial Investigation", 
                "type": "investigation",
                "status": "pending",
                "description": "Gather basic facts and evidence about the case"
            },
            {
                "id": "witness_interviews", 
                "name": "Witness Interviews",
                "type": "investigation", 
                "status": "pending",
                "description": "Interview key witnesses and gather testimonies"
            },
            {
                "id": "evidence_analysis",
                "name": "Evidence Analysis",
                "type": "investigation",
                "status": "pending", 
                "description": "Analyze collected evidence for trial preparation"
            },
            {
                "id": "trial_preparation",
                "name": "Trial Preparation",
                "type": "trial_prep",
                "status": "pending",
                "description": "Prepare legal strategy and evidence presentation"
            }
        ]
    
    def case_exists(self, case_id: str) -> bool:
        """Check if case exists"""
        return (self.cases_dir / case_id).exists()
    
    def load_case(self, case_id: str) -> None:
        """Load case state from events"""
        case_dir = self.cases_dir / case_id
        if not case_dir.exists():
            raise ValueError(f"Case not found: {case_id}")
        
        # Load event store
        self.event_store = EventStore(case_dir / "events.json")
        
        # Reconstruct game state from events
        self.game_state = GameState(self.event_store)
        
        # Initialize plugins with current state
        state_data = self.game_state.get_current_state()
        self.evidence.load_state(state_data.get("evidence", {}))
        self.characters.load_state(state_data.get("characters", {}))
        self.dice.load_state(state_data.get("dice", {}))
        self.trial.load_state(state_data.get("trial", {}))
        
        self.current_case_id = case_id
    
    def get_opening_text(self) -> str:
        """Get case opening text"""
        if not self.current_case_id:
            raise ValueError("No case loaded")
        
        opening_file = self.cases_dir / self.current_case_id / "opening.txt"
        if opening_file.exists():
            return opening_file.read_text()
        else:
            return "Opening text not available."
    
    def get_resume_context(self) -> Dict[str, Any]:
        """Get context for resuming gameplay"""
        if not self.game_state:
            raise ValueError("No case loaded")
        
        state = self.game_state.get_current_state()
        
        # Determine current status
        current_phase = state.get("phase", "investigation")
        completed_gates = [g for g in state.get("gates", []) if g.get("status") == "completed"]
        pending_gates = [g for g in state.get("gates", []) if g.get("status") == "pending"]
        
        # Determine available actions
        available_actions = []
        if current_phase == "investigation":
            available_actions.extend(["gather evidence", "interview witness", "examine location"])
        if pending_gates:
            available_actions.append(f"work on {pending_gates[0]['name']}")
        if len(completed_gates) >= 2:  # Ready for trial
            available_actions.append("start trial")
        
        status_text = f"{current_phase.title()} phase"
        if completed_gates:
            status_text += f" - {len(completed_gates)} gates completed"
        
        return {
            "status": status_text,
            "phase": current_phase,
            "completed_gates": len(completed_gates),
            "total_gates": len(state.get("gates", [])),
            "available_actions": available_actions,
            "evidence_count": len(state.get("evidence", {})),
            "character_count": len(state.get("characters", {}))
        }
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get complete current state for AI processing"""
        if not self.game_state:
            return {}
        
        return self.game_state.get_current_state()
    
    def list_cases(self) -> List[str]:
        """List all available cases"""
        if not self.cases_dir.exists():
            return []
        
        cases = []
        for case_dir in self.cases_dir.iterdir():
            if case_dir.is_dir() and (case_dir / "events.json").exists():
                cases.append(case_dir.name)
        
        return sorted(cases)
    
    def get_case_status(self, case_id: str) -> str:
        """Get status of a specific case"""
        try:
            # Temporarily load case to get status
            old_case = self.current_case_id
            self.load_case(case_id)
            
            state = self.game_state.get_current_state()
            phase = state.get("phase", "unknown")
            gates = state.get("gates", [])
            completed = len([g for g in gates if g.get("status") == "completed"])
            total = len(gates)
            
            # Restore previous case
            if old_case:
                self.load_case(old_case)
            
            return f"{phase}, {completed}/{total} gates"
            
        except Exception:
            return "unknown"
    
    def archive_case(self, case_id: str) -> None:
        """Archive a completed case"""
        case_dir = self.cases_dir / case_id
        if not case_dir.exists():
            raise ValueError(f"Case not found: {case_id}")
        
        # Create archive directory
        archive_dir = Path("archive")
        archive_dir.mkdir(exist_ok=True)
        
        # Move case to archive
        import shutil
        shutil.move(str(case_dir), str(archive_dir / case_id))
    
    # Plugin integration methods
    def add_evidence(self, name: str, description: str) -> None:
        """Add evidence through evidence plugin"""
        if not self.event_store:
            raise ValueError("No case loaded")
        
        # Use evidence plugin to validate and process
        evidence_data = self.evidence.add_evidence(name, description)
        
        # Record event
        event = {
            "type": "evidence_added",
            "data": evidence_data
        }
        self.event_store.add_event(event)
    
    def meet_character(self, name: str, role: str) -> None:
        """Introduce character through character plugin"""
        if not self.event_store:
            raise ValueError("No case loaded")
        
        # Use character plugin to validate and process
        character_data = self.characters.meet_character(name, role)
        
        # Record event  
        event = {
            "type": "character_met",
            "data": character_data
        }
        self.event_store.add_event(event)
    
    def roll_dice(self, action: str, modifiers: List[str] = None) -> Dict[str, Any]:
        """Roll dice through dice plugin"""
        if not self.event_store:
            raise ValueError("No case loaded")
        
        # Use dice plugin to handle roll
        roll_result = self.dice.roll_action(action, modifiers or [])
        
        # Record event
        event = {
            "type": "dice_rolled", 
            "data": roll_result
        }
        self.event_store.add_event(event)
        
        return roll_result