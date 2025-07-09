#!/usr/bin/env python3
"""
Case Scaffolding Script
Automates the structural aspects of case creation, leaving only creative content for manual input.
"""

import json
import os
import argparse
import sys
from pathlib import Path
import subprocess

class CaseScaffolding:
    def __init__(self, case_name, base_path="."):
        self.case_name = case_name
        self.base_path = Path(base_path)
        self.case_path = self.base_path / case_name
        
        # Required directory structure
        self.directories = [
            "backbone",
            "obstacles", 
            "solution",
            "game_state",
            "evidence"
        ]
        
        # Template files to create
        self.templates = {
            "backbone": [
                "case_structure.json",
                "character_facts.json", 
                "evidence_chain.json",
                "truth_timeline.json",
                "witness_testimonies.json",
                "trial_structure.json"
            ],
            "game_state": [
                "investigation_progress.json",
                "trial_progress.json"
            ],
            "solution": [
                "evidence_requirements.json",
                "character_behaviors.json", 
                "integrated_case.json"
            ]
        }
    
    def create_directory_structure(self):
        """Create the case directory and all subdirectories"""
        print(f"📁 Creating directory structure for '{self.case_name}'...")
        
        # Create main case directory
        self.case_path.mkdir(exist_ok=True)
        print(f"   ✅ Created: {self.case_path}")
        
        # Create subdirectories
        for directory in self.directories:
            dir_path = self.case_path / directory
            dir_path.mkdir(exist_ok=True)
            print(f"   ✅ Created: {dir_path}")
    
    def generate_inspiration_pool(self):
        """Generate random word inspiration pool"""
        print(f"🎲 Generating random word inspiration pool...")
        
        try:
            # Run the random word inspiration script
            result = subprocess.run([
                "python", "scripts/random_word_inspiration.py",
                "--target-dir", str(self.case_path)
            ], cwd=self.base_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Random word inspiration pool generated")
            else:
                print(f"   ❌ Failed to generate inspiration pool: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ❌ Error running inspiration script: {e}")
            return False
        
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
            "investigation_gates": {
                "basic_evidence_gathering": "pending",
                "key_breakthrough": "pending", 
                "conspiracy_exposure": "pending",
                "final_revelation": "pending"
            },
            "evidence_collected": [],
            "witnesses_interviewed": [],
            "psyche_locks_broken": [],
            "character_trust_levels": {},
            "current_location": "detention_center",
            "available_locations": [
                "detention_center"
            ],
            "day": 1,
            "time_until_trial": "3 days",
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
            "prompt_template": "CASE BACKBONE: [Insert backbone summary] Design investigation obstacles that: 1. Make witnesses hostile/uncooperative without breaking logical knowledge 2. Hide evidence behind realistic challenges 3. Create misdirection without contradicting established facts 4. Make client appear MORE guilty initially 5. Force player to work hard for every piece of information 6. Design Psyche-Lock scenarios requiring specific evidence combinations 7. Create story-driven evidence presentation gates EXCITEMENT CHECK: Rate investigation 1-10 for drama and suggest improvements.",
            "command": f"python scripts/chatgpt_consultant.py \"[PROMPT]\" -o obstacles/chatgpt_obstacles_v1.json",
            "notes": "Replace [PROMPT] with filled prompt_template above"
        }
        
        trial_request = {
            "phase": "2B_trial_fabrications", 
            "prompt_template": "You are designing an Ace Attorney courtroom battle. Embrace authentic AA zaniness! TRUE TESTIMONIES: [Insert witness testimonies summary] EVIDENCE LIST: [Insert evidence chain summary] Create fabricated testimonies with AUTHENTIC ACE ATTORNEY FLAIR: 1. THEATRICAL LIES: Add dramatic lies/contradictions with over-the-top confidence 2. EVIDENCE ANCHORS: Each lie must be contradictable by specific evidence 3. ZANY PROSECUTOR: Design prosecutor with impossible quirks 4. DRAMATIC BREAKDOWNS: Spectacular witness meltdowns when lies exposed 5. IMPOSSIBLE BUT LOGICAL: Elements that seem impossible but have logical explanations 6. GALLERY REACTIONS: Colorful characters reacting dramatically 7. JUDGE CHAOS: Judge missing obvious absurdities while focusing on trivial details REFERENCE ACE ATTORNEY SOURCE MATERIAL: Spirit channeling, time travel evidence, impossible crime scenes. EXCITEMENT CHECK: Rate trial 1-10 for AUTHENTIC AA DRAMA and suggest improvements.",
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
        
        # Check critical files
        critical_files = [
            "inspiration_pool.json",
            "backbone/case_structure.json",
            "game_state/investigation_progress.json",
            "solution/integrated_case.json"
        ]
        
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