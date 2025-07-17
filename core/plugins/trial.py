"""
Trial System Plugin

Handles courtroom proceedings, cross-examinations, and evidence presentation.
Provides authentic Ace Attorney-style trial mechanics.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class TrialPlugin:
    """Manages trial proceedings and courtroom mechanics"""
    
    def __init__(self):
        self.trial_state: Dict[str, Any] = {
            "status": "not_started",
            "current_witness": None,
            "cross_examination": None,
            "evidence_presented": [],
            "penalties": 0,
            "max_penalties": 5
        }
        self.witness_statements: List[Dict[str, Any]] = []
        self.testimony_history: List[Dict[str, Any]] = []
    
    def load_state(self, trial_data: Dict[str, Any]) -> None:
        """Load trial state from game state"""
        self.trial_state.update(trial_data.get("state", {}))
        self.witness_statements = trial_data.get("statements", [])
        self.testimony_history = trial_data.get("history", [])
    
    def start_trial(self, prosecutor_name: str, judge_name: str) -> Dict[str, Any]:
        """Begin trial proceedings"""
        
        if self.trial_state["status"] != "not_started":
            raise ValueError("Trial already in progress")
        
        self.trial_state.update({
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "prosecutor": prosecutor_name,
            "judge": judge_name,
            "phase": "opening_statements",
            "penalties": 0
        })
        
        return {
            "message": "Trial has begun! Court is now in session.",
            "phase": "opening_statements",
            "next_action": "Give opening statement or call first witness"
        }
    
    def call_witness(self, witness_name: str, witness_role: str = "witness") -> Dict[str, Any]:
        """Call a witness to testify"""
        
        if self.trial_state["status"] != "in_progress":
            raise ValueError("Trial not in progress")
        
        self.trial_state.update({
            "current_witness": witness_name,
            "witness_role": witness_role,
            "phase": "witness_testimony"
        })
        
        return {
            "message": f"{witness_name} has been called to the witness stand.",
            "current_witness": witness_name,
            "next_action": "Begin testimony or direct examination"
        }
    
    def start_cross_examination(self, witness_name: str, 
                               statements: List[str]) -> Dict[str, Any]:
        """Start cross-examination with witness statements"""
        
        if self.trial_state["status"] != "in_progress":
            raise ValueError("Trial not in progress")
        
        if not statements or len(statements) < 3:
            raise ValueError("Need at least 3 witness statements for cross-examination")
        
        # Create statement objects
        statement_objects = []
        for i, statement in enumerate(statements):
            statement_objects.append({
                "id": chr(65 + i),  # A, B, C, etc.
                "text": statement,
                "pressed": False,
                "contradicted": False
            })
        
        self.witness_statements = statement_objects
        
        self.trial_state.update({
            "cross_examination": {
                "witness": witness_name,
                "active": True,
                "started_at": datetime.now().isoformat(),
                "statements_count": len(statements),
                "victory_condition": None
            },
            "phase": "cross_examination"
        })
        
        return {
            "message": f"Cross-examination of {witness_name} begins!",
            "statements": self._format_statements_for_display(),
            "available_commands": [
                "press [A-E] - Press witness for details (information only)",
                "present [A-E] '[evidence_name]' - Present evidence against statement (case progress)",
                "hint - Get hint about current situation", 
                "end - End cross-examination"
            ]
        }
    
    def press_statement(self, statement_id: str) -> Dict[str, Any]:
        """Press witness for more details on a statement"""
        
        if not self._is_cross_examination_active():
            raise ValueError("No active cross-examination")
        
        statement = self._find_statement(statement_id)
        if not statement:
            raise ValueError(f"Statement {statement_id} not found")
        
        # Mark as pressed
        statement["pressed"] = True
        
        # Record action
        self.testimony_history.append({
            "action": "press",
            "statement_id": statement_id,
            "statement_text": statement["text"],
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "action": "press",
            "statement_id": statement_id,
            "message": f"You press {statement_id} for more details...",
            "note": "Press actions provide information only - use 'present' to make case progress",
            "effect": "information_only"
        }
    
    def present_evidence(self, statement_id: str, evidence_name: str) -> Dict[str, Any]:
        """Present evidence against a witness statement"""
        
        if not self._is_cross_examination_active():
            raise ValueError("No active cross-examination")
        
        statement = self._find_statement(statement_id)
        if not statement:
            raise ValueError(f"Statement {statement_id} not found")
        
        # Record evidence presentation
        presentation_record = {
            "action": "present_evidence",
            "statement_id": statement_id,
            "statement_text": statement["text"],
            "evidence_name": evidence_name,
            "timestamp": datetime.now().isoformat(),
            "result": None  # To be filled by AI
        }
        
        self.testimony_history.append(presentation_record)
        self.trial_state["evidence_presented"].append(evidence_name)
        
        return {
            "action": "objection",
            "statement_id": statement_id,
            "evidence_name": evidence_name,
            "message": f"OBJECTION! Presenting '{evidence_name}' against statement {statement_id}!",
            "note": "This creates a dramatic moment that advances the case",
            "effect": "case_progress",
            "requires_ai_response": True
        }
    
    def add_penalty(self, reason: str = "Wrong evidence presentation") -> Dict[str, Any]:
        """Add penalty for incorrect evidence presentation"""
        
        self.trial_state["penalties"] += 1
        
        penalty_record = {
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "penalty_count": self.trial_state["penalties"]
        }
        
        self.testimony_history.append({
            "action": "penalty",
            "data": penalty_record
        })
        
        # Check for game over
        if self.trial_state["penalties"] >= self.trial_state["max_penalties"]:
            return {
                "penalty_added": True,
                "penalty_count": self.trial_state["penalties"],
                "game_over": True,
                "message": "Too many penalties! Your case has been dismissed!"
            }
        
        return {
            "penalty_added": True,
            "penalty_count": self.trial_state["penalties"],
            "max_penalties": self.trial_state["max_penalties"],
            "game_over": False,
            "message": f"Penalty! {reason} ({self.trial_state['penalties']}/{self.trial_state['max_penalties']})"
        }
    
    def end_cross_examination(self, victory: bool = False, 
                            breakthrough: str = "") -> Dict[str, Any]:
        """End current cross-examination"""
        
        if not self._is_cross_examination_active():
            raise ValueError("No active cross-examination")
        
        # Record cross-examination end
        end_record = {
            "action": "end_cross_examination",
            "witness": self.trial_state["cross_examination"]["witness"],
            "victory": victory,
            "breakthrough": breakthrough,
            "duration": self._calculate_examination_duration(),
            "timestamp": datetime.now().isoformat()
        }
        
        self.testimony_history.append(end_record)
        
        # Clear cross-examination state
        self.trial_state["cross_examination"] = None
        self.trial_state["current_witness"] = None
        self.trial_state["phase"] = "trial_proceedings"
        self.witness_statements = []
        
        if victory:
            return {
                "cross_examination_ended": True,
                "victory": True,
                "breakthrough": breakthrough,
                "message": "Cross-examination successful! The truth has been revealed!",
                "next_action": "Continue trial proceedings or call next witness"
            }
        else:
            return {
                "cross_examination_ended": True,
                "victory": False,
                "message": "Cross-examination ended without breakthrough.",
                "next_action": "Call next witness or pursue different strategy"
            }
    
    def get_cross_examination_status(self) -> Dict[str, Any]:
        """Get current cross-examination status"""
        
        if not self._is_cross_examination_active():
            return {"active": False}
        
        exam = self.trial_state["cross_examination"]
        
        pressed_statements = [s for s in self.witness_statements if s["pressed"]]
        contradicted_statements = [s for s in self.witness_statements if s["contradicted"]]
        
        return {
            "active": True,
            "witness": exam["witness"],
            "statements_count": len(self.witness_statements),
            "pressed_count": len(pressed_statements),
            "contradicted_count": len(contradicted_statements),
            "penalties": self.trial_state["penalties"],
            "max_penalties": self.trial_state["max_penalties"],
            "evidence_presented": len(self.trial_state["evidence_presented"]),
            "duration": self._calculate_examination_duration()
        }
    
    def get_trial_summary(self) -> Dict[str, Any]:
        """Get comprehensive trial summary"""
        
        if self.trial_state["status"] == "not_started":
            return {"status": "not_started", "message": "Trial has not begun"}
        
        # Count different action types
        presses = len([h for h in self.testimony_history if h.get("action") == "press"])
        objections = len([h for h in self.testimony_history if h.get("action") == "present_evidence"])
        penalties = len([h for h in self.testimony_history if h.get("action") == "penalty"])
        
        # Get witness list
        witnesses_called = list(set([
            h.get("witness") for h in self.testimony_history 
            if h.get("action") == "end_cross_examination" and h.get("witness")
        ]))
        
        return {
            "status": self.trial_state["status"],
            "phase": self.trial_state.get("phase", "unknown"),
            "current_witness": self.trial_state.get("current_witness"),
            "prosecutor": self.trial_state.get("prosecutor"),
            "judge": self.trial_state.get("judge"),
            "penalties": self.trial_state["penalties"],
            "max_penalties": self.trial_state["max_penalties"],
            "statistics": {
                "presses": presses,
                "objections": objections,
                "penalties": penalties,
                "witnesses_called": len(witnesses_called),
                "evidence_presented": len(self.trial_state["evidence_presented"])
            },
            "witnesses_called": witnesses_called,
            "evidence_presented": self.trial_state["evidence_presented"],
            "started_at": self.trial_state.get("started_at")
        }
    
    def get_hint(self, context: Dict[str, Any]) -> str:
        """Get context-aware hint for current trial situation"""
        
        if not self._is_cross_examination_active():
            return "No active cross-examination. Call a witness to begin testimony."
        
        # Analyze current situation
        pressed_count = len([s for s in self.witness_statements if s["pressed"]])
        contradicted_count = len([s for s in self.witness_statements if s["contradicted"]])
        
        # Evidence-based hints
        evidence_count = context.get("evidence_count", 0)
        if evidence_count == 0:
            return "You have no evidence! Gather evidence during investigation before trial."
        
        # Progress-based hints
        if pressed_count == 0:
            return "Try pressing statements (A-E) to get more information before presenting evidence."
        
        if contradicted_count == 0 and pressed_count >= 2:
            return "You've pressed several statements. Look for contradictions to present evidence against."
        
        # Penalty-based hints
        if self.trial_state["penalties"] >= 3:
            return "Be careful! Too many wrong evidence presentations will end your case."
        
        # General hints
        hints = [
            "Look for statements that contradict your evidence.",
            "Press statements that seem suspicious for more details.",
            "Present evidence that directly contradicts what the witness said.",
            "Pay attention to specific details in statements that don't match evidence."
        ]
        
        import random
        return random.choice(hints)
    
    def _is_cross_examination_active(self) -> bool:
        """Check if cross-examination is currently active"""
        return (self.trial_state.get("cross_examination") is not None and 
                self.trial_state["cross_examination"].get("active", False))
    
    def _find_statement(self, statement_id: str) -> Optional[Dict[str, Any]]:
        """Find statement by ID"""
        statement_id = statement_id.upper()
        for statement in self.witness_statements:
            if statement["id"] == statement_id:
                return statement
        return None
    
    def _format_statements_for_display(self) -> List[str]:
        """Format statements for display in cross-examination"""
        formatted = []
        for statement in self.witness_statements:
            prefix = f"{statement['id']}. "
            indicators = ""
            
            if statement["pressed"]:
                indicators += " [PRESSED]"
            if statement["contradicted"]:
                indicators += " [CONTRADICTED]"
            
            formatted.append(f"{prefix}{statement['text']}{indicators}")
        
        return formatted
    
    def _calculate_examination_duration(self) -> str:
        """Calculate cross-examination duration"""
        
        exam = self.trial_state.get("cross_examination")
        if not exam or "started_at" not in exam:
            return "unknown"
        
        try:
            from datetime import datetime
            start_time = datetime.fromisoformat(exam["started_at"].replace('Z', '+00:00'))
            current_time = datetime.now(start_time.tzinfo)
            duration = current_time - start_time
            
            minutes = int(duration.total_seconds() / 60)
            if minutes < 1:
                return "less than 1 minute"
            elif minutes == 1:
                return "1 minute"
            else:
                return f"{minutes} minutes"
        
        except:
            return "unknown"
    
    def validate_trial_readiness(self, evidence_count: int, 
                                character_count: int) -> Dict[str, Any]:
        """Validate if case is ready for trial"""
        
        ready = True
        issues = []
        recommendations = []
        
        # Evidence requirements
        if evidence_count < 3:
            ready = False
            issues.append("Insufficient evidence for trial")
            recommendations.append("Gather at least 3 pieces of evidence")
        
        # Character requirements  
        if character_count < 4:
            ready = False
            issues.append("Need more characters for compelling trial")
            recommendations.append("Introduce more witnesses and suspects")
        
        # Trial readiness assessment
        readiness_score = 0
        if evidence_count >= 5:
            readiness_score += 3
        elif evidence_count >= 3:
            readiness_score += 2
        
        if character_count >= 6:
            readiness_score += 3
        elif character_count >= 4:
            readiness_score += 2
        
        if readiness_score >= 4:
            ready = True
            recommendations.append("Case looks ready for trial!")
        
        return {
            "ready_for_trial": ready,
            "readiness_score": readiness_score,
            "max_score": 6,
            "issues": issues,
            "recommendations": recommendations,
            "evidence_count": evidence_count,
            "character_count": character_count
        }