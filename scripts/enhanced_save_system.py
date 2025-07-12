#!/usr/bin/env python3
"""
Enhanced Save System for Narrative Continuity
Captures comprehensive case context at stage gates to prevent narrative drift
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class NarrativeSaveSystem:
    """Manages comprehensive narrative saves at stage gates"""
    
    def __init__(self, case_directory: str):
        self.case_directory = case_directory
        self.saves_dir = os.path.join(case_directory, "narrative_saves")
        os.makedirs(self.saves_dir, exist_ok=True)
    
    def create_narrative_save(self, gate_name: str, context: Dict[str, Any]) -> str:
        """Create comprehensive narrative save at stage gate"""
        
        # Load current game state
        game_state = self._load_game_state()
        
        # Create comprehensive narrative context
        narrative_save = {
            "metadata": {
                "gate_name": gate_name,
                "timestamp": datetime.now().isoformat(),
                "case_directory": os.path.basename(self.case_directory)
            },
            
            "case_facts": {
                "charges": context.get("charges", {}),
                "victim": context.get("victim", {}),
                "defendant": context.get("defendant", {}),
                "incident": context.get("incident", {}),
                "stakes": context.get("stakes", "")
            },
            
            "narrative_state": {
                "case_summary": context.get("case_summary", ""),
                "current_phase": game_state.get("current_phase", ""),
                "key_revelations": context.get("key_revelations", []),
                "unresolved_mysteries": context.get("unresolved_mysteries", []),
                "plot_threads": context.get("plot_threads", [])
            },
            
            "character_dynamics": context.get("character_dynamics", {}),
            
            "evidence_significance": self._enhance_evidence_context(
                game_state.get("evidence_collected", []),
                context.get("evidence_analysis", {})
            ),
            
            "trial_context": {
                "legal_strategy": context.get("legal_strategy", ""),
                "key_arguments": context.get("key_arguments", []),
                "evidence_presentation_plan": context.get("evidence_plan", []),
                "expected_objections": context.get("objections", [])
            },
            
            "emotional_stakes": {
                "player_investment": context.get("player_investment", ""),
                "dramatic_tension": context.get("dramatic_tension", ""),
                "character_motivations": context.get("motivations", {})
            },
            
            "game_state_snapshot": game_state
        }
        
        # Save to file
        save_filename = f"{gate_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_path = os.path.join(self.saves_dir, save_filename)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(narrative_save, f, indent=2, ensure_ascii=False)
        
        return save_path
    
    def restore_narrative_context(self, save_filename: str) -> Dict[str, Any]:
        """Restore comprehensive narrative context from save"""
        save_path = os.path.join(self.saves_dir, save_filename)
        
        if not os.path.exists(save_path):
            raise FileNotFoundError(f"Narrative save not found: {save_filename}")
        
        with open(save_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_context_summary(self, narrative_save: Dict[str, Any]) -> str:
        """Generate natural language summary for context restoration"""
        
        case_facts = narrative_save["case_facts"]
        narrative = narrative_save["narrative_state"]
        
        summary = f"""=== CASE CONTEXT RESTORATION ===

**Case**: {narrative_save['metadata']['case_directory']}
**Stage**: {narrative_save['metadata']['gate_name']}

**CHARGES**: {case_facts['charges'].get('primary', 'Unknown')}
**VICTIM**: {case_facts['victim'].get('name', 'Unknown')} - {case_facts['victim'].get('status', 'Unknown status')}
**DEFENDANT**: {case_facts['defendant'].get('name', 'Unknown')} - {case_facts['defendant'].get('relationship', 'Unknown relationship')}

**INCIDENT SUMMARY**:
{case_facts['incident'].get('summary', 'No summary available')}

**KEY EVIDENCE DISCOVERED**:
"""
        
        for evidence in narrative_save["evidence_significance"]:
            summary += f"- **{evidence['name']}**: {evidence['significance']}\n"
        
        summary += f"""
**CURRENT STRATEGY**: {narrative_save['trial_context']['legal_strategy']}

**UNRESOLVED MYSTERIES**:
"""
        for mystery in narrative["unresolved_mysteries"]:
            summary += f"- {mystery}\n"
        
        summary += f"""
