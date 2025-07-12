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
        # Include inspiration data in state if available
        state_data = data or {}
        if self.inspiration_data and "inspiration_data" not in state_data:
            state_data["inspiration_data"] = self.inspiration_data
        
        state = {
            "case_name": self.case_name,
            "current_phase": phase,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "data": state_data
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
            
            # Restore inspiration data if available
            data = state.get("data", {})
            if "inspiration_data" in data:
                self.inspiration_data = data["inspiration_data"]
            
            return state.get("current_phase"), state.get("status"), data
        except FileNotFoundError:
            return None, None, {}
        except json.JSONDecodeError as e:
            print(f"❌ Corrupted state file: {e}")
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
        
        # Ensure case_path is set from case_name
        if not self.case_path and self.case_name:
            self.case_path = self.base_path / self.case_name
        
        if not self.case_path:
            print("❌ Case path not available. Cannot proceed with Phase 2.")
            return False
        
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
        
        # Ensure case_path is set from case_name
        if not self.case_path and self.case_name:
            self.case_path = self.base_path / self.case_name
        
        if not self.case_path:
            print("❌ Case path not available. Cannot proceed with Phase 3.")
            return False
        
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
            
            # Check if files were saved to wrong location (common issue)
            root_obstacles_dir = self.base_path / "obstacles"
            if root_obstacles_dir.exists():
                print("\n🔍 Checking for misplaced files...")
                misplaced_files = []
                if (root_obstacles_dir / "chatgpt_obstacles_v1.json").exists():
                    misplaced_files.append("chatgpt_obstacles_v1.json")
                if (root_obstacles_dir / "trial_fabrications.json").exists():
                    misplaced_files.append("trial_fabrications.json")
                
                if misplaced_files:
                    print(f"📁 Found misplaced files in root obstacles directory: {misplaced_files}")
                    print("🔧 Attempting to move files to correct location...")
                    try:
                        for filename in misplaced_files:
                            src = root_obstacles_dir / filename
                            dst = self.case_path / "obstacles" / filename
                            src.rename(dst)
                            print(f"✅ Moved: {filename}")
                        print("🎯 File relocation successful, continuing...")
                        # Re-check after moving
                        missing_outputs = []
                        if not obstacle_file.exists():
                            missing_outputs.append("investigation obstacles")
                        if not trial_file.exists():
                            missing_outputs.append("trial fabrications")
                        if missing_outputs:
                            return False
                    except Exception as e:
                        print(f"❌ Failed to move files: {e}")
                        return False
                else:
                    return False
            else:
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
        
        # Attempt automatic BASE64 encoding
        solution_dir = self.case_path / "solution"
        if solution_dir.exists():
            print("\n🔧 Attempting automatic BASE64 encoding...")
            try:
                for json_file in solution_dir.glob("*.json"):
                    if not json_file.name.endswith(".b64"):
                        b64_file = solution_dir / f"{json_file.name}.b64"
                        with open(json_file, 'rb') as f:
                            encoded_content = base64.b64encode(f.read())
                        with open(b64_file, 'wb') as f:
                            f.write(encoded_content)
                        print(f"✅ Encoded: {json_file.name}")
                print("🎯 BASE64 encoding completed automatically")
            except Exception as e:
                print(f"⚠️  Automatic encoding failed: {e}")
                print("   Please encode manually as described above")
        
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
            print(f"🧹 Cleaned up state file: {self.state_file}")
        
        return True
    
    def recovery_diagnose(self, case_name):
        """Diagnose what went wrong with case creation"""
        print(f"\n🔍 RECOVERY MODE: DIAGNOSE")
        print("=" * 60)
        print(f"📁 Analyzing case: {case_name}")
        
        case_path = self.base_path / case_name
        if not case_path.exists():
            print(f"❌ Case directory not found: {case_path}")
            return False
        
        # Check for state files
        state_files = list(self.base_path.glob("case_creation_state_*.json"))
        print(f"\n🗂️  Found {len(state_files)} state files:")
        for state_file in sorted(state_files, key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                if state.get("case_name") == case_name:
                    print(f"✅ {state_file.name}: Phase {state.get('current_phase', 'unknown')}, Status: {state.get('status', 'unknown')}")
                else:
                    print(f"   {state_file.name}: Different case ({state.get('case_name', 'unknown')})")
            except Exception as e:
                print(f"❌ {state_file.name}: Corrupted ({e})")
        
        # Check directory structure
        print(f"\n📂 Directory Structure Analysis:")
        required_dirs = ["backbone", "obstacles", "solution", "game_state", "saves"]
        for dir_name in required_dirs:
            dir_path = case_path / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.glob("*")))
                print(f"✅ {dir_name}/ ({file_count} files)")
            else:
                print(f"❌ {dir_name}/ (missing)")
        
        # Check backbone files
        print(f"\n🦴 Backbone Files Analysis:")
        backbone_files = [
            "case_structure.json", "character_facts.json", "evidence_chain.json",
            "truth_timeline.json", "witness_testimonies.json", "trial_structure.json"
        ]
        backbone_complete = True
        for filename in backbone_files:
            file_path = case_path / "backbone" / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = json.load(f)
                    # Check if file has template placeholders
                    content_str = json.dumps(content)
                    if "[" in content_str and "]" in content_str:
                        print(f"⚠️  {filename}: Contains template placeholders")
                        backbone_complete = False
                    else:
                        print(f"✅ {filename}: Complete")
                except Exception as e:
                    print(f"❌ {filename}: Error reading ({e})")
                    backbone_complete = False
            else:
                print(f"❌ {filename}: Missing")
                backbone_complete = False
        
        # Check ChatGPT outputs
        print(f"\n🤖 ChatGPT Outputs Analysis:")
        chatgpt_files = ["chatgpt_obstacles_v1.json", "trial_fabrications.json"]
        chatgpt_complete = True
        for filename in chatgpt_files:
            file_path = case_path / "obstacles" / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = json.load(f)
                    if content.get("success"):
                        print(f"✅ {filename}: Complete")
                    else:
                        print(f"⚠️  {filename}: May have errors")
                        chatgpt_complete = False
                except Exception as e:
                    print(f"❌ {filename}: Error reading ({e})")
                    chatgpt_complete = False
            else:
                # Check if in wrong location
                wrong_path = self.base_path / "obstacles" / filename
                if wrong_path.exists():
                    print(f"📁 {filename}: Found in wrong location (root/obstacles/)")
                    chatgpt_complete = False
                else:
                    print(f"❌ {filename}: Missing")
                    chatgpt_complete = False
        
        # Check solution files
        print(f"\n✅ Solution Files Analysis:")
        solution_files = ["evidence_requirements.json", "character_behaviors.json", "integrated_case.json"]
        solution_complete = True
        for filename in solution_files:
            file_path = case_path / "solution" / filename
            b64_path = case_path / "solution" / f"{filename}.b64"
            if file_path.exists():
                if b64_path.exists():
                    print(f"✅ {filename}: Complete (with BASE64)")
                else:
                    print(f"⚠️  {filename}: Missing BASE64 encoding")
            else:
                print(f"❌ {filename}: Missing")
                solution_complete = False
        
        # Recommendations
        print(f"\n💡 RECOVERY RECOMMENDATIONS:")
        if not backbone_complete:
            print("🔧 Run: --recovery fix-files (will attempt to repair backbone)")
        if not chatgpt_complete:
            print("🔧 Run: --recovery reset-phase (restart from Phase 2)")
        if not solution_complete:
            print("🔧 Run: --recovery reset-phase (restart from Phase 3)")
        if backbone_complete and chatgpt_complete and solution_complete:
            print("🎯 Case appears complete - try resuming with --phase complete")
        
        return True
    
    def recovery_reset_phase(self, case_name):
        """Reset case to previous phase"""
        print(f"\n🔄 RECOVERY MODE: RESET PHASE")
        print("=" * 60)
        
        case_path = self.base_path / case_name
        if not case_path.exists():
            print(f"❌ Case directory not found: {case_path}")
            return False
        
        # Find most recent state file for this case
        state_files = list(self.base_path.glob("case_creation_state_*.json"))
        target_state = None
        for state_file in sorted(state_files, key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                if state.get("case_name") == case_name:
                    target_state = state_file
                    break
            except:
                continue
        
        if not target_state:
            print(f"❌ No state file found for case: {case_name}")
            return False
        
        with open(target_state, 'r') as f:
            state = json.load(f)
        
        current_phase = state.get("current_phase")
        print(f"📊 Current phase: {current_phase}")
        
        # Determine reset target
        if current_phase == "phase_3":
            reset_phase = "phase_2"
            print("🎯 Resetting to Phase 2 (ChatGPT consultations)")
            # Clear solution files
            solution_dir = case_path / "solution"
            if solution_dir.exists():
                for file in solution_dir.glob("*.json"):
                    if file.name not in ["evidence_requirements.json", "character_behaviors.json", "integrated_case.json"]:
                        continue
                    try:
                        file.unlink()
                        print(f"🗑️  Removed: {file.name}")
                    except:
                        pass
                for file in solution_dir.glob("*.b64"):
                    try:
                        file.unlink()
                        print(f"🗑️  Removed: {file.name}")
                    except:
                        pass
        elif current_phase == "phase_2":
            reset_phase = "phase_1"
            print("🎯 Resetting to Phase 1 (Backbone completion)")
            # Clear ChatGPT outputs
            obstacles_dir = case_path / "obstacles"
            if obstacles_dir.exists():
                for file in obstacles_dir.glob("*.json"):
                    try:
                        file.unlink()
                        print(f"🗑️  Removed: {file.name}")
                    except:
                        pass
        else:
            print(f"❌ Cannot reset from phase: {current_phase}")
            return False
        
        # Update state file
        state["current_phase"] = reset_phase
        state["status"] = "reset_recovery"
        state["timestamp"] = datetime.now().isoformat()
        
        with open(target_state, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"✅ Reset complete. Resume with:")
        print(f"   python3 scripts/create_new_game_orchestrator.py --resume {target_state.name} --phase {reset_phase}")
        
        return True
    
    def recovery_fix_files(self, case_name):
        """Attempt to fix common file issues"""
        print(f"\n🔧 RECOVERY MODE: FIX FILES")
        print("=" * 60)
        
        case_path = self.base_path / case_name
        if not case_path.exists():
            print(f"❌ Case directory not found: {case_path}")
            return False
        
        fixes_applied = 0
        
        # Fix 1: Move misplaced ChatGPT outputs
        root_obstacles = self.base_path / "obstacles"
        case_obstacles = case_path / "obstacles"
        if root_obstacles.exists() and case_obstacles.exists():
            for filename in ["chatgpt_obstacles_v1.json", "trial_fabrications.json"]:
                src = root_obstacles / filename
                dst = case_obstacles / filename
                if src.exists() and not dst.exists():
                    try:
                        src.rename(dst)
                        print(f"✅ Moved: {filename} to correct location")
                        fixes_applied += 1
                    except Exception as e:
                        print(f"❌ Failed to move {filename}: {e}")
        
        # Fix 2: Create missing directories
        required_dirs = ["backbone", "obstacles", "solution", "game_state", "saves"]
        for dir_name in required_dirs:
            dir_path = case_path / dir_name
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Created missing directory: {dir_name}/")
                    fixes_applied += 1
                except Exception as e:
                    print(f"❌ Failed to create {dir_name}/: {e}")
        
        # Fix 3: Encode solution files if missing BASE64
        solution_dir = case_path / "solution"
        if solution_dir.exists():
            for json_file in solution_dir.glob("*.json"):
                if json_file.name.endswith(".b64"):
                    continue
                b64_file = solution_dir / f"{json_file.name}.b64"
                if not b64_file.exists():
                    try:
                        with open(json_file, 'rb') as f:
                            encoded_content = base64.b64encode(f.read())
                        with open(b64_file, 'wb') as f:
                            f.write(encoded_content)
                        print(f"✅ Encoded: {json_file.name}")
                        fixes_applied += 1
                    except Exception as e:
                        print(f"❌ Failed to encode {json_file.name}: {e}")
        
        # Fix 4: Initialize game state if missing
        game_state_dir = case_path / "game_state"
        if game_state_dir.exists():
            required_states = ["investigation_progress.json", "trial_progress.json"]
            for state_file in required_states:
                state_path = game_state_dir / state_file
                if not state_path.exists():
                    try:
                        # Create minimal game state
                        initial_state = {
                            "case_id": case_name,
                            "current_phase": "investigation" if "investigation" in state_file else "trial",
                            "gates_completed": [],
                            "evidence_found": [],
                            "character_trust_levels": {},
                            "created": datetime.now().isoformat()
                        }
                        with open(state_path, 'w') as f:
                            json.dump(initial_state, f, indent=2)
                        print(f"✅ Initialized: {state_file}")
                        fixes_applied += 1
                    except Exception as e:
                        print(f"❌ Failed to initialize {state_file}: {e}")
        
        print(f"\n🎯 Applied {fixes_applied} fixes")
        if fixes_applied > 0:
            print("💡 Try running --recovery diagnose again to verify fixes")
        else:
            print("💡 No automatic fixes available - may need manual intervention")
        
        return fixes_applied > 0
    
    def recovery_clean_start(self, case_name):
        """Clean start - remove case and restart from inspiration"""
        print(f"\n🗑️  RECOVERY MODE: CLEAN START")
        print("=" * 60)
        print(f"⚠️  This will DELETE the entire case directory: {case_name}")
        print("📋 You will need to restart from the inspiration phase")
        
        case_path = self.base_path / case_name
        if not case_path.exists():
            print(f"❌ Case directory not found: {case_path}")
            return False
        
        # Safety confirmation
        print(f"\n💀 DESTRUCTIVE OPERATION WARNING")
        print(f"📁 Target: {case_path}")
        print(f"🔄 After deletion, restart with: python3 scripts/create_new_game_orchestrator.py")
        print(f"\n🛡️  Type 'DELETE {case_name}' to confirm:")
        
        try:
            response = input().strip()
            if response != f"DELETE {case_name}":
                print("❌ Confirmation failed - operation cancelled")
                return False
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Operation cancelled")
            return False
        
        # Remove case directory
        try:
            import shutil
            shutil.rmtree(case_path)
            print(f"✅ Deleted case directory: {case_name}")
            
            # Clean up related state files
            state_files = list(self.base_path.glob("case_creation_state_*.json"))
            for state_file in state_files:
                try:
                    with open(state_file, 'r') as f:
                        state = json.load(f)
                    if state.get("case_name") == case_name:
                        state_file.unlink()
                        print(f"✅ Deleted state file: {state_file.name}")
                except:
                    continue
            
            print(f"\n🎯 Clean start complete. Restart case creation with:")
            print(f"   python3 scripts/create_new_game_orchestrator.py")
            
        except Exception as e:
            print(f"❌ Failed to delete case: {e}")
            return False
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Orchestrate inspiration-first case creation')
    parser.add_argument('--resume', help='Resume from state file')
    parser.add_argument('--case-name', help='Case name for Phase 1 (after inspiration analysis)')
    parser.add_argument('--phase', help='Jump to specific phase (phase_2, phase_3, complete)')
    parser.add_argument('--recovery', choices=['diagnose', 'reset-phase', 'fix-files', 'clean-start'], 
                       help='Recovery mode for failed case creation')
    parser.add_argument('--target-case', help='Case directory for recovery operations')
    parser.add_argument('--base-path', default='.', help='Base directory path')
    
    args = parser.parse_args()
    
    orchestrator = CaseCreationOrchestrator(args.base_path)
    
    # Handle recovery mode
    if args.recovery:
        if not args.target_case:
            print("❌ --target-case required for recovery operations")
            sys.exit(1)
        
        if args.recovery == "diagnose":
            success = orchestrator.recovery_diagnose(args.target_case)
        elif args.recovery == "reset-phase":
            success = orchestrator.recovery_reset_phase(args.target_case)
        elif args.recovery == "fix-files":
            success = orchestrator.recovery_fix_files(args.target_case)
        elif args.recovery == "clean-start":
            success = orchestrator.recovery_clean_start(args.target_case)
        
        sys.exit(0 if success else 1)
    
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