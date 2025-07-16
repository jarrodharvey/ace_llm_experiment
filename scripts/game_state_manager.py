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
from dice_system import DiceRoller
from character_name_generator import CharacterNameGenerator
from enhanced_save_system import NarrativeSaveSystem
from red_herring_system import RedHerringClassifier

class ContextValidator:
    """Validates AI actions against current game state to prevent interpretation errors"""
    
    def __init__(self, game_state_manager):
        self.gsm = game_state_manager
        
    def validate_action_request(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if requested action is appropriate for current state"""
        
        current_phase = context['case_info']['current_phase']
        trial_status = context.get('trial_progress', {}).get('status', 'not_started')
        
        # Action compatibility matrix
        action_rules = {
            'start_trial': {
                'valid_when': trial_status == 'not_started',
                'invalid_reason': 'Trial already in progress',
                'alternative': 'continue_trial_proceedings'
            },
            'start_cross_examination': {
                'valid_when': trial_status == 'in_progress',
                'invalid_reason': 'Trial not active',
                'alternative': 'start_trial'
            },
            'opening_statement': {
                'valid_when': trial_status == 'not_started',
                'invalid_reason': 'Trial already in progress',
                'alternative': 'continue_trial_proceedings'
            },
            'gather_evidence': {
                'valid_when': current_phase == 'investigation',
                'invalid_reason': 'Not in investigation phase',
                'alternative': 'continue_current_phase'
            }
        }
        
        rule = action_rules.get(action, {})
        valid_condition = rule.get('valid_when', True)
        
        # Evaluate condition if it's a string
        if isinstance(valid_condition, str):
            try:
                valid_condition = eval(valid_condition)
            except:
                valid_condition = True
        
        if not valid_condition:
            return {
                'valid': False,
                'reason': rule.get('invalid_reason', 'Action not valid for current state'),
                'alternative': rule.get('alternative', 'check_status'),
                'current_state': current_phase,
                'trial_status': trial_status
            }
        
        return {'valid': True}
    
    def generate_context_summary(self, context: Dict[str, Any]) -> str:
        """Generate mandatory context summary for AI interpretation"""
        
        phase = context['case_info']['current_phase']
        trial_status = context.get('trial_progress', {}).get('status', 'not_started')
        
        # Determine current situation
        if trial_status == 'in_progress':
            current_witness = context.get('trial_progress', {}).get('current_witness')
            current_exam = context.get('trial_progress', {}).get('current_cross_exam')
            
            if current_exam and current_exam.get('witness'):
                situation = f"Cross-examining {current_exam['witness']}"
            elif current_witness:
                situation = f"Trial with {current_witness} active"
            else:
                situation = "Trial proceedings in progress"
        else:
            situation = f"In {phase} phase"
        
        # Get last significant event
        last_event = self._get_last_event(context)
        
        # Get valid actions
        valid_actions = self.get_valid_actions(context)
        
        return f"""
**MANDATORY CONTEXT INTERPRETATION:**
• Current Phase: {phase}
• Trial Status: {trial_status}
• Current Situation: {situation}
• Last Event: {last_event}
• Valid Actions: {', '.join(valid_actions)}

**BEFORE ANY ACTION - VALIDATE:**
✓ Current phase matches your understanding
✓ Requested action is valid for current state  
✓ Action advances narrative appropriately
✓ No contradictions with loaded context
"""
    
    def _get_last_event(self, context: Dict[str, Any]) -> str:
        """Determine last significant event from context"""
        
        trial_progress = context.get('trial_progress', {})
        trial_status = trial_progress.get('status', 'not_started')
        
        if trial_status == 'in_progress':
            current_exam = trial_progress.get('current_cross_exam')
            if current_exam:
                return f"Cross-examination of {current_exam['witness']} started"
            else:
                return "Trial proceedings began"
        
        # Check recent progress
        recent_progress = context.get('recent_progress', {})
        last_gate = recent_progress.get('last_completed_gate')
        if last_gate:
            return f"Completed {last_gate.replace('_', ' ').title()}"
        
        return "Game state loaded"
    
    def get_valid_actions(self, context: Dict[str, Any]) -> List[str]:
        """Get list of valid actions for current state"""
        
        current_phase = context['case_info']['current_phase']
        trial_status = context.get('trial_progress', {}).get('status', 'not_started')
        
        if trial_status == 'in_progress':
            current_exam = context.get('trial_progress', {}).get('current_cross_exam')
            if current_exam:
                return ['press_statement', 'present_evidence', 'end_cross_examination']
            else:
                return ['start_cross_examination', 'call_witness', 'present_evidence']
        elif current_phase == 'investigation':
            return ['gather_evidence', 'interview_witness', 'start_trial']
        else:
            return ['start_trial', 'continue_proceedings']
    
    def check_context_violations(self, context: Dict[str, Any]) -> List[str]:
        """Check for common context interpretation violations"""
        
        violations = []
        trial_status = context.get('trial_progress', {}).get('status', 'not_started')
        current_phase = context['case_info']['current_phase']
        
        # Common violation patterns
        if trial_status == 'in_progress' and current_phase != 'trial':
            violations.append("Trial status and phase mismatch")
        
        current_exam = context.get('trial_progress', {}).get('current_cross_exam')
        if current_exam and not current_exam.get('witness'):
            violations.append("Cross-examination active but no witness specified")
        
        return violations

class GameStateManager:
    def __init__(self, case_path: str):
        self.case_path = Path(case_path)
        self.case_name = self.case_path.name
        
        # Load shared configuration
        self.config_manager = get_config_manager()
        
        # Auto-detect case type from file structure
        self.case_type = self.detect_case_type()
        
        # Load case structure dynamically based on type
        self.case_structure = self.load_case_structure()
        self.current_state = self.load_current_state()
        self.trial_state = self.load_trial_state()
        
        # Auto-detect case characteristics
        self.case_length = self.detect_case_length()
        
        # Get all gates for this case (investigation + trial) for proper validation
        # Both simple and complex cases now use configuration for consistency
        self.gates = self.config_manager.get_gates_for_case_length(self.case_length)
        
        self.total_gates = len(self.gates)
        
        # Load inspiration pool for entropy prevention
        self.inspiration_pool = self.load_inspiration_pool()
        
        # Initialize dice roller for action resolution
        self.dice_roller = DiceRoller(str(self.case_path))
        
        # Initialize character name generator
        self.name_generator = CharacterNameGenerator(str(self.case_path))
        
        # Initialize red herring classification system
        self.red_herring_classifier = RedHerringClassifier(str(self.case_path))
        
        # Initialize enhanced narrative save system
        self.narrative_save_system = NarrativeSaveSystem(str(self.case_path))
        
        # Initialize context validator
        self.context_validator = ContextValidator(self)
        
        # Load client name for dialogue substitution
        self.client_name = self.load_client_name()
        
        # Initialize murder escalation system
        self.initialize_murder_escalation()
        
    def detect_case_type(self) -> str:
        """Auto-detect case type from file structure"""
        # Check for complex case structure
        backbone_dir = self.case_path / "backbone"
        if backbone_dir.exists() and (backbone_dir / "case_structure.json").exists():
            return "complex"
        
        # Check for simple improvisation structure
        real_life_file = self.case_path / "real_life_case_summary.txt"
        opening_file = self.case_path / "case_opening.txt"
        if real_life_file.exists() and opening_file.exists():
            return "simple_improvisation"
        
        # Fallback to complex for backward compatibility
        return "complex"
        
    def load_case_structure(self) -> Dict[str, Any]:
        """Load the basic case structure based on case type"""
        if self.case_type == "complex":
            structure_file = self.case_path / "backbone" / "case_structure.json"
            if not structure_file.exists():
                raise FileNotFoundError(f"Case structure not found: {structure_file}")
            
            with open(structure_file, 'r') as f:
                return json.load(f)
        
        elif self.case_type == "simple_improvisation":
            # Create minimal structure for simple improvisation cases
            return {
                "case_type": "simple_improvisation",
                "name": self.case_name.replace("_", " ").title(),
                "description": "Improvisation-first case",
                "phase": "investigation"
            }
        
        else:
            raise ValueError(f"Unknown case type: {self.case_type}")
    
    def load_current_state(self) -> Dict[str, Any]:
        """Load current investigation progress based on case type"""
        progress_file = self.case_path / "game_state" / "investigation_progress.json"
        
        if not progress_file.exists():
            if self.case_type == "simple_improvisation":
                # Initialize simple improvisation state
                return self.create_simple_improvisation_state()
            else:
                raise FileNotFoundError(f"Investigation progress not found: {progress_file}")
        
        with open(progress_file, 'r') as f:
            return json.load(f)
    
    def load_trial_state(self) -> Dict[str, Any]:
        """Load current trial progress based on case type"""
        trial_file = self.case_path / "game_state" / "trial_progress.json"
        
        if not trial_file.exists():
            if self.case_type == "simple_improvisation":
                # Initialize simple trial state
                return self.create_simple_trial_state()
            else:
                raise FileNotFoundError(f"Trial progress not found: {trial_file}")
        
        with open(trial_file, 'r') as f:
            return json.load(f)
    
    def create_simple_improvisation_state(self) -> Dict[str, Any]:
        """Create initial state for simple improvisation cases"""
        # Use the random case length from configuration to determine gates
        case_config = self.config_manager.config["case_types"]["simple_improvisation"]
        case_length = case_config.get("trial_trigger_after", 1)
        
        # Get proper gate structure from configuration based on case length
        gates = self.config_manager.get_gates_for_case_length(case_length)
        
        # Separate investigation and trial gates using configuration
        gate_classifications = self.config_manager.config["gate_classifications"]
        investigation_gate_types = gate_classifications["investigation"]
        trial_gate_types = gate_classifications["trial"]
        
        # Create investigation gates structure (may be empty for trial-only cases)
        investigation_gates = {}
        for gate in gates:
            if gate in investigation_gate_types:  # Only investigation gates
                investigation_gates[gate] = {
                    "status": "pending",
                    "description": f"Improvised {gate} phase",
                    "evidence_found": [],
                    "interviews_conducted": [],
                    "started_at": None,
                    "completed_at": None
                }
        
        # Determine the first gate and phase
        first_gate = gates[0] if gates else "trial_opening"
        if case_length == 1:
            # Trial-only case - start directly in trial phase
            current_phase = "trial"
            # Ensure trial_ready is True for trial-only cases
            trial_ready = True
        else:
            # Investigation + trial case - start in investigation phase
            current_phase = "investigation"
            trial_ready = False
        
        state = {
            "case_type": "simple_improvisation",
            "case_length": case_length,
            "current_phase": current_phase,
            "current_gate": first_gate,
            "investigation_gates": investigation_gates,
            "evidence_found": [],
            "character_trust_levels": {},
            "witnesses_interviewed": [],
            "character_facts": {},
            "location_progress": {},
            "failed_attempts": [],
            "inspiration_usage": [],
            "trial_ready": trial_ready,
            "last_updated": None
        }
        
        # Save the state file
        self.save_current_state(state)
        
        # Initialize character tracking files
        self._initialize_character_tracking_files()
        
        return state
    
    def _initialize_character_tracking_files(self):
        """Initialize character tracking files for proper character continuity"""
        # Ensure game_state directory exists
        game_state_dir = self.case_path / "game_state"
        game_state_dir.mkdir(exist_ok=True)
        
        # Initialize character families file if it doesn't exist
        families_file = game_state_dir / "character_families.json"
        if not families_file.exists():
            with open(families_file, 'w') as f:
                json.dump({}, f)
        
        # Initialize used character names file if it doesn't exist
        names_file = game_state_dir / "used_character_names.json"
        if not names_file.exists():
            with open(names_file, 'w') as f:
                json.dump([], f)
        
        # Initialize dice rolls file if it doesn't exist
        dice_file = game_state_dir / "dice_rolls.json"
        if not dice_file.exists():
            with open(dice_file, 'w') as f:
                json.dump([], f)
    
    def create_simple_trial_state(self) -> Dict[str, Any]:
        """Create initial trial state for simple improvisation cases"""
        state = {
            "case_type": "simple_improvisation",
            "trial_phase": "not_started",
            "current_witness": None,
            "witnesses_examined": [],
            "evidence_presented": [],
            "objections_sustained": 0,
            "objections_overruled": 0,
            "trial_gates": {
                "opening_statements": {"status": "pending", "completed_at": None},
                "witness_examination": {"status": "pending", "completed_at": None},
                "final_argument": {"status": "pending", "completed_at": None}
            },
            "trial_ready": False,
            "last_updated": None
        }
        
        # Save the state file
        self.save_trial_state(state)
        return state
        
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
        """Load inspiration pool for entropy prevention (legacy support)"""
        inspiration_file = self.case_path / "inspiration_pool.json"
        if not inspiration_file.exists():
            return {}
        
        with open(inspiration_file, 'r') as f:
            return json.load(f)
    
    def load_client_name(self) -> str:
        """Load client name based on case type"""
        try:
            if self.case_type == "complex":
                character_facts_file = self.case_path / "backbone" / "character_facts.json"
                if not character_facts_file.exists():
                    return "[Client Name]"  # Fallback to placeholder
                
                with open(character_facts_file, 'r') as f:
                    character_facts = json.load(f)
                
                # Find the character marked as client
                for character in character_facts.get("characters", []):
                    name = character.get("name", "")
                    if "(Client)" in name:
                        # Remove the "(Client)" suffix and return clean name
                        return name.replace("(Client)", "").strip()
                
                return "[Client Name]"  # Fallback if no client found
            
            elif self.case_type == "simple_improvisation":
                # For simple cases, derive client name from case name or use placeholder
                case_words = self.case_name.replace("_", " ").title().split()
                if len(case_words) >= 2:
                    return f"{case_words[0][0]}. {case_words[-1]}"  # e.g., "M. Masquerade"
                else:
                    return "[Client Name]"
            
            return "[Client Name]"
        except Exception:
            return "[Client Name]"  # Fallback on any error
    
    def save_current_state(self, state: Dict[str, Any]) -> None:
        """Save current investigation state to file"""
        progress_file = self.case_path / "game_state" / "investigation_progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(progress_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def save_trial_state(self, state: Dict[str, Any]) -> None:
        """Save current trial state to file"""
        trial_file = self.case_path / "game_state" / "trial_progress.json"
        trial_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(trial_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def get_client_name(self) -> str:
        """Get the client's name for dialogue substitution"""
        return self.client_name
    
    def substitute_client_name(self, text: str) -> str:
        """Substitute [Client Name] placeholder with actual client name in text"""
        return text.replace("[Client Name]", self.client_name)
    
    # Murder Escalation System
    
    def initialize_murder_escalation(self) -> None:
        """Initialize murder escalation system state"""
        if "murder_escalation" not in self.current_state:
            self.current_state["murder_escalation"] = {
                "escalated": False,
                "escalation_checks": [],
                "original_crime": "unknown",
                "escalation_gate": None
            }
    
    def detect_case_crime_type(self) -> str:
        """Detect the original crime type from case opening"""
        try:
            opening_file = self.case_path / "case_opening.txt"
            if opening_file.exists():
                with open(opening_file, 'r') as f:
                    opening_text = f.read().lower()
                
                # Check for murder indicators first
                if any(word in opening_text for word in ["murder", "killed", "dead body", "corpse", "homicide"]):
                    return "murder"
                
                # Check for other crime types
                if any(word in opening_text for word in ["burglary", "burglar", "break-in", "breaking and entering"]):
                    return "burglary"
                elif any(word in opening_text for word in ["theft", "stolen", "robbery", "robbed"]):
                    return "theft"
                elif any(word in opening_text for word in ["assault", "attacked", "beaten"]):
                    return "assault"
                elif any(word in opening_text for word in ["fraud", "embezzlement", "scam"]):
                    return "fraud"
                
            return "unknown"
        except Exception:
            return "unknown"
    
    def check_murder_escalation(self, gate_name: str) -> bool:
        """Check if murder escalation should occur at this gate"""
        # Initialize escalation state if needed
        if "murder_escalation" not in self.current_state:
            self.initialize_murder_escalation()
            # Set original crime type
            self.current_state["murder_escalation"]["original_crime"] = self.detect_case_crime_type()
        
        escalation_state = self.current_state["murder_escalation"]
        
        # Skip if already escalated
        if escalation_state["escalated"]:
            return False
        
        # Skip if already a murder case
        if escalation_state["original_crime"] == "murder":
            return False
        
        # Skip if already checked this gate
        if gate_name in escalation_state["escalation_checks"]:
            return False
        
        # Add to checked gates
        escalation_state["escalation_checks"].append(gate_name)
        
        # Get investigation gates only (exclude trial gates)
        investigation_gates = [g for g in self.gates if "trial" not in g.lower()]
        
        # Mandatory escalation on final investigation gate
        if gate_name == investigation_gates[-1]:
            return True
        
        # 50% chance escalation on other gates
        roll_result = self.dice_roller.roll_d20(description=f"Murder escalation check for gate '{gate_name}'")
        roll_total = roll_result["total"]
        escalation_occurs = roll_total >= 11  # 50% chance (11-20)
        
        # Update the description based on result
        roll_result["description"] = f"Murder escalation check for gate '{gate_name}' - {'ESCALATED' if escalation_occurs else 'No escalation'}"
        
        return escalation_occurs
    
    def escalate_to_murder(self, gate_name: str) -> None:
        """Escalate case to murder with dramatic notification"""
        escalation_state = self.current_state["murder_escalation"]
        
        # Mark as escalated
        escalation_state["escalated"] = True
        escalation_state["escalation_gate"] = gate_name
        
        # Get escalation narrative
        original_crime = escalation_state["original_crime"]
        escalation_narrative = self.get_escalation_narrative(original_crime, gate_name)
        
        # Display dramatic escalation message
        print("\n" + "="*60)
        print("🚨 CASE ESCALATION: MURDER REVEALED! 🚨")
        print("="*60)
        print(f"Original Crime: {original_crime.title()}")
        print(f"Escalation Gate: {gate_name}")
        print(f"Escalation Type: {escalation_narrative['type']}")
        print(f"\nNarrative Hook: {escalation_narrative['description']}")
        print(f"\nGM Guidance: {escalation_narrative['gm_guidance']}")
        print("="*60)
        
        # Save state
        self.save_current_state_to_file()
    
    def get_escalation_narrative(self, original_crime: str, gate_name: str) -> Dict[str, str]:
        """Get narrative suggestions for murder escalation"""
        escalation_patterns = {
            "burglary": {
                "type": "Victim Dies from Injuries",
                "description": "The victim has died from injuries sustained during the burglary. What seemed like a simple break-in has become a murder investigation.",
                "gm_guidance": "Consider: Did the victim die from the initial attack, or were they killed to prevent identification? Recontextualize existing evidence as murder clues."
            },
            "theft": {
                "type": "Witness Elimination",
                "description": "Someone who witnessed the theft has been found dead. The thief killed them to prevent identification.",
                "gm_guidance": "Consider: Who saw the theft? How did the killer learn they were a witness? Use existing evidence to build the murder timeline."
            },
            "assault": {
                "type": "Escalated Violence",
                "description": "The assault victim has succumbed to their injuries. The attacker is now facing murder charges.",
                "gm_guidance": "Consider: Was the death intentional or accidental? Did the attacker try to cover up the escalation? Look for evidence of consciousness of guilt."
            },
            "fraud": {
                "type": "Accomplice Silenced",
                "description": "A key figure in the fraud scheme has been found dead. Someone killed them to prevent their testimony.",
                "gm_guidance": "Consider: Who had the most to lose from the accomplice's testimony? How does this change the financial motive? Follow the money trail."
            },
            "unknown": {
                "type": "Hidden Murder Revealed",
                "description": "What appeared to be a minor crime was actually a cover-up for murder. The true crime has been revealed.",
                "gm_guidance": "Consider: How long has the murder been hidden? What was the original crime meant to conceal? Use pure random inspiration for unique twist."
            }
        }
        
        return escalation_patterns.get(original_crime, escalation_patterns["unknown"])
    
    def is_murder_case(self) -> bool:
        """Check if case has escalated to murder"""
        if "murder_escalation" not in self.current_state:
            self.initialize_murder_escalation()
            original_crime = self.detect_case_crime_type()
            self.current_state["murder_escalation"]["original_crime"] = original_crime
            return original_crime == "murder"
        
        escalation_state = self.current_state["murder_escalation"]
        return escalation_state["escalated"] or escalation_state["original_crime"] == "murder"
    
    def get_escalation_status(self) -> Dict[str, Any]:
        """Get current escalation status and probabilities"""
        if "murder_escalation" not in self.current_state:
            self.initialize_murder_escalation()
            self.current_state["murder_escalation"]["original_crime"] = self.detect_case_crime_type()
        
        escalation_state = self.current_state["murder_escalation"]
        investigation_gates = [g for g in self.gates if "trial" not in g.lower()]
        
        return {
            "is_murder_case": self.is_murder_case(),
            "original_crime": escalation_state["original_crime"],
            "escalated": escalation_state["escalated"],
            "escalation_gate": escalation_state.get("escalation_gate"),
            "gates_checked": escalation_state["escalation_checks"],
            "remaining_gates": [g for g in investigation_gates if g not in escalation_state["escalation_checks"]],
            "final_gate_mandatory": investigation_gates[-1] if investigation_gates else None
        }
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get comprehensive current status"""
        escalation_status = self.get_escalation_status()
        
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
            "witnesses_interviewed": len(self.current_state.get("witnesses_interviewed", [])),
            "murder_escalation": escalation_status
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
    
    def complete_gate(self, gate_name: str, narrative_context: Optional[Dict[str, Any]] = None) -> bool:
        """Complete a specific gate with validation and narrative save"""
        # Validate gate exists
        if gate_name not in self.gates:
            raise ValueError(f"Gate '{gate_name}' not found in case structure. Available gates: {self.gates}")
        
        # Check current status
        current_status = self.current_state["investigation_gates"].get(gate_name)
        if current_status == "completed":
            return False  # Already completed
        
        # Update state
        self.current_state["investigation_gates"][gate_name] = "completed"
        
        # Create enhanced narrative save if context provided
        if narrative_context:
            try:
                save_path = self.narrative_save_system.create_narrative_save(gate_name, narrative_context)
                print(f"📖 Narrative save created: {os.path.basename(save_path)}")
            except Exception as e:
                print(f"⚠️ Warning: Could not create narrative save: {e}")
        
        # Save changes
        self.save_current_state_to_file()
        
        return True
    
    def start_gate(self, gate_name: str) -> bool:
        """Mark a gate as in progress and check for murder escalation"""
        if gate_name not in self.gates:
            raise ValueError(f"Gate '{gate_name}' not found in case structure. Available gates: {self.gates}")
        
        current_status = self.current_state["investigation_gates"].get(gate_name)
        if current_status in ["completed", "in_progress"]:
            return False  # Already started or completed
        
        # Check for murder escalation at gate start
        if self.check_murder_escalation(gate_name):
            self.escalate_to_murder(gate_name)
        
        # Update state
        self.current_state["investigation_gates"][gate_name] = "in_progress"
        
        # Save changes
        self.save_current_state_to_file()
        
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
    
    def save_current_state_to_file(self) -> None:
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
        self.save_current_state_to_file()
        
        return True
    
    def update_character_trust(self, character_name: str, change: int) -> int:
        """Update character trust level"""
        trust_levels = self.current_state.get("character_trust_levels", {})
        current_trust = trust_levels.get(character_name, 5)  # Default to 5
        
        new_trust = max(0, min(10, current_trust + change))  # Clamp to 0-10
        trust_levels[character_name] = new_trust
        
        self.current_state["character_trust_levels"] = trust_levels
        self.save_current_state_to_file()
        
        return new_trust
    
    def set_location(self, location_name: str) -> bool:
        """Update current location"""
        available_locations = self.current_state.get("available_locations", [])
        
        if location_name not in available_locations:
            return False  # Invalid location
        
        self.current_state["current_location"] = location_name
        self.save_current_state_to_file()
        
        return True
    
    def add_investigation_note(self, note: str) -> None:
        """Add investigation note"""
        notes = self.current_state.get("investigation_notes", [])
        notes.append({
            "note": note,
            "gate": self.get_next_gate() or "unknown"
        })
        
        self.current_state["investigation_notes"] = notes
        self.save_current_state_to_file()
    
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
        self.save_current_state_to_file()
        self.save_trial_state_to_file()
        
        return True
    
    def save_trial_state_to_file(self) -> None:
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
            self.save_current_state_to_file()
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
        self.save_current_state_to_file()
    
    def get_available_actions(self) -> List[str]:
        """Get context-appropriate available actions"""
        actions = []
        
        # Cross-examination specific actions take priority
        current_exam = self.trial_state.get("current_cross_exam")
        if current_exam and self.trial_state.get("trial_phase") == "cross_examination":
            witness_name = current_exam["witness"]
            cross_exam_data = self.load_trial_statements(witness_name)
            
            if "statements" in cross_exam_data:
                # Show witness statements as primary actions
                for stmt in cross_exam_data["statements"]:
                    stmt_preview = stmt["text"][:60] + "..." if len(stmt["text"]) > 60 else stmt["text"]
                    actions.append(f"Press statement {stmt['id']}: '{stmt_preview}'")
                
                # Show evidence presentation options
                evidence_list = self.current_state.get("evidence_collected", [])
                if evidence_list:
                    actions.append("Present evidence against a statement")
                
                # Cross-examination meta actions
                actions.append("Check cross-examination progress")
                actions.append("End cross-examination")
                
                return actions
        
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
            self.save_current_state_to_file()
            self.save_trial_state_to_file()
            
            return True
            
        except Exception:
            return False
    
    def get_resume_context(self) -> Dict[str, Any]:
        """Get context needed to resume gameplay"""
        # Determine actual current phase by checking trial state
        actual_phase = self.current_state.get("current_phase", "unknown")
        trial_status = self.trial_state.get("trial_status", "not_started")
        trial_phase = self.trial_state.get("trial_phase", "not_started")
        
        # If trial has started, use trial phase as current phase
        if trial_status == "in_progress" or trial_phase != "not_started":
            actual_phase = "trial"
        
        return {
            "case_info": {
                "name": self.case_name,
                "length": self.case_length,
                "current_phase": actual_phase,
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
                "trial_ready": self.is_trial_ready() or trial_status == "in_progress",
                "available_actions": self.get_available_actions()[:5],  # Top 5 actions
                "key_characters": self.get_key_character_status()
            },
            "trial_progress": {
                "status": trial_status,
                "phase": trial_phase,
                "current_witness": self.trial_state.get("current_witness"),
                "witnesses_examined": self.trial_state.get("witnesses_examined", []),
                "cross_exam_history": self.trial_state.get("cross_examination_history", [])
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
        """Generate comprehensive resume context from all available sources (evergreen)"""
        return self.generate_comprehensive_context()
    
    def generate_comprehensive_context(self) -> str:
        """Evergreen comprehensive context generation - reads all files + most recent saves"""
        summary = ""
        
        # 0. Context Validation (NEW)
        try:
            context = self.get_resume_context()
            validation_summary = self.context_validator.generate_context_summary(context)
            summary += validation_summary + "\n\n"
        except Exception as e:
            summary += f"⚠️ Could not load context validation: {e}\n\n"
        
        # 1. Case Foundation Context
        try:
            foundation_context = self.get_case_foundation_context()
            summary += foundation_context + "\n\n"
        except Exception as e:
            summary += f"⚠️ Could not load case foundation: {e}\n\n"
        
        # 2. Narrative Context (most recent narrative save)
        try:
            narrative_context = self.get_narrative_context()
            if narrative_context:
                summary += narrative_context + "\n\n"
        except Exception as e:
            summary += f"⚠️ Could not load narrative context: {e}\n\n"
        
        # 3. Current Mechanical State
        try:
            mechanical_context = self.get_mechanical_context()
            summary += mechanical_context + "\n\n"
        except Exception as e:
            summary += f"⚠️ Could not load mechanical context: {e}\n\n"
        
        # 4. All Additional Files Context
        try:
            additional_context = self.get_all_additional_files_context()
            if additional_context:
                summary += additional_context + "\n\n"
        except Exception as e:
            summary += f"⚠️ Could not load additional files: {e}\n\n"
        
        # 5. Save Context (for GM awareness)
        try:
            save_context = self.get_save_context()
            if save_context:
                summary += save_context + "\n\n"
        except Exception as e:
            summary += f"⚠️ Could not load save context: {e}\n\n"
        
        # 6. Available Actions (current state)
        try:
            actions_context = self.get_available_actions_context()
            summary += actions_context
        except Exception as e:
            summary += f"⚠️ Could not load available actions: {e}\n"
        
        return summary.strip()
    
    def get_case_foundation_context(self) -> str:
        """Get case foundation context from core files"""
        context = ""
        
        # Real life case inspiration
        real_life_file = self.case_path / "real_life_case_summary.txt"
        if real_life_file.exists():
            with open(real_life_file, 'r', encoding='utf-8') as f:
                real_life_content = f.read().strip()
            context += f"**=== CASE FOUNDATION ===**\n{real_life_content}\n"
        
        # Case opening
        opening_file = self.case_path / "case_opening.txt"
        if opening_file.exists():
            with open(opening_file, 'r', encoding='utf-8') as f:
                opening_content = f.read().strip()
            context += f"**=== ORIGINAL OPENING ===**\n{opening_content}\n"
        
        return context
    
    def get_narrative_context(self) -> str:
        """Get narrative context from most recent narrative save"""
        try:
            narrative_saves = self.narrative_save_system.list_narrative_saves()
            if not narrative_saves:
                return ""
            
            # Get most recent narrative save
            latest_save = narrative_saves[0]  # Already sorted by timestamp desc
            narrative_data = self.narrative_save_system.restore_narrative_context(latest_save['filename'])
            summary = self.narrative_save_system.generate_context_summary(narrative_data)
            
            return f"**=== NARRATIVE CONTEXT (from {latest_save['gate_name']}) ===**\n{summary}\n"
        except Exception:
            return ""
    
    def get_mechanical_context(self) -> str:
        """Get current mechanical state context"""
        context = self.get_resume_context()
        
        # Build mechanical summary
        summary = f"**=== CURRENT MECHANICAL STATE ===**\n"
        summary += f"**{context['case_info']['name']}** ({context['case_info']['length']}-day case)\n"
        
        # Progress
        progress = context['case_info']['progress']
        phase = context['case_info']['current_phase']
        summary += f"**Status:** {progress:.1f}% complete, {phase} phase\n"
        
        # Location and timing
        location = context['current_situation']['location']
        day = context['current_situation']['day']
        time_left = context['current_situation']['time_until_trial']
        summary += f"**Location:** {location.replace('_', ' ').title()}\n"
        summary += f"**Day {day}** - {time_left} until trial\n"
        
        # Trial-specific progress if in trial
        trial_progress = context.get('trial_progress', {})
        if trial_progress.get('status') == 'in_progress':
            summary += "**🏛️ TRIAL IN PROGRESS**\n"
            
            # Show witnesses examined
            witnesses_examined = trial_progress.get('witnesses_examined', [])
            if witnesses_examined:
                summary += f"**Witnesses Examined:** {', '.join(witnesses_examined)}\n"
            
            # Show current witness if in cross-examination
            current_witness = trial_progress.get('current_witness')
            if current_witness:
                summary += f"**Currently Cross-Examining:** {current_witness}\n"
            
            # Show cross-examination victories
            cross_exam_history = trial_progress.get('cross_exam_history', [])
            if cross_exam_history:
                total_victories = sum(1 for exam in cross_exam_history if exam.get('victory_achieved', False))
                summary += f"**Cross-Examination Victories:** {total_victories}\n"
        else:
            # Investigation progress
            last_gate = context['recent_progress']['last_completed_gate']
            current_gate = context['recent_progress']['current_gate']
            if last_gate:
                summary += f"**Last Completed:** {last_gate.replace('_', ' ').title()}\n"
            if current_gate:
                summary += f"**Current Focus:** {current_gate.replace('_', ' ').title()}\n"
        
        # Recent evidence
        recent_evidence = context['recent_progress']['recent_evidence']
        if recent_evidence:
            summary += "**Recent Evidence:**\n"
            for evidence in recent_evidence[-3:]:  # Show last 3
                summary += f"  - {evidence['name']}: {evidence['description']}\n"
        
        # Trial status
        if context['current_status']['trial_ready'] and trial_progress.get('status') != 'in_progress':
            summary += "**🚨 TRIAL READY!** You have enough evidence to proceed to trial.\n"
        
        return summary
    
    def get_all_additional_files_context(self) -> str:
        """Get context from all additional files (evergreen discovery)"""
        context = ""
        additional_files = []
        
        # Scan all files except saves directories and core files already processed
        for file_path in self.case_path.rglob('*'):
            if file_path.is_file():
                # Skip save directories
                if '/saves/' in str(file_path) or '/narrative_saves/' in str(file_path):
                    continue
                
                # Skip core files already processed
                if file_path.name in ['real_life_case_summary.txt', 'case_opening.txt', 
                                    'investigation_progress.json', 'trial_progress.json']:
                    continue
                
                # Skip binary files
                if file_path.suffix in ['.b64', '.pyc', '.DS_Store']:
                    continue
                
                additional_files.append(file_path)
        
        if not additional_files:
            return ""
        
        context += "**=== ADDITIONAL FILES CONTEXT ===**\n"
        
        for file_path in sorted(additional_files):
            try:
                relative_path = file_path.relative_to(self.case_path)
                
                # Handle JSON files
                if file_path.suffix == '.json':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    context += f"**{relative_path}:**\n"
                    context += f"  {self.format_json_summary(data)}\n"
                
                # Handle text files
                elif file_path.suffix in ['.txt', '.md']:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if content:
                        context += f"**{relative_path}:**\n"
                        # Truncate long content
                        if len(content) > 500:
                            content = content[:500] + "..."
                        context += f"  {content}\n"
                
            except Exception as e:
                context += f"**{relative_path}:** (Error reading: {e})\n"
        
        return context
    
    def format_json_summary(self, data: Dict[str, Any]) -> str:
        """Format JSON data for summary display"""
        if isinstance(data, dict):
            if len(data) <= 3:
                return str(data)
            else:
                keys = list(data.keys())[:3]
                return f"Dict with keys: {keys}... ({len(data)} total)"
        elif isinstance(data, list):
            return f"List with {len(data)} items"
        else:
            return str(data)
    
    def get_save_context(self) -> str:
        """Get save context for GM awareness"""
        context = ""
        
        # List manual saves
        saves = self.list_save_points()
        if saves:
            context += "**=== SAVE POINTS (for GM awareness) ===**\n"
            context += f"**Available save points:** {len(saves)}\n"
            
            # Show most recent save
            latest_save = saves[0]
            context += f"**Most recent save:** {latest_save['name']} "
            context += f"({latest_save['timestamp']})\n"
            
            # Show all save names
            save_names = [save['name'] for save in saves[:5]]  # Show first 5
            context += f"**Recent saves:** {', '.join(save_names)}\n"
        
        # Show narrative saves
        try:
            narrative_saves = self.narrative_save_system.list_narrative_saves()
            if narrative_saves:
                context += f"**Narrative saves:** {len(narrative_saves)} available\n"
                latest_narrative = narrative_saves[0]
                context += f"**Latest narrative save:** {latest_narrative['gate_name']} "
                context += f"({latest_narrative['timestamp']})\n"
        except Exception:
            pass
        
        return context
    
    def get_available_actions_context(self) -> str:
        """Get current available actions"""
        context = self.get_resume_context()
        actions = context['current_status']['available_actions']
        
        if actions:
            summary = "**=== AVAILABLE ACTIONS ===**\n"
            for action in actions[:5]:  # Show top 5
                summary += f"  - {action}\n"
            return summary
        else:
            return "**=== AVAILABLE ACTIONS ===**\n  - Use game state manager to see current options\n"
    
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
    
    def get_pure_random_inspiration(self, context: str) -> Dict[str, Any]:
        """Get completely random word for pure entropy forcing function"""
        try:
            from wonderwords import RandomWord
            r = RandomWord()
            
            # Generate random word with filtering
            word = r.word(
                word_min_length=3,
                word_max_length=12,
                include_categories=["noun", "verb", "adjective"]
            )
            
            return {
                "category": "pure_random",
                "word": word,
                "context": context,
                "source": "wonderwords",
                "instruction": f"Use A-to-C process: Current situation (A) + '{word}' (B) → Creative solution (C)"
            }
            
        except ImportError:
            # Fallback to basic random word if wonderwords not available
            import random
            import string
            
            # Simple fallback word generation
            fallback_words = [
                "anchor", "bridge", "cascade", "deliberate", "echo", "fragment", "gravity", 
                "hollow", "intricate", "journey", "kindle", "labyrinth", "momentum", "nebula",
                "obscure", "pivot", "quench", "radiant", "spiral", "turbulent", "unveil",
                "vibrant", "whisper", "xenial", "yearning", "zenith"
            ]
            
            word = random.choice(fallback_words)
            return {
                "category": "pure_random",
                "word": word,
                "context": context,
                "source": "fallback",
                "instruction": f"Use A-to-C process: Current situation (A) + '{word}' (B) → Creative solution (C)"
            }
    
    def get_inspiration(self, category: str) -> Dict[str, Any]:
        """Get random inspiration from specified category (legacy support)"""
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
        """Get random inspiration - uses pure random if no inspiration pool"""
        import random
        
        if not self.inspiration_pool:
            # Use pure random inspiration for new cases
            return self.get_pure_random_inspiration("random_inspiration")
        
        # Legacy support for cases with inspiration pools
        categories = list(self.inspiration_pool.keys())
        random_category = random.choice(categories)
        return self.get_inspiration(random_category)
    
    def get_contextual_inspiration(self) -> Dict[str, Any]:
        """Get inspiration based on current game context"""
        # For cases without inspiration pool, use pure random
        if not self.inspiration_pool:
            current_gate = self.get_next_gate() or "unknown"
            current_location = self.current_state.get("current_location", "unknown")
            context = f"gate: {current_gate}, location: {current_location}"
            return self.get_pure_random_inspiration(context)
        
        # Legacy support for cases with inspiration pools
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
        self.save_current_state_to_file()
    
    def get_inspiration_history(self) -> List[Dict[str, Any]]:
        """Get history of inspiration usage"""
        return self.current_state.get("inspiration_log", [])
    
    # Dice Rolling System Integration
    
    def roll_dice(self, modifier: int = 0, description: str = "") -> Dict[str, Any]:
        """Roll a d20 for action resolution"""
        return self.dice_roller.roll_d20(modifier, description)
    
    def make_action_check(self, 
                         action_description: str,
                         difficulty: int = 10,
                         evidence_count: int = 0,
                         character_trust: int = 0,
                         additional_modifier: int = 0) -> Dict[str, Any]:
        """
        Make an action check with contextual modifiers.
        
        Args:
            action_description: What the player is trying to do
            difficulty: Target difficulty (1-20, default 10)
            evidence_count: Number of relevant evidence pieces
            character_trust: Trust level with relevant character (-10 to +10)
            additional_modifier: Any additional situation modifiers
            
        Returns:
            Dict with roll result and success information
        """
        # Calculate total modifier
        total_modifier = additional_modifier
        total_modifier += self.dice_roller.get_evidence_modifier(evidence_count)
        total_modifier += self.dice_roller.get_trust_modifier(character_trust)
        
        # Make the skill check
        result = self.dice_roller.make_skill_check(
            target_difficulty=difficulty,
            modifier=total_modifier,
            description=action_description
        )
        
        # Add contextual information
        result["modifiers"] = {
            "evidence_bonus": self.dice_roller.get_evidence_modifier(evidence_count),
            "trust_bonus": self.dice_roller.get_trust_modifier(character_trust),
            "additional": additional_modifier,
            "total": total_modifier
        }
        
        return result
    
    def get_difficulty_for_action(self, action_type: str) -> int:
        """Get recommended difficulty for common action types"""
        difficulties = {
            "casual_conversation": 5,
            "witness_interview": 8,
            "evidence_examination": 10,
            "confrontation": 12,
            "hostile_questioning": 15,
            "convincing_judge": 16,
            "accessing_restricted_area": 18,
            "getting_confession": 20
        }
        return difficulties.get(action_type, 10)
    
    def get_recent_dice_rolls(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent dice roll history"""
        return self.dice_roller.get_recent_rolls(count)
    
    def must_use_inspiration(self, context: str) -> Dict[str, Any]:
        """FORCING FUNCTION: Must use inspiration for off-script responses"""
        # Always use pure random for new cases without inspiration pools
        if not self.inspiration_pool:
            inspiration = self.get_pure_random_inspiration(context)
        else:
            # Legacy support for cases with inspiration pools
            inspiration = self.get_contextual_inspiration()
        
        if "error" not in inspiration:
            self.log_inspiration_usage(inspiration, context)
        return inspiration
    
    # Cross-Examination System
    
    def load_trial_statements(self, witness_name: str = None) -> Dict[str, Any]:
        """Load trial statements for cross-examination"""
        statements_file = self.case_path / "game_state" / "trial_statements.json"
        
        if not statements_file.exists():
            return {"error": "No trial statements file found"}
        
        with open(statements_file, 'r') as f:
            statements_data = json.load(f)
        
        if witness_name:
            # Look for specific witness cross-examination
            witness_key = f"{witness_name.lower().replace(' ', '_')}_cross_exam"
            if witness_key in statements_data:
                return statements_data[witness_key]
            else:
                return {"error": f"No cross-examination found for {witness_name}"}
        
        return statements_data
    
    def start_cross_examination(self, witness_name: str) -> Dict[str, Any]:
        """Start cross-examination of a specific witness"""
        cross_exam_data = self.load_trial_statements(witness_name)
        
        if "error" in cross_exam_data:
            return cross_exam_data
        
        # Update trial state
        self.trial_state["current_witness"] = witness_name
        self.trial_state["trial_phase"] = "cross_examination"
        self.trial_state["current_cross_exam"] = {
            "witness": witness_name,
            "statements_presented": [],
            "evidence_presented": [],
            "successful_contradictions": 0,
            "failed_presentations": 0,
            "statements_pressed": [],
            "penalty_count": 0,
            "game_over": False
        }
        
        self.save_trial_state_to_file()
        
        return {
            "success": True,
            "witness": witness_name,
            "statements": cross_exam_data["statements"],
            "message": f"Cross-examination of {witness_name} begins!"
        }
    
    def press_statement(self, statement_id: str) -> Dict[str, Any]:
        """Press a witness for more details on a statement"""
        current_exam = self.trial_state.get("current_cross_exam")
        if not current_exam:
            return {"error": "No cross-examination in progress"}
        
        witness_name = current_exam["witness"]
        cross_exam_data = self.load_trial_statements(witness_name)
        
        if "error" in cross_exam_data:
            return cross_exam_data
        
        # Find the statement
        statement = None
        for stmt in cross_exam_data["statements"]:
            if stmt["id"] == statement_id:
                statement = stmt
                break
        
        if not statement:
            return {"error": f"Statement {statement_id} not found"}
        
        # Record that this statement was pressed
        if statement_id not in current_exam["statements_pressed"]:
            current_exam["statements_pressed"].append(statement_id)
            self.trial_state["current_cross_exam"] = current_exam
            self.save_trial_state_to_file()
        
        # Use pre-written response if available, otherwise generate subtle clarification response
        base_response = statement.get("press_response", "")
        if not base_response:
            # Press responses should be information-only, not dramatic revelations
            clarification_context = f"witness clarifying details about {statement['text'][:50]}..."
            dynamic_response = self.generate_press_clarification(clarification_context)
        else:
            dynamic_response = base_response
        
        return {
            "success": True,
            "statement_id": statement_id,
            "response": dynamic_response,
            "statement_text": statement["text"]
        }
    
    def get_hint(self, statement_id: str = None) -> Dict[str, Any]:
        """Get context-aware hint for current cross-examination"""
        current_exam = self.trial_state.get("current_cross_exam")
        if not current_exam:
            return {"error": "No cross-examination in progress"}
        
        witness_name = current_exam["witness"]
        cross_exam_data = self.load_trial_statements(witness_name)
        
        if "error" in cross_exam_data:
            return cross_exam_data
        
        # If specific statement requested, provide targeted hint
        if statement_id:
            for stmt in cross_exam_data["statements"]:
                if stmt["id"] == statement_id:
                    if stmt.get("is_lie", False):
                        contradicting_evidence = stmt.get("contradicting_evidence", [])
                        if contradicting_evidence:
                            hint_text = f"This statement seems suspicious. Try examining evidence related to: {', '.join(contradicting_evidence)}"
                        else:
                            hint_text = "This statement contradicts something we know about the case."
                    else:
                        hint_text = "This statement appears to be truthful. Consider pressing for more details or focus on other statements."
                    
                    return {
                        "hint_type": "statement_specific",
                        "statement_id": statement_id,
                        "hint_text": hint_text,
                        "statement_text": stmt["text"]
                    }
            
            return {"error": f"Statement {statement_id} not found"}
        
        # General hints based on current progress
        successful_contradictions = current_exam["successful_contradictions"]
        failed_presentations = current_exam["failed_presentations"]
        penalty_count = current_exam.get("penalty_count", 0)
        
        # Analyze what's been tried
        evidence_presented = [ep["evidence_name"] for ep in current_exam["evidence_presented"]]
        statements_pressed = current_exam.get("statements_pressed", [])
        
        # Find statements that are lies but haven't been contradicted yet
        unchallenged_lies = []
        for stmt in cross_exam_data["statements"]:
            if stmt.get("is_lie", False):
                stmt_contradicted = any(
                    ep["statement_id"] == stmt["id"] and ep["success"] 
                    for ep in current_exam["evidence_presented"]
                )
                if not stmt_contradicted:
                    unchallenged_lies.append(stmt)
        
        # Generate contextual hint
        if penalty_count >= 3:
            hint_text = "⚠️ You're accumulating penalties. Try pressing statements for more information before presenting evidence."
        elif failed_presentations > successful_contradictions:
            hint_text = "💡 Consider focusing on the contradictions in the witness's story rather than trying random evidence."
        elif len(statements_pressed) < 2:
            hint_text = "💭 Try pressing some statements first to gather more information before presenting evidence."
        elif unchallenged_lies:
            target_stmt = unchallenged_lies[0]
            hint_text = f"🎯 Statement {target_stmt['id']} looks suspicious. What evidence might contradict it?"
        else:
            victory_status = self.check_cross_examination_victory()
            if victory_status.get('victory_achieved', False):
                hint_text = "🏆 You've achieved victory conditions! Consider ending the cross-examination."
            else:
                hint_text = "🔍 Keep looking for contradictions in the witness's testimony."
        
        return {
            "hint_type": "general",
            "hint_text": hint_text,
            "progress_info": {
                "successful_contradictions": successful_contradictions,
                "failed_presentations": failed_presentations,
                "penalty_count": penalty_count,
                "statements_pressed": len(statements_pressed),
                "unchallenged_lies": len(unchallenged_lies)
            }
        }
    
    def apply_penalty(self, witness_name: str) -> Dict[str, Any]:
        """Apply penalty for wrong evidence presentation"""
        current_exam = self.trial_state.get("current_cross_exam")
        if not current_exam:
            return {"error": "No cross-examination in progress"}
        
        cross_exam_data = self.load_trial_statements(witness_name)
        if "error" in cross_exam_data:
            return cross_exam_data
        
        penalty_system = cross_exam_data.get("penalty_system", {})
        if not penalty_system.get("enabled", False):
            return {"penalty_applied": False}
        
        # Increment penalty count
        current_exam["penalty_count"] += 1
        penalty_count = current_exam["penalty_count"]
        max_penalties = penalty_system.get("max_wrong_presentations", 5)
        
        # Check if game over
        if penalty_count >= max_penalties:
            current_exam["game_over"] = True
            self.trial_state["current_cross_exam"] = current_exam
            self.save_trial_state_to_file()
            
            failure_message = penalty_system.get("failure_consequences", {}).get(
                "max_penalties_reached", 
                "GAME OVER: Too many wrong evidence presentations!"
            )
            
            return {
                "penalty_applied": True,
                "penalty_count": penalty_count,
                "max_penalties": max_penalties,
                "game_over": True,
                "penalty_message": failure_message
            }
        
        # Apply penalty effect based on count
        penalty_effects = penalty_system.get("penalty_effects", {})
        penalty_message = ""
        
        if penalty_count <= 2:
            penalty_message = penalty_effects.get("1-2", "The judge looks disapproving")
        elif penalty_count <= 4:
            penalty_message = penalty_effects.get("3-4", "The prosecutor objects and the judge sustains")
        else:
            penalty_message = penalty_effects.get("5+", "The judge threatens contempt of court")
        
        # Generate dynamic penalty response
        dynamic_penalty = self.generate_dramatic_response(
            f"penalty {penalty_count} for wrong evidence presentation", 
            "judge_reaction"
        )
        
        self.trial_state["current_cross_exam"] = current_exam
        self.save_trial_state_to_file()
        
        return {
            "penalty_applied": True,
            "penalty_count": penalty_count,
            "max_penalties": max_penalties,
            "game_over": False,
            "penalty_message": penalty_message,
            "dynamic_penalty": dynamic_penalty
        }
    
    def generate_dramatic_response(self, context: str, response_type: str = "success") -> str:
        """Generate dynamic dramatic response using forcing function"""
        try:
            inspiration = self.get_forced_inspiration(f"trial {response_type} response: {context}")
            
            if "error" in inspiration:
                # Fallback to default responses
                if response_type == "success":
                    return "OBJECTION! The witness's statement has been contradicted!"
                elif response_type == "failure":
                    return "That evidence doesn't contradict the witness's statement."
                elif response_type == "press":
                    return "The witness has nothing more to add."
                else:
                    return "The courtroom waits in tense silence..."
            
            # Use the forced inspiration word to generate unique response
            forced_word = inspiration.get("word", "tension")
            
            # Generate contextual dramatic response based on forced word
            if response_type == "success":
                return f"OBJECTION! Like a {forced_word} cutting through deception, the evidence reveals the truth! {context}"
            elif response_type == "failure":
                return f"The evidence sits like a {forced_word} in the courtroom - present, but ineffective against this testimony."
            elif response_type == "press":
                return f"The witness's expression shows {forced_word} as they elaborate on their statement."
            elif response_type == "judge_reaction":
                return f"The judge's expression reflects {forced_word} as the courtroom drama unfolds."
            elif response_type == "prosecutor_objection":
                return f"The prosecutor rises with {forced_word}, objecting to this line of questioning!"
            else:
                return f"The courtroom atmosphere fills with {forced_word} as the trial continues."
                
        except Exception as e:
            # Fallback for any errors
            return "The courtroom holds its breath as the evidence is presented."
    
    def generate_press_clarification(self, context: str) -> str:
        """Generate subtle clarification response for press actions (information-only)"""
        # Press actions should provide clarifying details, not dramatic revelations
        # These are meant to give the player more information to work with
        clarification_templates = [
            "The witness elaborates: ",
            "Upon further questioning, the witness adds: ",
            "The witness clarifies their statement: ",
            "When pressed for details, the witness explains: ",
            "The witness provides additional information: "
        ]
        
        import random
        template = random.choice(clarification_templates)
        return f"{template}Details emerge that may be useful for your investigation."
    
    def generate_objection_moment(self, statement_id: str, evidence_name: str, statement_text: str) -> str:
        """Generate authentic Ace Attorney style OBJECTION moment"""
        try:
            # Get forced inspiration for unique objection style
            inspiration = self.get_forced_inspiration(
                f"dramatic courtroom objection moment presenting {evidence_name} against witness statement"
            )
            
            if "error" in inspiration:
                forced_word = "lightning"
            else:
                forced_word = inspiration.get("word", "lightning")
            
            # Create dramatic OBJECTION with forced word for uniqueness
            objection_intro = f"**OBJECTION!**\n\n*You slam your hand on the defense table with the force of {forced_word}*"
            
            evidence_presentation = f"**This {evidence_name} directly contradicts the witness's testimony!**"
            
            contradiction_explanation = (
                f"The witness claims: '{statement_text[:80]}...'\n\n"
                f"But {evidence_name} proves otherwise! "
                f"Like {forced_word} cutting through deception, this evidence reveals the truth!"
            )
            
            return f"{objection_intro}\n\n{evidence_presentation}\n\n{contradiction_explanation}"
            
        except Exception as e:
            # Fallback objection
            return (
                f"**OBJECTION!**\n\n"
                f"This {evidence_name} contradicts the witness's statement!\n\n"
                f"The truth has been revealed!"
            )
    
    def present_evidence_against_statement(self, statement_id: str, evidence_name: str) -> Dict[str, Any]:
        """Present evidence to contradict a witness statement"""
        current_exam = self.trial_state.get("current_cross_exam")
        if not current_exam:
            return {"error": "No cross-examination in progress"}
        
        witness_name = current_exam["witness"]
        cross_exam_data = self.load_trial_statements(witness_name)
        
        if "error" in cross_exam_data:
            return cross_exam_data
        
        # Find the statement
        statement = None
        for stmt in cross_exam_data["statements"]:
            if stmt["id"] == statement_id:
                statement = stmt
                break
        
        if not statement:
            return {"error": f"Statement {statement_id} not found"}
        
        # Check if evidence exists in our case
        evidence_list = self.current_state.get("evidence_collected", [])
        evidence_exists = any(e["name"] == evidence_name for e in evidence_list)
        
        if not evidence_exists:
            return {"error": f"Evidence '{evidence_name}' not found in your case file"}
        
        # Check if this evidence contradicts the statement
        contradicting_evidence = statement.get("contradicting_evidence", [])
        
        # Record the presentation attempt
        presentation_record = {
            "statement_id": statement_id,
            "evidence_name": evidence_name,
            "success": evidence_name in contradicting_evidence
        }
        
        current_exam["evidence_presented"].append(presentation_record)
        
        if evidence_name in contradicting_evidence:
            # Success!
            current_exam["successful_contradictions"] += 1
            self.trial_state["current_cross_exam"] = current_exam
            self.save_trial_state_to_file()
            
            # Generate authentic OBJECTION moment
            base_response = statement.get("success_response", "")
            if not base_response:
                objection_response = self.generate_objection_moment(
                    statement_id, evidence_name, statement['text']
                )
            else:
                objection_response = base_response
            
            # Add judge reaction for extra drama
            judge_reaction = self.generate_dramatic_response(
                f"successful objection with {evidence_name}", 
                "judge_reaction"
            )
            
            return {
                "success": True,
                "contradiction_found": True,
                "statement_id": statement_id,
                "evidence_name": evidence_name,
                "response": objection_response,
                "judge_reaction": judge_reaction,
                "statement_text": statement["text"]
            }
        else:
            # Failure - apply penalty system
            current_exam["failed_presentations"] += 1
            self.trial_state["current_cross_exam"] = current_exam
            self.save_trial_state_to_file()
            
            # Apply penalty for wrong evidence presentation
            penalty_result = self.apply_penalty(witness_name)
            
            # Check if game over due to penalties
            if penalty_result.get("game_over", False):
                return {
                    "success": False,
                    "contradiction_found": False,
                    "statement_id": statement_id,
                    "evidence_name": evidence_name,
                    "response": penalty_result["penalty_message"],
                    "game_over": True,
                    "penalty_count": penalty_result["penalty_count"],
                    "statement_text": statement["text"]
                }
            
            # Use pre-written response if available, otherwise generate dynamic response
            base_response = statement.get("failure_response", "")
            if not base_response:
                dynamic_response = self.generate_dramatic_response(
                    f"evidence {evidence_name} fails against statement", 
                    "failure"
                )
            else:
                dynamic_response = base_response
            
            # Add prosecutor reaction for extra drama
            prosecutor_reaction = self.generate_dramatic_response(
                f"defense fails with {evidence_name}", 
                "prosecutor_objection"
            )
            
            response_data = {
                "success": False,
                "contradiction_found": False,
                "statement_id": statement_id,
                "evidence_name": evidence_name,
                "response": dynamic_response,
                "prosecutor_reaction": prosecutor_reaction,
                "statement_text": statement["text"]
            }
            
            # Add penalty information if penalties are enabled
            if penalty_result.get("penalty_applied", False):
                response_data["penalty_applied"] = True
                response_data["penalty_count"] = penalty_result["penalty_count"]
                response_data["max_penalties"] = penalty_result["max_penalties"]
                response_data["penalty_message"] = penalty_result["penalty_message"]
                if "dynamic_penalty" in penalty_result:
                    response_data["penalty_reaction"] = penalty_result["dynamic_penalty"]
            
            return response_data
    
    def present_evidence_combination(self, statement_id: str, evidence_names: List[str]) -> Dict[str, Any]:
        """Present multiple pieces of evidence together to create complex contradictions"""
        current_exam = self.trial_state.get("current_cross_exam")
        if not current_exam:
            return {"error": "No cross-examination in progress"}
        
        witness_name = current_exam["witness"]
        cross_exam_data = self.load_trial_statements(witness_name)
        
        if "error" in cross_exam_data:
            return cross_exam_data
        
        # Find the statement
        statement = None
        for stmt in cross_exam_data["statements"]:
            if stmt["id"] == statement_id:
                statement = stmt
                break
        
        if not statement:
            return {"error": f"Statement {statement_id} not found"}
        
        # Check if all evidence exists
        evidence_list = self.current_state.get("evidence_collected", [])
        for evidence_name in evidence_names:
            if not any(e["name"] == evidence_name for e in evidence_list):
                return {"error": f"Evidence '{evidence_name}' not found in your case file"}
        
        # Check for evidence combinations in statement metadata
        evidence_combinations = statement.get("evidence_combinations", [])
        
        # Look for matching combination
        matching_combination = None
        for combo in evidence_combinations:
            required_evidence = set(combo.get("required_evidence", []))
            provided_evidence = set(evidence_names)
            
            if required_evidence.issubset(provided_evidence):
                matching_combination = combo
                break
        
        # If no specific combination found, check if all evidence individually contradicts
        if not matching_combination:
            contradicting_evidence = statement.get("contradicting_evidence", [])
            individual_matches = [e for e in evidence_names if e in contradicting_evidence]
            
            if len(individual_matches) >= 2:  # Multiple individual pieces
                # Create dynamic combination response
                dynamic_response = self.generate_dramatic_response(
                    f"multiple evidence pieces {', '.join(individual_matches)} against statement",
                    "success"
                )
                
                combination_response = f"OBJECTION! Multiple pieces of evidence contradict this testimony: {', '.join(individual_matches)}!"
                if not any("OBJECTION!" in dynamic_response for _ in [1]):  # Check if already has objection
                    combination_response = dynamic_response
                
                # Record successful combination
                current_exam["successful_contradictions"] += 1
                current_exam["evidence_presented"].append({
                    "statement_id": statement_id,
                    "evidence_combination": evidence_names,
                    "success": True,
                    "combination_type": "multiple_individual"
                })
                
                self.trial_state["current_cross_exam"] = current_exam
                self.save_trial_state_to_file()
                
                return {
                    "success": True,
                    "contradiction_found": True,
                    "combination_used": True,
                    "evidence_combination": evidence_names,
                    "statement_id": statement_id,
                    "response": combination_response,
                    "combination_type": "multiple_individual",
                    "statement_text": statement["text"]
                }
        
        # Use specific combination if found
        if matching_combination:
            current_exam["successful_contradictions"] += 1
            current_exam["evidence_presented"].append({
                "statement_id": statement_id,
                "evidence_combination": evidence_names,
                "success": True,
                "combination_type": "designed_combination"
            })
            
            self.trial_state["current_cross_exam"] = current_exam
            self.save_trial_state_to_file()
            
            combination_response = matching_combination.get(
                "success_response", 
                f"OBJECTION! The combination of {', '.join(evidence_names)} completely undermines this testimony!"
            )
            
            return {
                "success": True,
                "contradiction_found": True,
                "combination_used": True,
                "evidence_combination": evidence_names,
                "statement_id": statement_id,
                "response": combination_response,
                "combination_type": "designed_combination",
                "statement_text": statement["text"]
            }
        
        # No valid combination found
        current_exam["failed_presentations"] += 1
        self.trial_state["current_cross_exam"] = current_exam
        
        # Apply penalty for failed combination
        penalty_result = self.apply_penalty(witness_name)
        
        if penalty_result.get("game_over", False):
            return {
                "success": False,
                "contradiction_found": False,
                "combination_used": True,
                "evidence_combination": evidence_names,
                "statement_id": statement_id,
                "response": penalty_result["penalty_message"],
                "game_over": True,
                "statement_text": statement["text"]
            }
        
        failure_response = f"Those pieces of evidence don't work together to contradict this statement."
        
        response_data = {
            "success": False,
            "contradiction_found": False,
            "combination_used": True,
            "evidence_combination": evidence_names,
            "statement_id": statement_id,
            "response": failure_response,
            "statement_text": statement["text"]
        }
        
        # Add penalty information
        if penalty_result.get("penalty_applied", False):
            response_data["penalty_applied"] = True
            response_data["penalty_count"] = penalty_result["penalty_count"]
            response_data["penalty_message"] = penalty_result["penalty_message"]
        
        return response_data
    
    def generate_trial_statements_from_backbone(self, witness_name: str) -> Dict[str, Any]:
        """Generate cross-examination statements dynamically from backbone files"""
        
        # Check if this is a simple improvisation case
        if self.case_type == "simple_improvisation":
            return {"error": "This case doesn't have backbone files for dynamic generation"}
        
        # Load backbone files
        try:
            character_facts_file = self.case_path / "backbone" / "character_facts.json"
            witness_testimonies_file = self.case_path / "backbone" / "witness_testimonies.json"
            evidence_chain_file = self.case_path / "backbone" / "evidence_chain.json"
            
            if not all([character_facts_file.exists(), witness_testimonies_file.exists(), evidence_chain_file.exists()]):
                return {"error": "Missing backbone files required for dynamic generation"}
            
            with open(character_facts_file, 'r') as f:
                character_facts = json.load(f)
            with open(witness_testimonies_file, 'r') as f:
                witness_testimonies = json.load(f)
            with open(evidence_chain_file, 'r') as f:
                evidence_chain = json.load(f)
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return {"error": f"Failed to load backbone files: {e}"}
        
        # Find witness in testimonies
        witness_testimony = None
        for testimony in witness_testimonies.get("true_testimonies_before_fabrication", []):
            if testimony["witness"].lower() == witness_name.lower():
                witness_testimony = testimony
                break
        
        if not witness_testimony:
            return {"error": f"No testimony found for {witness_name} in backbone files"}
        
        # Find character facts for this witness
        character_data = None
        for char in character_facts.get("characters", []):
            if witness_name.lower() in char["name"].lower():
                character_data = char
                break
        
        # Extract contradictable elements and evidence
        contradictable_elements = witness_testimony.get("contradictable_elements", [])
        true_testimony = witness_testimony.get("true_testimony", "")
        evidence_pieces = evidence_chain.get("evidence_pieces", [])
        
        # Generate statements by breaking down the testimony
        statements = []
        statement_id = 'A'
        
        # Split testimony into logical chunks and create statements
        testimony_sentences = [s.strip() for s in true_testimony.split('.') if s.strip()]
        
        for i, sentence in enumerate(testimony_sentences[:5]):  # Max 5 statements (A-E)
            # Determine if this statement should be a lie based on contradictable elements
            # More sophisticated lie detection using keyword matching
            is_lie = False
            for element in contradictable_elements:
                element_lower = element.lower()
                sentence_lower = sentence.lower()
                
                # Check for key concepts that would make this statement contradictable
                if (("claims" in element_lower or "says" in element_lower or "emphasizes" in element_lower) and
                    any(keyword in sentence_lower for keyword in 
                        ["office", "files", "screaming", "coffee", "cup", "time", "death", "digitalis", "intentional"])):
                    is_lie = True
                    break
            
            # Find relevant evidence that could contradict this statement
            relevant_evidence = []
            for evidence in evidence_pieces:
                evidence_name = evidence.get("name", "")
                evidence_desc = evidence.get("description", "").lower()
                
                # Check if evidence relates to this statement
                if any(keyword in sentence.lower() for keyword in evidence_desc.split()[:3]):
                    relevant_evidence.append(evidence_name)
            
            # Generate dynamic press response based on character knowledge
            press_response = ""
            if character_data:
                hidden_knowledge = character_data.get("what_he_hides", [])
                if hidden_knowledge and is_lie:
                    press_response = f"The witness shows discomfort when pressed about this detail."
                else:
                    press_response = f"The witness provides additional details about the situation."
            else:
                press_response = "The witness has nothing more to add."
            
            statement = {
                "id": statement_id,
                "text": sentence + ".",
                "is_lie": is_lie,
                "press_response": press_response,
                "truth_level": "fabricated" if is_lie else "accurate"
            }
            
            # Add contradiction evidence if this is a lie
            if is_lie and relevant_evidence:
                statement["contradicting_evidence"] = relevant_evidence[:2]  # Max 2 pieces
                statement["success_response"] = f"OBJECTION! The evidence contradicts this testimony!"
                statement["failure_response"] = f"That evidence doesn't contradict this part of the testimony."
            
            statements.append(statement)
            statement_id = chr(ord(statement_id) + 1)
        
        # Generate victory conditions
        lies_count = sum(1 for stmt in statements if stmt.get("is_lie", False))
        critical_lies = [stmt["id"] for stmt in statements if stmt.get("is_lie", False)]
        
        victory_condition = {
            "required_contradictions": max(1, lies_count // 2),
            "critical_lies": critical_lies,
            "success_message": f"{witness_name}'s testimony has been thoroughly discredited! The contradictions are clear!"
        }
        
        # Create penalty system
        penalty_system = {
            "enabled": True,
            "max_wrong_presentations": 5,
            "penalty_effects": {
                "1-2": "The judge looks displeased with your evidence presentation",
                "3-4": "The prosecutor objects and the judge warns you about irrelevant evidence",
                "5+": "The judge threatens to hold you in contempt for wasting the court's time"
            },
            "failure_consequences": {
                "max_penalties_reached": f"GAME OVER: Your repeated irrelevant evidence presentations have undermined your case against {witness_name}!"
            }
        }
        
        # Create full cross-examination structure
        cross_exam_data = {
            "witness_name": witness_name,
            "statements": statements,
            "victory_condition": victory_condition,
            "penalty_system": penalty_system,
            "generated_from": "backbone_files",
            "source_testimony": true_testimony
        }
        
        return {
            "success": True,
            "cross_exam_data": cross_exam_data,
            "witness_name": witness_name,
            "statements_generated": len(statements),
            "lies_detected": lies_count
        }
    
    def auto_generate_trial_statements_for_case(self) -> Dict[str, Any]:
        """Auto-generate trial statements for all witnesses in a case"""
        
        if self.case_type == "simple_improvisation":
            return {"error": "Simple improvisation cases don't have backbone files for generation"}
        
        # Get available witnesses from backbone
        try:
            witness_testimonies_file = self.case_path / "backbone" / "witness_testimonies.json"
            if not witness_testimonies_file.exists():
                return {"error": "No witness testimonies file found"}
            
            with open(witness_testimonies_file, 'r') as f:
                witness_testimonies = json.load(f)
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return {"error": f"Failed to load witness testimonies: {e}"}
        
        witnesses = witness_testimonies.get("true_testimonies_before_fabrication", [])
        if not witnesses:
            return {"error": "No witnesses found in backbone files"}
        
        # Generate statements for each witness
        generated_statements = {}
        total_statements = 0
        total_lies = 0
        
        for witness_data in witnesses:
            witness_name = witness_data["witness"]
            result = self.generate_trial_statements_from_backbone(witness_name)
            
            if result.get("success", False):
                witness_key = f"{witness_name.lower().replace(' ', '_')}_cross_exam"
                generated_statements[witness_key] = result["cross_exam_data"]
                total_statements += result["statements_generated"]
                total_lies += result["lies_detected"]
        
        if not generated_statements:
            return {"error": "Failed to generate statements for any witnesses"}
        
        # Save to trial_statements.json
        statements_file = self.case_path / "game_state" / "trial_statements.json"
        
        try:
            with open(statements_file, 'w') as f:
                json.dump(generated_statements, f, indent=2)
        except Exception as e:
            return {"error": f"Failed to save trial statements: {e}"}
        
        return {
            "success": True,
            "witnesses_generated": len(generated_statements),
            "total_statements": total_statements,
            "total_lies": total_lies,
            "file_saved": str(statements_file),
            "witnesses": list(generated_statements.keys())
        }
    
    def adapt_case_for_interactive_trial(self) -> Dict[str, Any]:
        """Automatically adapt any case to support interactive trials"""
        
        adaptation_results = {
            "case_type": self.case_type,
            "adaptations_made": [],
            "warnings": [],
            "success": True
        }
        
        # Check if trial statements already exist
        statements_file = self.case_path / "game_state" / "trial_statements.json"
        if statements_file.exists():
            adaptation_results["warnings"].append("Trial statements already exist - no adaptation needed")
            return adaptation_results
        
        # Simple improvisation cases - create basic interactive structure
        if self.case_type == "simple_improvisation":
            # Create evidence based on what's been collected during investigation
            evidence_collected = self.current_state.get("evidence_collected", [])
            
            if not evidence_collected:
                adaptation_results["warnings"].append("No evidence collected yet - run investigation first")
                return adaptation_results
            
            # Create a basic witness based on the case opening or client info
            client_name = self.client_name or "Unknown Client"
            
            # Generate basic statements from evidence
            statements = []
            for i, evidence in enumerate(evidence_collected[:5]):
                statement_id = chr(ord('A') + i)
                
                # Make some statements lies based on evidence descriptions
                is_lie = "inconsistencies" in evidence["name"].lower() or "location" in evidence["name"].lower()
                
                statement = {
                    "id": statement_id,
                    "text": f"The evidence shows that {evidence['description']}.",
                    "is_lie": is_lie,
                    "press_response": "The witness provides more details about this evidence.",
                    "truth_level": "fabricated" if is_lie else "accurate"
                }
                
                if is_lie:
                    statement["contradicting_evidence"] = [evidence["name"]]
                    statement["success_response"] = f"OBJECTION! This contradicts the evidence we found!"
                    statement["failure_response"] = "That evidence doesn't contradict this statement."
                
                statements.append(statement)
            
            # Create cross-examination structure
            cross_exam_data = {
                f"prosecution_witness_cross_exam": {
                    "witness_name": "Prosecution Witness",
                    "statements": statements,
                    "victory_condition": {
                        "required_contradictions": 1,
                        "critical_lies": [stmt["id"] for stmt in statements if stmt.get("is_lie", False)],
                        "success_message": "The prosecution's case has been undermined by the evidence!"
                    },
                    "penalty_system": {
                        "enabled": True,
                        "max_wrong_presentations": 5,
                        "penalty_effects": {
                            "1-2": "The judge looks skeptical of your approach",
                            "3-4": "The prosecutor objects to your evidence presentation",
                            "5+": "The judge warns you about wasting the court's time"
                        },
                        "failure_consequences": {
                            "max_penalties_reached": "GAME OVER: Your case has been undermined by poor evidence presentation!"
                        }
                    },
                    "generated_from": "simple_case_adaptation",
                    "evidence_basis": [e["name"] for e in evidence_collected]
                }
            }
            
            # Save the generated statements
            try:
                with open(statements_file, 'w') as f:
                    json.dump(cross_exam_data, f, indent=2)
                adaptation_results["adaptations_made"].append("Created basic trial statements from investigation evidence")
            except Exception as e:
                adaptation_results["success"] = False
                adaptation_results["warnings"].append(f"Failed to save trial statements: {e}")
                return adaptation_results
        
        # Complex cases with backbone - use dynamic generation
        elif self.case_type == "complex":
            result = self.auto_generate_trial_statements_for_case()
            if result.get("success", False):
                adaptation_results["adaptations_made"].append(f"Generated statements for {result['witnesses_generated']} witnesses from backbone")
                adaptation_results["witnesses_generated"] = result["witnesses_generated"]
                adaptation_results["total_statements"] = result["total_statements"]
            else:
                adaptation_results["success"] = False
                adaptation_results["warnings"].append(result.get("error", "Failed to generate from backbone"))
                return adaptation_results
        
        # Ensure trial state is properly initialized for new format
        trial_phase = self.trial_state.get("trial_phase")
        trial_status = self.trial_state.get("trial_status") 
        
        if not trial_phase or trial_status == "not_started":
            # Update to new trial state format
            if self.case_type == "simple_improvisation":
                self.trial_state.update(self.create_simple_trial_state())
            else:
                # Update complex case trial state to new format
                self.trial_state.update({
                    "trial_phase": "not_started",
                    "current_witness": None,
                    "witnesses_examined": [],
                    "evidence_presented": [],
                    "objections_sustained": 0,
                    "objections_overruled": 0,
                    "trial_gates": {
                        "opening_statements": {"status": "pending", "completed_at": None},
                        "witness_examination": {"status": "pending", "completed_at": None},
                        "final_argument": {"status": "pending", "completed_at": None}
                    },
                    "trial_ready": True,
                    "last_updated": None
                })
                
            self.save_trial_state_to_file()
            adaptation_results["adaptations_made"].append("Updated trial state to new interactive format")
        
        # Add evidence to investigation state if not present
        evidence_collected = self.current_state.get("evidence_collected", [])
        if not evidence_collected and self.case_type == "complex":
            # Load evidence from backbone if available
            try:
                evidence_chain_file = self.case_path / "backbone" / "evidence_chain.json"
                if evidence_chain_file.exists():
                    with open(evidence_chain_file, 'r') as f:
                        evidence_chain = json.load(f)
                    
                    for evidence in evidence_chain.get("evidence_pieces", [])[:3]:  # Add first 3 pieces
                        self.add_evidence(evidence["name"], evidence["description"])
                    
                    adaptation_results["adaptations_made"].append("Added initial evidence from backbone to investigation")
            except Exception as e:
                adaptation_results["warnings"].append(f"Could not load evidence from backbone: {e}")
        
        return adaptation_results
    
    def get_trial_progress(self) -> Dict[str, Any]:
        """Get comprehensive trial progress and next actions"""
        if self.trial_state["trial_phase"] == "not_started":
            return {
                "phase": "not_started",
                "ready_for_trial": self.is_trial_ready(),
                "next_action": "start_trial" if self.is_trial_ready() else "complete_investigation"
            }
        
        # Check if we're in cross-examination
        current_exam = self.trial_state.get("current_cross_exam")
        if current_exam and not current_exam.get("game_over", False):
            witness_name = current_exam["witness"]
            victory_status = self.check_cross_examination_victory()
            
            return {
                "phase": "cross_examination",
                "current_witness": witness_name,
                "victory_achieved": victory_status.get("victory_achieved", False),
                "successful_contradictions": current_exam["successful_contradictions"],
                "penalty_count": current_exam.get("penalty_count", 0),
                "next_action": "continue_cross_examination" if not victory_status.get("victory_achieved", False) else "end_cross_examination"
            }
        
        # Determine what witnesses are available for cross-examination
        available_witnesses = self.get_available_witnesses_for_cross_examination()
        examined_witnesses = self.trial_state.get("witnesses_examined", [])
        
        if available_witnesses and len(examined_witnesses) < len(available_witnesses):
            unexamined = [w for w in available_witnesses if w not in examined_witnesses]
            return {
                "phase": "witness_examination",
                "available_witnesses": available_witnesses,
                "examined_witnesses": examined_witnesses,
                "next_witness": unexamined[0] if unexamined else None,
                "next_action": f"start_cross_examination_{unexamined[0].replace(' ', '_')}" if unexamined else "closing_arguments"
            }
        
        # All witnesses examined or no witnesses available
        return {
            "phase": "closing_arguments",
            "all_witnesses_examined": True,
            "trial_complete": True,
            "next_action": "closing_arguments"
        }
    
    def get_available_witnesses_for_cross_examination(self) -> List[str]:
        """Get list of witnesses available for cross-examination"""
        # Check if we have trial statements files
        statements_file = self.case_path / "game_state" / "trial_statements.json"
        if not statements_file.exists():
            return []
        
        with open(statements_file, 'r') as f:
            statements_data = json.load(f)
        
        # Extract witness names from cross-examination data
        witnesses = []
        for key in statements_data.keys():
            if key.endswith("_cross_exam"):
                witness_data = statements_data[key]
                witness_name = witness_data.get("witness_name", "")
                if witness_name:
                    witnesses.append(witness_name)
        
        return witnesses
    
    def suggest_next_trial_action(self) -> Dict[str, Any]:
        """Suggest the next action based on trial progress"""
        progress = self.get_trial_progress()
        
        suggestions = {
            "not_started": "Use --start-trial to begin the trial phase",
            "cross_examination": f"Continue cross-examining {progress.get('current_witness', 'the witness')} or use --end-cross-examination",
            "witness_examination": f"Start cross-examining {progress.get('next_witness', 'the next witness')}",
            "closing_arguments": "Prepare closing arguments - trial evidence phase complete"
        }
        
        suggestion = suggestions.get(progress["phase"], "Continue with trial proceedings")
        
        return {
            "phase": progress["phase"],
            "suggestion": suggestion,
            "specific_command": progress.get("next_action", ""),
            "progress_details": progress
        }
    
    def check_cross_examination_victory(self) -> Dict[str, Any]:
        """Check if cross-examination victory conditions are met"""
        current_exam = self.trial_state.get("current_cross_exam")
        if not current_exam:
            return {"error": "No cross-examination in progress"}
        
        witness_name = current_exam["witness"]
        cross_exam_data = self.load_trial_statements(witness_name)
        
        if "error" in cross_exam_data:
            return cross_exam_data
        
        victory_condition = cross_exam_data.get("victory_condition", {})
        required_contradictions = victory_condition.get("required_contradictions", 1)
        critical_lies = victory_condition.get("critical_lies", [])
        
        successful_contradictions = current_exam["successful_contradictions"]
        
        # Check if critical lies were exposed
        critical_exposed = 0
        for presentation in current_exam["evidence_presented"]:
            if presentation["success"] and presentation["statement_id"] in critical_lies:
                critical_exposed += 1
        
        victory_achieved = (
            successful_contradictions >= required_contradictions and
            critical_exposed > 0
        )
        
        return {
            "victory_achieved": victory_achieved,
            "successful_contradictions": successful_contradictions,
            "required_contradictions": required_contradictions,
            "critical_lies_exposed": critical_exposed,
            "total_critical_lies": len(critical_lies),
            "victory_message": victory_condition.get("success_message", "Cross-examination completed successfully!")
        }
    
    def end_cross_examination(self) -> Dict[str, Any]:
        """End the current cross-examination"""
        current_exam = self.trial_state.get("current_cross_exam")
        if not current_exam:
            return {"error": "No cross-examination in progress"}
        
        # Check victory status
        victory_status = self.check_cross_examination_victory()
        
        # Add to witnesses examined
        witness_name = current_exam["witness"]
        examined_witnesses = self.trial_state.get("witnesses_examined", [])
        if witness_name not in examined_witnesses:
            examined_witnesses.append(witness_name)
        
        # Update trial state
        self.trial_state["witnesses_examined"] = examined_witnesses
        self.trial_state["current_witness"] = None
        self.trial_state["trial_phase"] = "witness_examination"
        
        # Archive the cross-examination results
        cross_exam_history = self.trial_state.get("cross_examination_history", [])
        cross_exam_history.append({
            "witness": witness_name,
            "successful_contradictions": current_exam["successful_contradictions"],
            "failed_presentations": current_exam["failed_presentations"],
            "statements_pressed": current_exam["statements_pressed"],
            "victory_achieved": victory_status.get("victory_achieved", False)
        })
        
        self.trial_state["cross_examination_history"] = cross_exam_history
        self.trial_state["current_cross_exam"] = None
        
        self.save_trial_state_to_file()
        
        return {
            "success": True,
            "witness": witness_name,
            "victory_status": victory_status,
            "summary": f"Cross-examination of {witness_name} completed."
        }

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
    parser.add_argument('--show-evidence', action='store_true', help='Show all collected evidence with descriptions')
    parser.add_argument('--show-characters', action='store_true', help='Show all characters with trust levels and roles')
    parser.add_argument('--show-witnesses', action='store_true', help='Show all interviewed witnesses')
    parser.add_argument('--check-role', help='Check if specific role already exists (e.g., prosecutor, judge)')
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
    parser.add_argument('--roll', nargs='*', help='Roll dice with optional modifiers and description')
    parser.add_argument('--action-check', nargs='+', help='Make action check: action_description [difficulty] [evidence_count] [character_trust] [additional_modifier]')
    parser.add_argument('--dice-history', action='store_true', help='Show recent dice roll history')
    parser.add_argument('--client-name', action='store_true', help='Show client name for dialogue substitution')
    parser.add_argument('--generate-name', nargs='?', const='', help='Generate unique character name (optional role hint)')
    parser.add_argument('--generate-names', type=int, metavar='COUNT', help='Generate multiple unique character names')
    parser.add_argument('--generate-name-personality', nargs='?', const='', help='Generate unique character name with personality trait (optional role hint)')
    parser.add_argument('--generate-personality', action='store_true', help='Generate random personality trait')
    parser.add_argument('--name-suggestions', help='Get character name suggestions based on description')
    parser.add_argument('--create-family', type=int, metavar='SIZE', help='Create entire family of specified size')
    parser.add_argument('--family-surname', help='Specific surname for family creation')
    parser.add_argument('--add-family-member', help='Add family member to existing character (format: "existing_name:relationship")')
    parser.add_argument('--surname-suggestions', nargs='+', help='Get surname suggestions avoiding these existing names')
    
    # Red herring system commands
    parser.add_argument('--classify-character', nargs='+', metavar='ARG', help='Classify character: CHARACTER_NAME CASE_LENGTH [ROLE_HINT] (optional role hint for weighting)')
    parser.add_argument('--check-character-role', metavar='CHARACTER_NAME', help='Check existing character classification')
    parser.add_argument('--list-classifications', action='store_true', help='List all character classifications for GM reference')
    parser.add_argument('--classification-stats', action='store_true', help='Show classification statistics for current case')
    parser.add_argument('--generate-name-classified', nargs='?', const='', help='Generate name with automatic classification (optional role hint)')
    parser.add_argument('--generate-age', nargs='?', const='', help='Generate appropriate age for role (optional role hint)')
    parser.add_argument('--generate-occupation', nargs=2, metavar=('AGE', 'ROLE'), help='Generate occupation for given age and role')
    parser.add_argument('--show-spoilers', action='store_true', help='Show character classifications and killer identities (for testing/GM reference only)')
    parser.add_argument('--reveal-classification', metavar='CHARACTER_NAME', help='Reveal character classification at narrative climax point')
    parser.add_argument('--check-killer-status', action='store_true', help='Check if true killer character has been generated yet')
    parser.add_argument('--remove-character', metavar='CHARACTER_NAME', help='Remove character from classification system')
    
    # Murder escalation commands
    parser.add_argument('--check-escalation-status', action='store_true', help='Show murder escalation status and probabilities')
    parser.add_argument('--force-escalation', action='store_true', help='Force murder escalation at current gate (GM override)')
    parser.add_argument('--escalation-narrative', help='Get escalation narrative for specific crime type')
    
    # Cross-examination commands
    parser.add_argument('--start-cross-examination', metavar='WITNESS_NAME', help='Start cross-examination of specified witness')
    parser.add_argument('--press', metavar='STATEMENT_ID', help='Press witness for more details on statement (A, B, C, etc.)')
    parser.add_argument('--present', nargs=2, metavar=('STATEMENT_ID', 'EVIDENCE_NAME'), help='Present evidence against statement')
    parser.add_argument('--check-victory', action='store_true', help='Check cross-examination victory status')
    parser.add_argument('--end-cross-examination', action='store_true', help='End current cross-examination')
    parser.add_argument('--show-statements', action='store_true', help='Show current witness statements')
    parser.add_argument('--hint', nargs='?', const='', metavar='STATEMENT_ID', help='Get hint for cross-examination (optional statement ID for specific hint)')
    parser.add_argument('--trial-status', action='store_true', help='Show comprehensive trial progress and next actions')
    parser.add_argument('--generate-trial-statements', action='store_true', help='Auto-generate trial statements from backbone files')
    parser.add_argument('--generate-witness-statements', metavar='WITNESS_NAME', help='Generate statements for specific witness from backbone')
    parser.add_argument('--present-combination', nargs='+', help='Present multiple evidence pieces together against statement (format: STATEMENT_ID EVIDENCE1 EVIDENCE2 ...)')
    parser.add_argument('--adapt-case', action='store_true', help='Automatically adapt case for interactive trials')
    
    # Enhanced narrative save system commands
    parser.add_argument('--create-narrative-save', help='Create narrative save for current gate')
    parser.add_argument('--restore-narrative', help='Restore narrative context from save file')
    parser.add_argument('--list-narrative-saves', action='store_true', help='List all narrative saves')
    parser.add_argument('--narrative-summary', help='Generate context summary from narrative save')
    
    # Context validation commands
    parser.add_argument('--validate-action', help='Validate if action is appropriate for current state')
    parser.add_argument('--context-violation', action='store_true', help='Handle context violation')
    
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
            
            # Murder escalation status
            escalation = status['murder_escalation']
            print(f"\nMurder Escalation:")
            print(f"  Original Crime: {escalation['original_crime'].title()}")
            print(f"  Is Murder Case: {'Yes' if escalation['is_murder_case'] else 'No'}")
            if escalation['escalated']:
                print(f"  🚨 ESCALATED at gate: {escalation['escalation_gate']}")
            elif escalation['original_crime'] != 'murder':
                print(f"  Gates Checked: {escalation['gates_checked']}")
                remaining = escalation['remaining_gates']
                if remaining:
                    print(f"  Remaining Gates: {remaining}")
                    if escalation['final_gate_mandatory'] in remaining:
                        print(f"  ⚠️  Mandatory escalation at: {escalation['final_gate_mandatory']}")
            
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
        
        if args.show_evidence:
            evidence_list = manager.current_state.get("evidence_collected", [])
            print(f"\n=== Evidence Collected ===")
            if not evidence_list:
                print("No evidence collected yet.")
            else:
                for i, evidence in enumerate(evidence_list, 1):
                    print(f"{i}. {evidence['name']}")
                    print(f"   Description: {evidence['description']}")
                    print(f"   Discovered at: {evidence.get('discovered_at', 'Unknown location')}")
                    print()
        
        if args.show_characters:
            trust_levels = manager.current_state.get("character_trust_levels", {})
            character_facts = manager.current_state.get("character_facts", {})
            witnesses = manager.current_state.get("witnesses_interviewed", [])
            
            # Get character names from the name generator system
            used_names_file = manager.case_path / "game_state" / "used_character_names.json"
            used_names = {}
            if used_names_file.exists():
                with open(used_names_file, 'r') as f:
                    data = json.load(f)
                    # Handle case where file contains list instead of dict
                    used_names = data if isinstance(data, dict) else {}
            
            all_characters = set()
            all_characters.update(trust_levels.keys())
            all_characters.update(character_facts.keys())
            all_characters.update(witnesses)
            all_characters.update(used_names.keys())
            
            print(f"\n=== Characters in Case ===")
            if not all_characters:
                print("No characters introduced yet.")
            else:
                for i, character in enumerate(sorted(all_characters), 1):
                    print(f"{i}. {character}")
                    
                    # Show comprehensive character information from character_facts
                    if character in character_facts:
                        facts = character_facts[character]
                        if isinstance(facts, dict):
                            # Display structured character information
                            if 'age' in facts:
                                print(f"   📅 Age: {facts['age']}")
                            if 'occupation' in facts:
                                print(f"   💼 Occupation: {facts['occupation']}")
                            if 'personality' in facts:
                                print(f"   🎭 Personality: {facts['personality']}")
                            if 'role_hint' in facts and facts['role_hint']:
                                print(f"   🎪 Role: {facts['role_hint']}")
                            
                            # Show any other character details
                            for key, value in facts.items():
                                if key not in ['age', 'occupation', 'personality', 'role_hint', 'generated_at']:
                                    print(f"   {key.title()}: {value}")
                        else:
                            print(f"   Details: {facts}")
                    
                    # Show trust level if available
                    if character in trust_levels:
                        trust = trust_levels[character]
                        trust_emoji = "😊" if trust > 0 else "😐" if trust == 0 else "😠"
                        print(f"   💝 Trust Level: {trust} {trust_emoji}")
                    
                    # Show if interviewed
                    if character in witnesses:
                        print(f"   📝 Status: ✅ Interviewed")
                    else:
                        print(f"   📝 Status: Not interviewed")
                    
                    # Show character generation info from used_names if not in character_facts
                    if character not in character_facts and character in used_names:
                        name_info = used_names[character]
                        if isinstance(name_info, dict):
                            if 'role' in name_info:
                                print(f"   🎪 Role: {name_info['role']}")
                            if 'age' in name_info:
                                print(f"   📅 Age: {name_info['age']}")
                            if 'occupation' in name_info:
                                print(f"   💼 Occupation: {name_info['occupation']}")
                            if 'personality' in name_info:
                                print(f"   🎭 Personality: {name_info['personality']}")
                    
                    print()
        
        if args.show_witnesses:
            witnesses = manager.current_state.get("witnesses_interviewed", [])
            trust_levels = manager.current_state.get("character_trust_levels", {})
            
            print(f"\n=== Interviewed Witnesses ===")
            if not witnesses:
                print("No witnesses interviewed yet.")
            else:
                for i, witness in enumerate(witnesses, 1):
                    print(f"{i}. {witness}")
                    if witness in trust_levels:
                        trust = trust_levels[witness]
                        trust_emoji = "😊" if trust > 0 else "😐" if trust == 0 else "😠"
                        print(f"   Trust Level: {trust} {trust_emoji}")
                    print()
        
        if args.check_role:
            role_to_check = args.check_role.lower()
            character_facts = manager.current_state.get("character_facts", {})
            
            print(f"\n=== Role Check: {args.check_role} ===")
            
            matching_characters = []
            
            # Check character_facts for role matches
            for character, facts in character_facts.items():
                if isinstance(facts, dict):
                    # Check occupation field
                    if 'occupation' in facts and facts['occupation']:
                        if role_to_check in facts['occupation'].lower():
                            matching_characters.append((character, facts, 'occupation'))
                    
                    # Check role_hint field
                    if 'role_hint' in facts and facts['role_hint']:
                        if role_to_check in facts['role_hint'].lower():
                            matching_characters.append((character, facts, 'role_hint'))
            
            # Also check used_names file as fallback
            used_names_file = manager.case_path / "game_state" / "used_character_names.json"
            if used_names_file.exists():
                with open(used_names_file, 'r') as f:
                    data = json.load(f)
                    # Handle case where file contains list instead of dict
                    used_names = data if isinstance(data, dict) else {}
                
                for character, info in used_names.items():
                    if isinstance(info, dict) and 'role' in info:
                        if role_to_check in info['role'].lower():
                            matching_characters.append((character, info, 'role'))
            
            if matching_characters:
                print(f"⚠️  Found existing {args.check_role}(s):")
                for character, info, source_field in matching_characters:
                    if source_field == 'occupation':
                        print(f"   • {character} (Occupation: {info.get('occupation', 'Unknown')})")
                    elif source_field == 'role_hint':
                        print(f"   • {character} (Role: {info.get('role_hint', 'Unknown')})")
                    else:
                        print(f"   • {character} (Role: {info.get('role', 'Unknown')})")
                    
                    # Show additional details
                    if 'age' in info:
                        print(f"     Age: {info['age']}")
                    if 'personality' in info:
                        print(f"     Personality: {info['personality']}")
                
                print(f"\n💡 Consider using existing character(s) instead of creating new {args.check_role}")
            else:
                print(f"✅ No existing {args.check_role} found. Safe to create new character with this role.")
        
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
        
        # Cross-examination command handlers
        if args.start_cross_examination:
            result = manager.start_cross_examination(args.start_cross_examination)
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"⚖️  {result['message']}")
                print(f"\n=== CROSS-EXAMINATION: {result['witness']} ===")
                for stmt in result['statements']:
                    print(f"{stmt['id']}. {stmt['text']}")
                print(f"\nCommands: press [A-E] | present [A-E] [evidence_name] | check-victory | end-cross-examination")
        
        if args.press:
            result = manager.press_statement(args.press.upper())
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"💬 PRESS: {result['statement_text']}")
                print(f"👤 WITNESS: {result['response']}")
        
        if args.present:
            statement_id, evidence_name = args.present
            result = manager.present_evidence_against_statement(statement_id.upper(), evidence_name)
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"📋 PRESENT: {evidence_name} against statement {statement_id.upper()}")
                print(f"📜 STATEMENT: {result['statement_text']}")
                if result['contradiction_found']:
                    print(f"🎯 {result['response']}")
                    if 'judge_reaction' in result:
                        print(f"⚖️  JUDGE: {result['judge_reaction']}")
                else:
                    if result.get('game_over', False):
                        print(f"💀 GAME OVER: {result['response']}")
                        print(f"⚠️  Total Penalties: {result['penalty_count']}")
                        return 1  # Exit with error code for game over
                    else:
                        print(f"❌ {result['response']}")
                        if 'prosecutor_reaction' in result:
                            print(f"👨‍💼 PROSECUTOR: {result['prosecutor_reaction']}")
                        
                        # Show penalty information if applied
                        if result.get('penalty_applied', False):
                            print(f"⚠️  PENALTY: {result['penalty_message']}")
                            print(f"📊 Penalty Count: {result['penalty_count']}/{result['max_penalties']}")
                            if 'penalty_reaction' in result:
                                print(f"⚖️  JUDGE: {result['penalty_reaction']}")
        
        if args.present_combination:
            if len(args.present_combination) < 3:
                print("❌ Evidence combination requires: statement_id evidence1 evidence2 [evidence3...]")
            else:
                statement_id = args.present_combination[0].upper()
                evidence_names = args.present_combination[1:]
                
                result = manager.present_evidence_combination(statement_id, evidence_names)
                if "error" in result:
                    print(f"❌ {result['error']}")
                else:
                    print(f"📋 PRESENT COMBINATION: {', '.join(evidence_names)} against statement {statement_id}")
                    print(f"📜 STATEMENT: {result['statement_text']}")
                    
                    if result.get('game_over', False):
                        print(f"💀 GAME OVER: {result['response']}")
                        return 1
                    elif result['contradiction_found']:
                        print(f"🎯 {result['response']}")
                        print(f"⚡ COMBINATION TYPE: {result['combination_type']}")
                    else:
                        print(f"❌ {result['response']}")
                        if result.get('penalty_applied', False):
                            print(f"⚠️  PENALTY: {result['penalty_message']}")
                            print(f"📊 Penalty Count: {result['penalty_count']}")
        
        if args.check_victory:
            result = manager.check_cross_examination_victory()
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"\n=== CROSS-EXAMINATION STATUS ===")
                print(f"Contradictions Found: {result['successful_contradictions']}/{result['required_contradictions']}")
                print(f"Critical Lies Exposed: {result['critical_lies_exposed']}/{result['total_critical_lies']}")
                if result['victory_achieved']:
                    print(f"🏆 VICTORY! {result['victory_message']}")
                else:
                    print("⏳ Continue cross-examination to achieve victory conditions")
        
        if args.end_cross_examination:
            result = manager.end_cross_examination()
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"⚖️  {result['summary']}")
                victory_status = result['victory_status']
                if victory_status['victory_achieved']:
                    print(f"🏆 {victory_status['victory_message']}")
                else:
                    print("Cross-examination ended without achieving victory conditions")
        
        if args.show_statements:
            current_exam = manager.trial_state.get("current_cross_exam")
            if not current_exam:
                print("❌ No cross-examination in progress")
            else:
                witness_name = current_exam["witness"]
                cross_exam_data = manager.load_trial_statements(witness_name)
                if "error" in cross_exam_data:
                    print(f"❌ {cross_exam_data['error']}")
                else:
                    print(f"\n=== CROSS-EXAMINATION: {witness_name} ===")
                    for stmt in cross_exam_data['statements']:
                        print(f"{stmt['id']}. {stmt['text']}")
                    print(f"\nCommands: press [A-E] | present [A-E] [evidence_name]")
        
        if args.hint is not None:
            statement_id = args.hint.upper() if args.hint else None
            result = manager.get_hint(statement_id)
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                if result['hint_type'] == 'statement_specific':
                    print(f"\n💡 HINT for Statement {result['statement_id']}:")
                    print(f"📜 Statement: {result['statement_text']}")
                    print(f"🔍 Hint: {result['hint_text']}")
                else:
                    print(f"\n💡 GENERAL HINT:")
                    print(f"🔍 {result['hint_text']}")
                    
                    progress = result['progress_info']
                    print(f"\n📊 Your Progress:")
                    print(f"   ✅ Successful contradictions: {progress['successful_contradictions']}")
                    print(f"   ❌ Failed presentations: {progress['failed_presentations']}")
                    print(f"   ⚠️  Penalties: {progress['penalty_count']}")
                    print(f"   💬 Statements pressed: {progress['statements_pressed']}")
                    print(f"   🎯 Unchallenged lies remaining: {progress['unchallenged_lies']}")
        
        if args.trial_status:
            suggestion = manager.suggest_next_trial_action()
            progress = suggestion['progress_details']
            
            print(f"\n⚖️  TRIAL STATUS")
            print(f"Current Phase: {progress['phase'].replace('_', ' ').title()}")
            
            if progress['phase'] == 'not_started':
                print(f"Trial Ready: {progress['ready_for_trial']}")
            elif progress['phase'] == 'cross_examination':
                print(f"Current Witness: {progress['current_witness']}")
                print(f"Victory Achieved: {progress['victory_achieved']}")
                print(f"Successful Contradictions: {progress['successful_contradictions']}")
                print(f"Penalty Count: {progress['penalty_count']}")
            elif progress['phase'] == 'witness_examination':
                print(f"Available Witnesses: {', '.join(progress['available_witnesses'])}")
                print(f"Examined: {', '.join(progress['examined_witnesses'])}")
                if progress['next_witness']:
                    print(f"Next Witness: {progress['next_witness']}")
            elif progress['phase'] == 'closing_arguments':
                print(f"All Witnesses Examined: {progress['all_witnesses_examined']}")
                print(f"Trial Complete: {progress['trial_complete']}")
            
            print(f"\n💡 Next Action: {suggestion['suggestion']}")
            if suggestion['specific_command']:
                print(f"🔧 Suggested Command: --{suggestion['specific_command'].replace('_', '-')}")
        
        if args.generate_trial_statements:
            result = manager.auto_generate_trial_statements_for_case()
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"✅ Generated trial statements successfully!")
                print(f"📊 Statistics:")
                print(f"   Witnesses: {result['witnesses_generated']}")
                print(f"   Total Statements: {result['total_statements']}")
                print(f"   Contradictable Lies: {result['total_lies']}")
                print(f"💾 Saved to: {result['file_saved']}")
                print(f"\n🎯 Generated cross-examinations for:")
                for witness in result['witnesses']:
                    print(f"   - {witness.replace('_cross_exam', '').replace('_', ' ').title()}")
        
        if args.generate_witness_statements:
            result = manager.generate_trial_statements_from_backbone(args.generate_witness_statements)
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"✅ Generated statements for {result['witness_name']}")
                print(f"📊 Statistics:")
                print(f"   Statements: {result['statements_generated']}")
                print(f"   Lies: {result['lies_detected']}")
                print(f"\n🎯 Cross-examination data:")
                cross_exam = result['cross_exam_data']
                for stmt in cross_exam['statements']:
                    lie_indicator = "🔴" if stmt['is_lie'] else "🟢"
                    print(f"   {stmt['id']}. {lie_indicator} {stmt['text']}")
        
        if args.adapt_case:
            result = manager.adapt_case_for_interactive_trial()
            print(f"\n🔧 CASE ADAPTATION RESULTS")
            print(f"Case Type: {result['case_type']}")
            
            if result['success']:
                print("✅ Adaptation completed successfully!")
                
                if result['adaptations_made']:
                    print(f"\n🛠️  Adaptations Made:")
                    for adaptation in result['adaptations_made']:
                        print(f"   ✅ {adaptation}")
                
                if 'witnesses_generated' in result:
                    print(f"\n📊 Generation Statistics:")
                    print(f"   Witnesses: {result['witnesses_generated']}")
                    print(f"   Statements: {result['total_statements']}")
                
                if result['warnings']:
                    print(f"\n⚠️  Warnings:")
                    for warning in result['warnings']:
                        print(f"   ⚠️  {warning}")
                        
                print(f"\n🎯 Your case is now ready for interactive trials!")
                print(f"Use --trial-status to see available actions.")
            else:
                print("❌ Adaptation failed!")
                for warning in result['warnings']:
                    print(f"   ❌ {warning}")
        
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
        
        if args.roll is not None:
            if len(args.roll) == 0:
                # Simple d20 roll
                result = manager.roll_dice()
                print(f"🎲 D20 Roll: {result['base_roll']} = {result['total']} ({result['success_level']})")
            else:
                # Parse modifier and description
                modifier = 0
                description = ""
                if len(args.roll) >= 1:
                    try:
                        modifier = int(args.roll[0])
                        description = " ".join(args.roll[1:]) if len(args.roll) > 1 else ""
                    except ValueError:
                        description = " ".join(args.roll)
                
                result = manager.roll_dice(modifier, description)
                print(f"🎲 D20 Roll: {description}")
                print(f"   Result: {result['base_roll']} + {result['modifier']} = {result['total']}")
                print(f"   Success Level: {result['success_level']}")
        
        if args.action_check:
            action_description = args.action_check[0]
            difficulty = int(args.action_check[1]) if len(args.action_check) > 1 else 10
            evidence_count = int(args.action_check[2]) if len(args.action_check) > 2 else 0
            character_trust = int(args.action_check[3]) if len(args.action_check) > 3 else 0
            additional_modifier = int(args.action_check[4]) if len(args.action_check) > 4 else 0
            
            result = manager.make_action_check(
                action_description, difficulty, evidence_count, character_trust, additional_modifier
            )
            
            print(f"🎯 Action Check: {action_description}")
            print(f"   Target Difficulty: {result['target_difficulty']}")
            print(f"   Roll: {result['base_roll']} + {result['modifier']} = {result['total']}")
            print(f"   Result: {'SUCCESS' if result['succeeded'] else 'FAILURE'} (margin: {result['margin']})")
            print(f"   Success Level: {result['success_level']}")
            print(f"   Modifiers: Evidence({result['modifiers']['evidence_bonus']}) + Trust({result['modifiers']['trust_bonus']}) + Additional({result['modifiers']['additional']}) = {result['modifiers']['total']}")
        
        if args.dice_history:
            history = manager.get_recent_dice_rolls()
            if history:
                print(f"\n=== Recent Dice Rolls ===")
                for i, roll in enumerate(history, 1):
                    print(f"{i}. {roll['description'] or 'Generic roll'}")
                    print(f"   Result: {roll['base_roll']} + {roll['modifier']} = {roll['total']} ({roll['success_level']})")
                    print(f"   Time: {roll['timestamp']}")
                    print()
            else:
                print("No dice roll history found.")
        
        if args.client_name:
            client_name = manager.get_client_name()
            print(f"👤 Client Name: {client_name}")
        
        if args.generate_name is not None:
            role_hint = args.generate_name if args.generate_name else None
            name = manager.name_generator.generate_unique_name(role_hint)
            print(f"🎭 Generated Name: {name}")
            if role_hint:
                print(f"   Role Hint: {role_hint}")
        
        if args.generate_names:
            names = manager.name_generator.generate_multiple_names(args.generate_names)
            print(f"🎭 Generated {args.generate_names} Names:")
            for i, name in enumerate(names, 1):
                print(f"   {i}. {name}")
        
        if args.generate_name_personality is not None:
            role_hint = args.generate_name_personality if args.generate_name_personality else None
            name = manager.name_generator.generate_unique_name(role_hint, include_personality=True)
            print(f"🎭 Generated Name with Personality: {name}")
            if role_hint:
                print(f"   Role Hint: {role_hint}")
        
        if args.generate_personality:
            personality = manager.name_generator.generate_personality_trait()
            print(f"🎭 Generated Personality Trait: {personality}")
        
        if args.name_suggestions:
            suggestions = manager.name_generator.get_character_suggestions(args.name_suggestions)
            print(f"🎭 Name Suggestions for '{args.name_suggestions}':")
            for key, name in suggestions.items():
                print(f"   {key}: {name}")
        
        if args.create_family:
            family = manager.name_generator.create_family(args.create_family, args.family_surname)
            print(f"👨‍👩‍👧‍👦 Created family of {args.create_family}:")
            for role, name in family.items():
                print(f"   {role}: {name}")
            manager.name_generator.save_used_names()
        
        if args.add_family_member:
            try:
                if ':' not in args.add_family_member:
                    print("❌ Error: Format should be 'existing_name:relationship'")
                else:
                    existing_name, relationship = args.add_family_member.split(':', 1)
                    new_member = manager.name_generator.add_family_member_to_existing(existing_name.strip(), relationship.strip())
                    print(f"👥 Added family member: {new_member}")
                    print(f"   Relationship to {existing_name}: {relationship}")
                    manager.name_generator.save_used_names()
            except ValueError as e:
                print(f"❌ Error: {e}")
        
        if args.surname_suggestions:
            suggestions = manager.name_generator.get_family_surname_suggestions(args.surname_suggestions)
            print(f"📝 Surname suggestions (avoiding conflicts with: {', '.join(args.surname_suggestions)}):")
            for i, surname in enumerate(suggestions, 1):
                print(f"   {i}. {surname}")
        
        # Red herring system commands
        if args.classify_character:
            if len(args.classify_character) < 2:
                print("❌ Error: --classify-character requires CHARACTER_NAME and CASE_LENGTH")
            else:
                character_name = args.classify_character[0]
                case_length_str = args.classify_character[1]
                role_hint = args.classify_character[2] if len(args.classify_character) > 2 else None
                
                try:
                    case_length = int(case_length_str)
                    classification = manager.red_herring_classifier.classify_character(character_name, case_length, role_hint)
                    
                    if args.show_spoilers:
                        print(f"🎭 Character Classification:")
                        print(f"   Name: {character_name}")
                        print(f"   Case Length: {case_length} days")
                        if role_hint:
                            print(f"   Role Hint: {role_hint}")
                        print(f"   Role: {classification}")
                        
                        # Calculate and show weighted probability
                        weighted_prob = manager.red_herring_classifier.get_weighted_probability(case_length, role_hint)
                        if classification == "true_killer":
                            print(f"   ⚠️  Weighted killer probability was: {weighted_prob*100:.1f}%")
                        else:
                            print(f"   🎭 Weighted killer probability was: {weighted_prob*100:.1f}%")
                        
                        base_prob = 1.0/(case_length+1)*100
                        role_weight = manager.red_herring_classifier._get_role_weight(role_hint)
                        print(f"   📊 Base: {base_prob:.1f}% × Role weight: {role_weight:.1f}x")
                    else:
                        print(f"🎭 Character Classified:")
                        print(f"   Name: {character_name}")
                        print(f"   Case Length: {case_length} days")
                        if role_hint:
                            print(f"   Role Hint: {role_hint}")
                        print(f"   ✅ Classification recorded (use --show-spoilers to reveal)")
                        weighted_prob = manager.red_herring_classifier.get_weighted_probability(case_length, role_hint)
                        print(f"   📊 Role-weighted killer probability: {weighted_prob*100:.1f}%")
                except ValueError:
                    print("❌ Error: Case length must be a number (1, 2, or 3)")
        
        if args.check_character_role:
            role = manager.red_herring_classifier.get_character_role(args.check_character_role)
            if role:
                if args.show_spoilers:
                    print(f"🎭 Character Role Check:")
                    print(f"   Name: {args.check_character_role}")
                    print(f"   Classification: {role}")
                else:
                    print(f"🎭 Character Status:")
                    print(f"   Name: {args.check_character_role}")
                    print(f"   ✅ Has been classified (use --show-spoilers to reveal)")
            else:
                print(f"❓ Character '{args.check_character_role}' has not been classified yet")
        
        if args.list_classifications:
            classifications = manager.red_herring_classifier.get_all_classifications()
            if classifications:
                if args.show_spoilers:
                    print("🎭 All Character Classifications:")
                    killers = manager.red_herring_classifier.get_killers()
                    conspirators = manager.red_herring_classifier.get_conspirators()
                    red_herrings = manager.red_herring_classifier.get_red_herrings()
                    
                    if killers:
                        print(f"\n   🔪 Killers ({len(killers)}):")
                        for killer in killers:
                            print(f"      • {killer}")
                    
                    if conspirators:
                        print(f"\n   🤝 Conspirators ({len(conspirators)}):")
                        for conspirator in conspirators:
                            print(f"      • {conspirator}")
                    
                    if red_herrings:
                        print(f"\n   🎭 Red Herrings ({len(red_herrings)}):")
                        for herring in red_herrings:
                            print(f"      • {herring}")
                else:
                    print("🎭 Character Classifications:")
                    print(f"   Total Characters: {len(classifications)}")
                    print("   ✅ All classifications recorded")
                    print("   💡 Use --show-spoilers to reveal identities")
            else:
                print("❓ No characters have been classified yet")
        
        if args.classification_stats:
            stats = manager.red_herring_classifier.get_classification_stats(manager.case_length)
            print("📊 Classification Statistics:")
            print(f"   Case Length: {stats['case_length']} days")
            print(f"   Total Characters: {stats['total_characters']}")
            
            if args.show_spoilers:
                print(f"   Killers: {stats['killers']}")
                print(f"   Conspirators: {stats['conspirators']}")
                print(f"   Red Herrings: {stats['red_herrings']}")
                if stats['total_characters'] > 0:
                    print(f"   Actual Killer Rate: {stats['actual_killer_rate']*100:.1f}%")
                    print(f"   Actual Conspirator Rate: {stats['actual_conspirator_rate']*100:.1f}%")
                    print(f"   Actual Red Herring Rate: {stats['actual_red_herring_rate']*100:.1f}%")
            
            print(f"   Expected Killer Rate: {stats['expected_killer_rate']*100:.1f}%")
            print(f"   Expected Conspirator Rate: {stats['expected_conspirator_rate']*100:.1f}%")
            print(f"   Expected Red Herring Rate: {stats['expected_red_herring_rate']*100:.1f}%")
            
            if stats['killer_constraint_active']:
                print("   🚫 Killer constraint active (max 1 killer)")
            
            conspirator_caps = stats['conspirator_caps']
            current_conspirators = stats['conspirators']
            max_conspirators = conspirator_caps.get(stats['case_length'], 2)
            print(f"   🤝 Conspirator limit: {current_conspirators}/{max_conspirators}")
            
            if not args.show_spoilers and stats['total_characters'] > 0:
                print("   💡 Use --show-spoilers to see actual distribution")
        
        if args.generate_name_classified is not None:
            role_hint = args.generate_name_classified if args.generate_name_classified else None
            name, classification, age, occupation, personality = manager.name_generator.generate_name_with_classification(manager.case_length, role_hint)
            
            if args.show_spoilers:
                print(f"🎭 Generated Name with Classification:")
                print(f"   Name: {name}")
                print(f"   Age: {age}")
                print(f"   Occupation: {occupation}")
                print(f"   Personality: {personality}")
                print(f"   Classification: {classification}")
                print(f"   Case Length: {manager.case_length} days")
                if role_hint:
                    print(f"   Role Hint: {role_hint}")
                # Calculate and show weighted probability
                weighted_prob = manager.red_herring_classifier.get_weighted_probability(manager.case_length, role_hint)
                if classification == "true_killer":
                    print(f"   ⚠️  Weighted killer probability was: {weighted_prob*100:.1f}%")
                    base_prob = 1.0/(manager.case_length+1)*100
                    role_weight = manager.red_herring_classifier._get_role_weight(role_hint)
                    print(f"   📊 Base: {base_prob:.1f}% × Role weight: {role_weight:.1f}x")
                else:
                    print(f"   🎭 Weighted killer probability was: {weighted_prob*100:.1f}%")
                    base_prob = 1.0/(manager.case_length+1)*100
                    role_weight = manager.red_herring_classifier._get_role_weight(role_hint)
                    print(f"   📊 Base: {base_prob:.1f}% × Role weight: {role_weight:.1f}x")
            else:
                print(f"🎭 Generated Character:")
                print(f"   Name: {name}")
                print(f"   Age: {age}")
                print(f"   Occupation: {occupation}")
                print(f"   Personality: {personality}")
                print(f"   Case Length: {manager.case_length} days")
                if role_hint:
                    print(f"   Role Hint: {role_hint}")
                print(f"   ✅ Classification recorded (use --show-spoilers to reveal)")
                weighted_prob = manager.red_herring_classifier.get_weighted_probability(manager.case_length, role_hint)
                print(f"   📊 Role-weighted killer probability: {weighted_prob*100:.1f}%")
                
                # Store comprehensive character information
                if "character_facts" not in manager.current_state:
                    manager.current_state["character_facts"] = {}
                
                manager.current_state["character_facts"][name] = {
                    "age": age,
                    "occupation": occupation,
                    "personality": personality,
                    "role_hint": role_hint,
                    "generated_at": "case_start"
                }
                manager.save_current_state_to_file()
        
        if args.generate_age is not None:
            role_hint = args.generate_age if args.generate_age else None
            age = manager.name_generator.generate_age(role_hint)
            print(f"🎂 Generated Age:")
            print(f"   Age: {age}")
            if role_hint:
                print(f"   Role Hint: {role_hint}")
        
        if args.generate_occupation:
            try:
                age_str, role = args.generate_occupation
                age = int(age_str)
                occupation = manager.name_generator.generate_occupation(age, role)
                print(f"💼 Generated Occupation:")
                print(f"   Age: {age}")
                print(f"   Role: {role}")
                print(f"   Occupation: {occupation}")
            except ValueError:
                print("❌ Error: Age must be a number")
        
        # Enhanced narrative save system commands
        if args.create_narrative_save:
            # This requires interactive input for narrative context
            print("🎭 Creating narrative save requires comprehensive context.")
            print("Use the complete_gate method with narrative_context parameter in gameplay.")
            print(f"Gate: {args.create_narrative_save}")
        
        if args.restore_narrative:
            try:
                narrative_save = manager.narrative_save_system.restore_narrative_context(args.restore_narrative)
                summary = manager.narrative_save_system.generate_context_summary(narrative_save)
                print(summary)
            except FileNotFoundError:
                print(f"❌ Narrative save not found: {args.restore_narrative}")
            except Exception as e:
                print(f"❌ Error restoring narrative: {e}")
        
        if args.list_narrative_saves:
            saves = manager.narrative_save_system.list_narrative_saves()
            if saves:
                print("📚 Available Narrative Saves:")
                for save in saves:
                    print(f"   {save['filename']}")
                    print(f"      Gate: {save['gate_name']}")
                    print(f"      Time: {save['timestamp']}")
                    print(f"      Charges: {save['charges']}")
                    print()
            else:
                print("📚 No narrative saves found.")
        
        if args.narrative_summary:
            try:
                narrative_save = manager.narrative_save_system.restore_narrative_context(args.narrative_summary)
                summary = manager.narrative_save_system.generate_context_summary(narrative_save)
                print(summary)
            except FileNotFoundError:
                print(f"❌ Narrative save not found: {args.narrative_summary}")
            except Exception as e:
                print(f"❌ Error generating summary: {e}")
        
        # Context validation commands
        if args.validate_action:
            context = manager.get_resume_context()
            validation = manager.context_validator.validate_action_request(args.validate_action, context)
            
            if validation['valid']:
                print(f"✅ Action '{args.validate_action}' is valid for current state")
            else:
                print(f"❌ Action '{args.validate_action}' is invalid")
                print(f"Reason: {validation['reason']}")
                print(f"Alternative: {validation['alternative']}")
                print(f"Current state: {validation['current_state']}")
                print(f"Trial status: {validation['trial_status']}")
        
        if args.context_violation:
            print("🚨 CONTEXT VIOLATION DETECTED")
            print("AI must re-read comprehensive context and validate action compatibility")
            print("Required steps:")
            print("1. Re-run --resume to get current context")
            print("2. Identify current phase and last event")
            print("3. Validate requested action appropriateness")
            print("4. Provide corrected response based on actual game state")
            print()
            print("Context violations detected:")
            context = manager.get_resume_context()
            violations = manager.context_validator.check_context_violations(context)
            if violations:
                for violation in violations:
                    print(f"  - {violation}")
            else:
                print("  - No automatic violations detected - check manual interpretation")
        
        # New revelation commands
        if args.reveal_classification:
            character_name = args.reveal_classification
            classification = manager.red_herring_classifier.get_character_role(character_name)
            
            if classification is None:
                print(f"❌ Character '{character_name}' not found or not classified")
            else:
                print(f"🎭 REVELATION: {character_name}")
                if classification == "killer":
                    print(f"   💀 Classification: TRUE KILLER")
                    print(f"   ⚖️  This character is the actual perpetrator")
                    print(f"   🎯 Case can conclude with this revelation")
                elif classification == "conspirator":
                    print(f"   🤝 Classification: CONSPIRATOR")
                    print(f"   ⚠️  This character is involved but not the main perpetrator")
                    print(f"   🔍 Continue investigation to find the true killer")
                else:
                    print(f"   🎭 Classification: RED HERRING")
                    print(f"   ❌ This character is NOT the true killer")
                    print(f"   🔍 Continue investigation to find the real perpetrator")
                    
                    # Check if killer has been generated yet
                    killers = manager.red_herring_classifier.get_killers()
                    if not killers:
                        print(f"   ⚠️  No true killer generated yet - use --check-killer-status")
        
        if args.check_killer_status:
            killers = manager.red_herring_classifier.get_killers()
            total_characters = len(manager.red_herring_classifier.get_all_classifications())
            
            if killers:
                print(f"✅ KILLER STATUS: True killer has been generated")
                print(f"   🎭 Total characters classified: {total_characters}")
                print(f"   💀 Killer(s) in cast: {len(killers)}")
                print(f"   🎯 Case is solvable - true killer exists in character roster")
            else:
                print(f"❌ KILLER STATUS: No true killer generated yet")
                print(f"   🎭 Total characters classified: {total_characters}")
                print(f"   ⚠️  All current characters are red herrings")
                print(f"   🔧 Generate more characters to 'flush out' the true killer")
                print(f"   💡 Use --generate-name-classified to add more suspects")
        
        if args.remove_character:
            character_name = args.remove_character
            removed = manager.red_herring_classifier.remove_character(character_name)
            
            if removed:
                print(f"✅ Character '{character_name}' removed from classification system")
            else:
                print(f"❌ Character '{character_name}' not found in classification system")
        
        # Murder escalation commands
        if args.check_escalation_status:
            status = manager.get_escalation_status()
            print(f"🔍 MURDER ESCALATION STATUS")
            print(f"   Original Crime: {status['original_crime'].title()}")
            print(f"   Is Murder Case: {'Yes' if status['is_murder_case'] else 'No'}")
            print(f"   Escalated: {'Yes' if status['escalated'] else 'No'}")
            
            if status['escalated']:
                print(f"   Escalation Gate: {status['escalation_gate']}")
            else:
                print(f"   Gates Checked: {status['gates_checked']}")
                print(f"   Remaining Gates: {status['remaining_gates']}")
                if status['final_gate_mandatory']:
                    print(f"   Final Gate (Mandatory): {status['final_gate_mandatory']}")
                    if status['remaining_gates'] and status['final_gate_mandatory'] in status['remaining_gates']:
                        print(f"   ⚠️  Murder escalation guaranteed at final gate!")
        
        if args.force_escalation:
            current_gate = manager.get_next_gate()
            if current_gate:
                if manager.get_escalation_status()['escalated']:
                    print(f"❌ Case has already escalated to murder")
                elif manager.get_escalation_status()['original_crime'] == 'murder':
                    print(f"❌ Case is already a murder case")
                else:
                    manager.escalate_to_murder(current_gate)
                    print(f"✅ Murder escalation forced at gate: {current_gate}")
            else:
                print(f"❌ No current gate to escalate from")
        
        if args.escalation_narrative:
            crime_type = args.escalation_narrative.lower()
            narrative = manager.get_escalation_narrative(crime_type, "example_gate")
            print(f"🎭 ESCALATION NARRATIVE: {crime_type.title()} → Murder")
            print(f"   Type: {narrative['type']}")
            print(f"   Description: {narrative['description']}")
            print(f"   GM Guidance: {narrative['gm_guidance']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())