**DRAMATIC STAKES**: {narrative_save['emotional_stakes']['dramatic_tension']}
"""
        
        return summary
    
    def _load_game_state(self) -> Dict[str, Any]:
        """Load current game state"""
        state_path = os.path.join(self.case_directory, "game_state", "investigation_progress.json")
        
        if os.path.exists(state_path):
            with open(state_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _enhance_evidence_context(self, evidence_list: List[Dict], analysis: Dict) -> List[Dict]:
        """Enhance evidence with significance and implications"""
        enhanced = []
        
        for evidence in evidence_list:
            enhanced_evidence = evidence.copy()
            evidence_name = evidence["name"]
            
            if evidence_name in analysis:
                enhanced_evidence["significance"] = analysis[evidence_name].get("significance", "")
                enhanced_evidence["implications"] = analysis[evidence_name].get("implications", [])
                enhanced_evidence["trial_value"] = analysis[evidence_name].get("trial_value", "")
            else:
                enhanced_evidence["significance"] = enhanced_evidence.get("description", "")
                enhanced_evidence["implications"] = []
                enhanced_evidence["trial_value"] = "Unknown"
            
            enhanced.append(enhanced_evidence)
        
        return enhanced
    
    def list_narrative_saves(self) -> List[Dict[str, str]]:
        """List all available narrative saves"""
        saves = []
        
        if not os.path.exists(self.saves_dir):
            return saves
        
        for filename in os.listdir(self.saves_dir):
            if filename.endswith('.json'):
                save_path = os.path.join(self.saves_dir, filename)
                try:
                    with open(save_path, 'r') as f:
                        save_data = json.load(f)
                    
                    saves.append({
                        "filename": filename,
                        "gate_name": save_data["metadata"]["gate_name"],
                        "timestamp": save_data["metadata"]["timestamp"],
                        "charges": save_data["case_facts"]["charges"].get("primary", "Unknown")
                    })
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return sorted(saves, key=lambda x: x["timestamp"], reverse=True)


def create_sample_narrative_save():
    """Create sample narrative save for the_midnight_masquerade case"""
    
    # Correct case context based on actual facts
    context = {
        "charges": {
            "primary": "assault with intent to cause grievous bodily harm",
            "related": ["stalking", "intimidation", "property damage"],
            "NOT_murder": True,
            "details": "Throwing petrol on victim's face and attempting to ignite"
        },
        
        "victim": {
            "name": "Sandra Watts",
            "status": "survived with facial burns",
            "relationship": "former romantic partner of defendant",
            "testimony_role": "primary prosecution witness"
        },
        
        "defendant": {
            "name": "David Mcgrath",
            "occupation": "security guard",
            "background": "former street performer with fire expertise",
            "handedness": "right-handed",
            "relationship": "accused of assaulting ex-girlfriend"
        },
        
        "incident": {
            "summary": "David allegedly threw petrol on Sandra's face and tried to light it, causing burns to left side of her face",
            "location": "Sandra's apartment",
            "key_inconsistency": "Right-handed defendant could not create left-side burn pattern"
        },
        
        "stakes": "2-5 years prison sentence for aggravated assault",
        
        "case_summary": "Defense of David Mcgrath against assault charges. Key evidence shows physical impossibility - right-handed defendant cannot create left-side facial burns as alleged.",
        
        "key_revelations": [
            "David is right-handed",
            "Burn pattern on Sandra's left side",
            "David has street performer background with fire expertise",
            "Sandra showing anger rather than distress after incident"
        ],
        
        "unresolved_mysteries": [
            "Who actually attacked Sandra if not David?",
            "Why is Sandra accusing David specifically?",
            "What was Sandra angry about after the incident?",
            "Who else had access to create this burn pattern?"
        ],
        
        "character_dynamics": {
            "David Mcgrath": {
                "role": "defendant",
                "key_traits": "observant from street performer background, cooperative",
                "secrets": "noticed Sandra's anger rather than distress that night",
                "player_relationship": "trusting, relies on defense"
            },
            "Sandra Watts": {
                "role": "victim/witness",
                "key_traits": "burn victim, ex-girlfriend of defendant",
                "secrets": "behavior inconsistent with genuine victim",
                "player_relationship": "hostile, defensive under cross-examination"
            }
        },
        
        "evidence_analysis": {
            "David's Right-Handedness": {
                "significance": "Creates physical impossibility of creating left-side burns",
                "implications": ["Someone else attacked Sandra", "David is being framed"],
                "trial_value": "Core defense argument - reasonable doubt"
            },
            "David's Street Performer Background": {
                "significance": "Expert fire handling experience contradicts sloppy attack pattern",
                "implications": ["David would know proper technique", "Attack shows amateur execution"],
                "trial_value": "Character evidence of expertise vs. alleged clumsiness"
            },
            "Evidence Location Inconsistencies": {
                "significance": "Physical evidence doesn't match prosecution timeline",
                "implications": ["Scene was staged", "Multiple perpetrators possible"],
                "trial_value": "Prosecution theory has holes"
            }
        },
        
        "legal_strategy": "Prove physical impossibility of right-handed defendant creating left-side burns, expose Sandra's inconsistent behavior",
        
        "dramatic_tension": "David faces years in prison for crime he physically could not have committed, while real attacker remains free"
    }
    
    # Create narrative save
    save_system = NarrativeSaveSystem("/Users/jarrod/Dropbox/claude_mystery_games/the_midnight_masquerade")
    save_path = save_system.create_narrative_save("trial_opening_corrected", context)
    
    print(f"Sample narrative save created: {save_path}")
    
    # Generate and display context summary
    narrative_save = save_system.restore_narrative_context(os.path.basename(save_path))
    summary = save_system.generate_context_summary(narrative_save)
    print("\n" + "="*60)
    print("GENERATED CONTEXT SUMMARY:")
    print("="*60)
    print(summary)

if __name__ == "__main__":
    create_sample_narrative_save()