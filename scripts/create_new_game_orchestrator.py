#!/usr/bin/env python3
"""
Case Creation Orchestrator
Manages the inspiration-first case creation process with strategic pause points for Claude intervention.
"""

import json
import os
import subprocess
import sys
import base64
from pathlib import Path
import argparse
from datetime import datetime

class CaseCreationOrchestrator:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.case_name = None
        self.case_path = None
        self.inspiration_data = None
        self.state_file = None
        
    def save_state(self, phase, status, data=None):
        """Save orchestration state for resuming"""
        state = {
            "case_name": self.case_name,
            "current_phase": phase,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        if self.state_file:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
    
    def load_state(self, state_file_path):
        """Load orchestration state for resuming"""
        try:
            with open(state_file_path, 'r') as f:
                state = json.load(f)
            
            self.case_name = state.get("case_name")
            self.case_path = self.base_path / self.case_name if self.case_name else None
            self.state_file = state_file_path
            
            return state.get("current_phase"), state.get("status"), state.get("data", {})
        except FileNotFoundError:
            return None, None, {}
    
    def phase_0_inspiration_generation(self):
        """Phase 0: Generate real-world inspiration for case creation"""
        print("🎲 PHASE 0: REAL-WORLD INSPIRATION GENERATION")
        print("=" * 60)
        
        # Generate real-life inspiration (unencrypted for Claude analysis)
        print("📚 Fetching real-world legal case for inspiration...")
        try:
            result = subprocess.run([
                "python3", str(Path(__file__).parent / "real_life_inspiration.py")
            ], cwd=self.base_path, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"❌ Inspiration generation failed: {result.stderr}")
                return False
            
            # Store inspiration data
            self.inspiration_data = result.stdout.strip()
            print("✅ Real-world legal case fetched successfully")
            print(f"📄 Case content: {len(self.inspiration_data)} characters")
            
        except subprocess.TimeoutExpired:
            print("❌ Inspiration generation timed out (30s)")
            return False
        except Exception as e:
            print(f"❌ Error generating inspiration: {e}")
            return False
        
        # Create timestamped state file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.state_file = self.base_path / f"case_creation_state_{timestamp}.json"
        
        # Save state and pause for Claude intervention
        self.save_state("phase_0", "inspiration_ready", {
            "inspiration_data": self.inspiration_data
        })
        
        print("\n🛑 CLAUDE INTERVENTION REQUIRED")
        print("=" * 60)
        print("📋 CLAUDE'S TASKS:")
        print("1. Analyze the legal case content below")
        print("2. Identify key themes: crime type, setting, legal issues, character dynamics")
        print("3. Derive an appropriate case name based on themes")
        print("4. Format: 'The [Theme/Location] [Crime/Legal Term]' (e.g., 'The Gallery Gambit')")
        print("5. Continue with: python3 scripts/create_new_game_orchestrator.py --resume <state_file> --case-name <chosen_name>")
        print(f"\n📁 State file: {self.state_file}")
        print(f"\n📄 INSPIRATION CONTENT:")
        print("=" * 60)
        print(self.inspiration_data)
        print("=" * 60)
        
        return True
    
    def phase_1_case_scaffolding(self, case_name):
        """Phase 1: Create case scaffolding with inspiration context"""
        print(f"\n🏗️ PHASE 1: CASE SCAFFOLDING")
        print("=" * 60)
        
        self.case_name = case_name
        self.case_path = self.base_path / case_name
        
        # Validate case name format
        if not case_name.replace('_', '').replace('-', '').isalnum():
            print(f"❌ Invalid case name format: {case_name}")
            print("Use lowercase_with_underscores format (e.g., 'the_gallery_gambit')")
            return False
        
        # Run case scaffolding
        print(f"📁 Creating scaffolding for case: {case_name}")
        try:
            result = subprocess.run([
                "python3", str(Path(__file__).parent / "case_scaffolding.py"), 
                case_name
            ], cwd=self.base_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Scaffolding failed: {result.stderr}")
                return False
            
            print("✅ Case scaffolding completed successfully")
            # Don't print full stdout as it's verbose, just confirm success
            
        except Exception as e:
            print(f"❌ Error during scaffolding: {e}")
            return False
        
        # Save inspiration data to case directory for reference
        inspiration_file = self.case_path / "real_life_inspiration.txt"
        with open(inspiration_file, 'w') as f:
            f.write(f"# Real-world inspiration for {case_name}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
            f.write(self.inspiration_data)
        
        # Save state and pause for Claude intervention
        self.save_state("phase_1", "scaffolding_complete", {
            "case_name": case_name,
            "inspiration_saved": str(inspiration_file)
        })
        
        print("\n🛑 CLAUDE INTERVENTION REQUIRED")
        print("=" * 60)
        print("📋 CLAUDE'S TASKS:")
        print("1. Fill out backbone template files with creative content:")
        print(f"   📄 {case_name}/backbone/case_structure.json")
        print(f"   👥 {case_name}/backbone/character_facts.json")
        print(f"   🔍 {case_name}/backbone/evidence_chain.json") 
        print(f"   ⏰ {case_name}/backbone/truth_timeline.json")
        print(f"   👁️ {case_name}/backbone/witness_testimonies.json")
        print(f"   ⚖️ {case_name}/backbone/trial_structure.json")
        print(f"2. Use inspiration from: {inspiration_file}")
        print("3. Create logical, consistent case foundation")
        print("4. Continue with: python3 scripts/create_new_game_orchestrator.py --resume <state_file> --phase phase_2")
        
        return True
    
    def phase_2_chatgpt_preparation(self):
        """Phase 2: Prepare for ChatGPT consultation"""
        print(f"\n🤖 PHASE 2: CHATGPT CONSULTATION PREPARATION")
        print("=" * 60)
        
        # Verify backbone files exist
        backbone_files = [
            "case_structure.json",
            "evidence_chain.json", 
            "character_facts.json",
            "truth_timeline.json",
            "witness_testimonies.json",
            "trial_structure.json"
        ]
        
        missing_files = []
        for filename in backbone_files:
            file_path = self.case_path / "backbone" / filename
            if not file_path.exists():
                missing_files.append(filename)
            elif file_path.stat().st_size < 100:  # Check if file is just template
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if "[" in content and "]" in content:  # Contains template placeholders
                            missing_files.append(f"{filename} (template not filled)")
                except:
                    missing_files.append(f"{filename} (unreadable)")
        
        if missing_files:
            print(f"❌ Backbone files need completion: {missing_files}")
            print("Claude must complete Phase 1 backbone creation first")
            return False
        
        print("✅ All backbone files present and filled out")
        
        # Load ChatGPT request templates
        obstacle_template = self.case_path / "chatgpt_obstacle_request.json"
        trial_template = self.case_path / "chatgpt_trial_request.json"
        
        if not obstacle_template.exists() or not trial_template.exists():
            print("❌ ChatGPT request templates missing from scaffolding")
            return False
        
        # Save state and pause for Claude intervention
        self.save_state("phase_2", "backbone_ready", {
            "backbone_files_verified": True
        })
        
        print("\n🛑 CLAUDE INTERVENTION REQUIRED")
        print("=" * 60)
        print("📋 CLAUDE'S TASKS:")
        print("1. Summarize backbone files for ChatGPT prompts")
        print("2. Fill and customize ChatGPT consultation requests:")
        print(f"   🚧 {obstacle_template}")
        print(f"   ⚖️ {trial_template}")
        print("3. Run ChatGPT consultations using the templates")
        print("4. Ensure ChatGPT outputs are saved to:")
        print(f"   📄 {self.case_name}/obstacles/chatgpt_obstacles_v1.json")
        print(f"   ⚖️ {self.case_name}/obstacles/trial_fabrications.json")
        print("5. Continue with: python3 scripts/create_new_game_orchestrator.py --resume <state_file> --phase phase_3")
        
        return True
    
    def phase_3_validation_and_completion(self):
        """Phase 3: Validate and complete case creation"""
        print(f"\n🔍 PHASE 3: VALIDATION & COMPLETION")
        print("=" * 60)
        
        # Verify ChatGPT outputs exist
        obstacle_file = self.case_path / "obstacles" / "chatgpt_obstacles_v1.json"
        trial_file = self.case_path / "obstacles" / "trial_fabrications.json"
        
        missing_outputs = []
        if not obstacle_file.exists():
            missing_outputs.append("investigation obstacles")
        if not trial_file.exists():
            missing_outputs.append("trial fabrications")
        
        if missing_outputs:
            print(f"❌ Missing ChatGPT outputs: {missing_outputs}")
            print("Claude must complete Phase 2 ChatGPT consultations first")
            return False
        
        print("✅ ChatGPT consultation outputs present")
        
        # Save state and pause for Claude intervention
        self.save_state("phase_3", "chatgpt_complete", {
            "obstacles_ready": True,
            "trial_fabrications_ready": True
        })
        
        print("\n🛑 CLAUDE INTERVENTION REQUIRED")
        print("=" * 60)
        print("📋 CLAUDE'S TASKS:")
        print("1. Validate obstacles against logical backbone")
        print("2. Ensure fabricated lies are contradictable by evidence")
        print("3. Complete and encode solution files:")
        print(f"   🔍 {self.case_name}/solution/evidence_requirements.json")
        print(f"   👥 {self.case_name}/solution/character_behaviors.json")
        print(f"   ✅ {self.case_name}/solution/integrated_case.json")
        print("4. BASE64 encode solution files for game security")
        print("5. Continue with: python3 scripts/create_new_game_orchestrator.py --resume <state_file> --phase complete")
        
        return True
    
    def phase_complete(self):
        """Final phase: Mark case as complete and ready for gameplay"""
        print(f"\n🎉 CASE CREATION COMPLETE!")
        print("=" * 60)
        
        # Verify solution files exist
        solution_files = [
            "evidence_requirements.json",
            "character_behaviors.json", 
            "integrated_case.json"
        ]
        
        completed_files = []
        missing_files = []
        
        for filename in solution_files:
            file_path = self.case_path / "solution" / filename
            if file_path.exists():
                completed_files.append(filename)
            else:
                missing_files.append(filename)
        
        # Run final validation using game state manager
        print("🔍 Running final case validation...")
        try:
            result = subprocess.run([
                "python3", str(Path(__file__).parent / "game_state_manager.py"),
                str(self.case_path), "--validate"
            ], cwd=self.base_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Case structure validation passed")
            else:
                print(f"⚠️ Validation warnings: {result.stdout}")
                
        except Exception as e:
            print(f"⚠️ Could not run validation: {e}")
        
        # Final summary
        print(f"\n📊 CASE SUMMARY:")
        print(f"📁 Case Name: {self.case_name}")
        print(f"📂 Case Directory: {self.case_path}")
        print(f"✅ Solution Files: {len(completed_files)}/{len(solution_files)} complete")
        if missing_files:
            print(f"⚠️ Missing Files: {missing_files}")
        
        # Show how to start the game
        print(f"\n🎮 READY FOR GAMEPLAY:")
        print(f"▶️ Start: start game {self.case_name}")
        print(f"💾 Save: Use game state manager --save commands during play")
        print(f"🔄 Resume: continue game {self.case_name}")
        
        # Clean up state file
        if self.state_file and os.path.exists(self.state_file):
            os.remove(self.state_file)
            print(f"🧹 Cleaned up state file: {self.state_file.name}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Orchestrate inspiration-first case creation')
    parser.add_argument('--resume', help='Resume from state file')
    parser.add_argument('--case-name', help='Case name for Phase 1 (after inspiration analysis)')
    parser.add_argument('--phase', help='Jump to specific phase (phase_2, phase_3, complete)')
    parser.add_argument('--base-path', default='.', help='Base directory path')
    
    args = parser.parse_args()
    
    orchestrator = CaseCreationOrchestrator(args.base_path)
    
    # Handle resume from state file
    if args.resume:
        if not os.path.exists(args.resume):
            print(f"❌ State file not found: {args.resume}")
            sys.exit(1)
        
        orchestrator.state_file = args.resume
        current_phase, status, data = orchestrator.load_state(args.resume)
        
        if args.phase:
            # Jump to specific phase
            if args.phase == "phase_2":
                success = orchestrator.phase_2_chatgpt_preparation()
            elif args.phase == "phase_3":
                success = orchestrator.phase_3_validation_and_completion()
            elif args.phase == "complete":
                success = orchestrator.phase_complete()
            else:
                print(f"❌ Invalid phase: {args.phase}")
                sys.exit(1)
        elif args.case_name:
            # Continue with case name from Phase 0
            orchestrator.inspiration_data = data.get("inspiration_data", "")
            success = orchestrator.phase_1_case_scaffolding(args.case_name)
        else:
            print("❌ When resuming, specify either --case-name or --phase")
            print("📋 Available phases: phase_2, phase_3, complete")
            sys.exit(1)
    else:
        # Start from beginning
        success = orchestrator.phase_0_inspiration_generation()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()