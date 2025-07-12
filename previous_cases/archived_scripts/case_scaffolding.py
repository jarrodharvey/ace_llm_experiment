#!/usr/bin/env python3
"""
Case Scaffolding Script
Automates the structural aspects of case creation, leaving only creative content for manual input.
"""

import json
import os
import argparse
import sys
import random
from pathlib import Path
import subprocess
from case_config import get_config_manager

class CaseScaffolding:
    def __init__(self, case_name, base_path="."):
        self.case_name = case_name
        self.base_path = Path(base_path)
        self.case_path = self.base_path / case_name
        self.config_manager = get_config_manager()
        self.case_length = self.determine_case_length()
        
        # Required directory structure (from config)
        mandatory_dirs = list(self.config_manager.get_mandatory_files().keys())
        optional_dirs = list(self.config_manager.get_optional_files().keys())
        self.directories = list(set(mandatory_dirs + optional_dirs))
        
        # Template files to create (from config)
        self.templates = self.config_manager.get_mandatory_files()
    
    def determine_case_length(self):
        """Randomly determine case length (1-3 days) based on Ace Attorney structure"""
        available_lengths = list(self.config_manager.get_case_lengths().keys())
        return int(random.choice(available_lengths))
    
    def create_investigation_gates(self):
        """Create appropriate gate structure based on case length"""
        gates = self.config_manager.get_gates_for_case_length(self.case_length)
        return {gate: "pending" for gate in gates}
    
    def create_directory_structure(self):
        """Create the case directory and all subdirectories"""
        print(f"📁 Creating directory structure for '{self.case_name}' ({self.case_length}-day case)...")
        
        # Create main case directory
        self.case_path.mkdir(exist_ok=True)
        print(f"   ✅ Created: {self.case_path}")
        
        # Create subdirectories
        for directory in self.directories:
            dir_path = self.case_path / directory
            dir_path.mkdir(exist_ok=True)
            print(f"   ✅ Created: {dir_path}")
    
    def generate_inspiration_pool(self):
        """DEPRECATED: No longer generates inspiration pools - using pure random words instead"""
        print(f"🎲 Skipping inspiration pool generation (using pure random words)...")
        print("   ✅ Pure random inspiration system enabled")
        return True
    
    def create_backbone_templates(self):
        """Create template files for backbone development"""
        print(f"📋 Creating backbone template files...")
        
        templates = {
            "case_structure.json": {
                "case_title": f"[CASE TITLE]",
                "case_id": f"{self.case_name}",
                "difficulty": "[easy/medium/hard]",
                "estimated_time": "[XX-YY minutes]",
                "victim": {
                    "name": "[VICTIM NAME]",
                    "age": "[AGE]",
                    "occupation": "[OCCUPATION]",
                    "murder_method": "[METHOD]",
                    "location": "[LOCATION]",
                    "time_of_death": "[TIME]"
                },
                "client": {
                    "name": "[CLIENT NAME]", 
                    "age": "[AGE]",
                    "occupation": "[OCCUPATION]",
                    "charges": "[CHARGES]",
                    "why_appears_guilty": [],
                    "why_actually_innocent": []
                },
                "real_killer": {
                    "name": "[KILLER NAME]",
                    "true_motive": "[MOTIVE]",
                    "why_not_suspected": []
                },
                "victory_conditions": {}
            },
            
            "character_facts.json": {
                "characters": [
                    {
                        "name": "[CHARACTER NAME] (Client)",
                        "true_knowledge": [],
                        "what_he_hides": [],
                        "motivations": "[MOTIVATIONS]"
                    }
                ]
            },
            
            "evidence_chain.json": {
                "evidence_pieces": [],
                "evidence_chain_logic": {},
                "how_client_was_framed": {}
            },
            
            "truth_timeline.json": {
                "timeline_of_actual_events": {},
                "key_timeline_facts": {}
            },
            
            "witness_testimonies.json": {
                "true_testimonies_before_fabrication": [],
                "testimony_analysis": {}
            },
            
            "trial_structure.json": {
                "trial_phase_structure": {
                    "prosecutor_profile": {},
                    "witness_order": [],
                    "cross_examination_targets": {},
                    "victory_sequence": {}
                }
            }
        }
        
        for filename, template in templates.items():
            file_path = self.case_path / "backbone" / filename
            with open(file_path, 'w') as f:
                json.dump(template, f, indent=2)
            print(f"   ✅ Created: {file_path}")
    
    def create_game_state_files(self):
        """Create initial game state files"""
        print(f"🎮 Creating game state files...")
        
        investigation_progress = {
            "current_phase": "ready_to_start",
            "case_length": self.case_length,
            "investigation_gates": self.create_investigation_gates(),
            "evidence_collected": [],
            "witnesses_interviewed": [],
            "psyche_locks_broken": [],
            "character_trust_levels": {},
            "current_location": "detention_center",
            "available_locations": [
                "detention_center"
            ],
            "day": 1,
            "time_until_trial": f"{self.case_length} days" if self.case_length > 1 else "trial_only",
            "investigation_notes": []
        }
        
        trial_progress = {
            "trial_status": "not_started",
            "current_witness": None,
            "witnesses_examined": [],
            "evidence_presented": [],
            "contradictions_exposed": [],
            "prosecutor_confidence": 95,
            "jury_opinion": "strongly_against_defendant",
            "trial_day": 0,
            "session_progress": {
                "opening_statements": "pending",
                "prosecution_case": "pending",
                "cross_examinations": "pending", 
                "final_arguments": "pending",
                "verdict": "pending"
            }
        }
        
        # Save files
        with open(self.case_path / "game_state" / "investigation_progress.json", 'w') as f:
            json.dump(investigation_progress, f, indent=2)
        print(f"   ✅ Created: investigation_progress.json")
        
        with open(self.case_path / "game_state" / "trial_progress.json", 'w') as f:
            json.dump(trial_progress, f, indent=2)
        print(f"   ✅ Created: trial_progress.json")
    
    def create_solution_templates(self):
        """Create solution template files"""
        print(f"🔍 Creating solution template files...")
        
        templates = {
            "evidence_requirements.json": {
                "investigation_gates": {},
                "trial_evidence_requirements": {},
                "psyche_lock_scenarios": {}
            },
            
            "character_behaviors.json": {
                "investigation_behaviors": {},
                "trial_behaviors": {}
            },
            
            "integrated_case.json": {
                "case_validation": {
                    "logical_consistency_check": "PENDING",
                    "evidence_chain_integrity": "PENDING",
                    "character_knowledge_alignment": "PENDING"
                },
                "case_summary": {},
                "deployment_readiness": {
                    "status": "UNDER_DEVELOPMENT"
                }
            }
        }
        
        for filename, template in templates.items():
            file_path = self.case_path / "solution" / filename
            with open(file_path, 'w') as f:
                json.dump(template, f, indent=2)
            print(f"   ✅ Created: {file_path}")
    
    def create_chatgpt_request_templates(self):
        """Create ChatGPT consultation request templates"""
        print(f"🤖 Creating ChatGPT request templates...")
        
        obstacle_request = {
            "phase": "2A_investigation_obstacles",
            "prompt_template": "You are a game designer creating specific investigation obstacles for an Ace Attorney fan game. DO NOT provide commentary or ratings - only create the actual content requested. CASE BACKBONE: [Insert backbone summary] Create a detailed JSON structure with these specific investigation obstacles: 1. BUREAUCRATIC BARRIERS - List 3-4 specific administrative roadblocks that delay evidence gathering (court orders, encryption, backlogged tests, etc.) 2. HOSTILE WITNESSES - Design 3-4 uncooperative characters with specific reasons for hostility (job fears, loyalty conflicts, personal secrets) 3. FALSE APPEARANCES - Create 3-4 ways the real killer appears helpful while the client looks guilty 4. PSYCHE-LOCK SCENARIOS - Design 2-3 dramatic confrontation sequences with: character name, number of locks (3-5), required evidence list, breakthrough trigger 5. EVIDENCE PRESENTATION GATES - Create 3 story-driven checkpoints where specific evidence must be presented to specific characters before progression Format your response as a JSON object with keys: bureaucratic_barriers, hostile_witnesses, false_appearances, psyche_lock_scenarios, evidence_presentation_gates. Each section should contain specific, actionable content that a game master can immediately use.",
            "command": f"python scripts/chatgpt_consultant.py \"[PROMPT]\" -o obstacles/chatgpt_obstacles_v1.json",
            "notes": "Replace [PROMPT] with filled prompt_template above"
        }
        
        trial_request = {
            "phase": "2B_trial_fabrications", 
            "prompt_template": "You are creating specific trial content for an Ace Attorney fan game. DO NOT provide commentary or ratings - only create the actual fabricated testimonies and trial elements requested. TRUE TESTIMONIES: [Insert witness testimonies summary] EVIDENCE LIST: [Insert evidence chain summary] Create a detailed JSON structure with these specific trial fabrications: 1. PROSECUTOR PROFILE - Name, specific quirky personality traits, signature props they bring to court, catchphrase 2. FABRICATED TESTIMONIES - For each key witness, create specific lies they will tell, formatted as: witness name, list of 3-4 fabricated claims, list of evidence pieces that contradict each lie 3. DRAMATIC BREAKDOWNS - For each witness, describe their specific meltdown when lies are exposed (physical actions, props, emotional reactions) 4. IMPOSSIBLE BUT LOGICAL ELEMENTS - Create 2-3 seemingly supernatural courtroom moments that have logical explanations tied to evidence 5. GALLERY REACTIONS - Specific crowd responses to major revelations 6. JUDGE CHAOS - Specific judicial mistakes, terminology confusion, and comedic timing issues Format your response as a JSON object with keys: prosecutor_profile, fabricated_testimonies, dramatic_breakdowns, impossible_but_logical_elements, gallery_reactions, judge_chaos. Each section should contain specific, usable content for immediate gameplay implementation.",
            "command": f"python scripts/chatgpt_consultant.py \"[PROMPT]\" -o obstacles/trial_fabrications.json -t 0.8",
            "notes": "Replace [PROMPT] with filled prompt_template above"
        }
        
        with open(self.case_path / "chatgpt_obstacle_request.json", 'w') as f:
            json.dump(obstacle_request, f, indent=2)
        print(f"   ✅ Created: chatgpt_obstacle_request.json")
        
        with open(self.case_path / "chatgpt_trial_request.json", 'w') as f:
            json.dump(trial_request, f, indent=2)
        print(f"   ✅ Created: chatgpt_trial_request.json")
    
    def validate_structure(self):
        """Validate that all required files and directories exist"""
        print(f"🔍 Validating case structure...")
        
        # Check directories
        missing_dirs = []
        for directory in self.directories:
            dir_path = self.case_path / directory
            if not dir_path.exists():
                missing_dirs.append(directory)
        
        if missing_dirs:
            print(f"   ❌ Missing directories: {missing_dirs}")
            return False
        
        # Check critical files (from config)
        critical_files = ["inspiration_pool.json"]
        mandatory_files = self.config_manager.get_mandatory_files()
        for directory, files in mandatory_files.items():
            for file in files:
                critical_files.append(f"{directory}/{file}")
        
        missing_files = []
        for file_path in critical_files:
            full_path = self.case_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"   ❌ Missing files: {missing_files}")
            return False
        
        print(f"   ✅ Case structure validation passed")
        return True
    
    def print_next_steps(self):
        """Print guidance for manual steps"""
        print(f"\n🎯 CASE SCAFFOLDING COMPLETE!")
        print(f"\n📊 CASE STRUCTURE:")
        case_config = self.config_manager.get_case_length_config(self.case_length)
        print(f"   📅 Case Length: {self.case_length} day{'s' if self.case_length > 1 else ''} - {case_config.get('name', 'Unknown')}")
        print(f"   🎮 Total Gates: {len(self.create_investigation_gates())}")
        print(f"   ⏱️  Estimated Time: {case_config.get('estimated_time', 'unknown')}")
        print(f"   📝 Description: {case_config.get('description', 'No description available')}")
        print(f"\n📋 NEXT STEPS (Manual):")
        print(f"   1. Run real-life inspiration: python scripts/real_life_inspiration.py --encrypt")
        print(f"   2. Fill out backbone template files in {self.case_name}/backbone/")
        print(f"   3. Customize ChatGPT prompts in chatgpt_*_request.json files")
        print(f"   4. Run ChatGPT consultations for obstacles and trial fabrications")
        print(f"   5. Complete solution files and validate case integrity")
        print(f"\n📁 Case directory: {self.case_path}")
        print(f"🎲 Inspiration pool: {self.case_path}/inspiration_pool.json")
    
    def scaffold_case(self):
        """Run the complete scaffolding process"""
        print(f"🏗️  Starting case scaffolding for '{self.case_name}'...\n")
        
        try:
            # Create directory structure
            self.create_directory_structure()
            
            # Generate inspiration pool
            if not self.generate_inspiration_pool():
                return False
            
            # Create template files
            self.create_backbone_templates()
            self.create_game_state_files()
            self.create_solution_templates()
            self.create_chatgpt_request_templates()
            
            # Validate structure
            if not self.validate_structure():
                return False
            
            # Print next steps
            self.print_next_steps()
            
            return True
            
        except Exception as e:
            print(f"❌ Error during scaffolding: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Generate case scaffolding for new Ace Attorney game')
    parser.add_argument('case_name', help='Name of the new case (use lowercase_with_underscores)')
    parser.add_argument('--base-path', default='.', help='Base directory path (default: current directory)')
    
    args = parser.parse_args()
    
    # Validate case name format
    if not args.case_name.replace('_', '').replace('-', '').isalnum():
        print("❌ Case name should use lowercase_with_underscores format")
        sys.exit(1)
    
    # Create scaffolding
    scaffolder = CaseScaffolding(args.case_name, args.base_path)
    success = scaffolder.scaffold_case()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()