#!/usr/bin/env python3
"""
Simplified Case Creation - Improvisation-First Strategy
Creates lightweight cases with just real_life_case_summary.txt and case_opening.txt
"""

import json
import os
import subprocess
import sys
from pathlib import Path
import argparse
from datetime import datetime

class SimpleCaseCreator:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        
    def create_case(self):
        """Complete simplified case creation workflow"""
        print("🎲 SIMPLIFIED CASE CREATION - IMPROVISATION FIRST")
        print("=" * 60)
        
        # Step 1: Get real-world inspiration
        print("📚 Fetching real-world legal case for inspiration...")
        try:
            result = subprocess.run([
                "python3", str(Path(__file__).parent / "real_life_inspiration.py")
            ], cwd=self.base_path, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"❌ Inspiration generation failed: {result.stderr}")
                return False
            
            inspiration_content = result.stdout.strip()
            print(f"✅ Real-world legal case fetched ({len(inspiration_content)} characters)")
            
        except subprocess.TimeoutExpired:
            print("❌ Inspiration generation timed out (30s)")
            return False
        except Exception as e:
            print(f"❌ Error generating inspiration: {e}")
            return False
        
        # Step 2: Get case name from user
        print("\n📋 CASE NAME DERIVATION:")
        print("Analyze the legal case content below and derive an appropriate case name.")
        print("Format: 'The [Theme/Location] [Crime/Legal Term]' (e.g., 'The Gallery Gambit')")
        print("Use lowercase_with_underscores for directory name (e.g., 'the_gallery_gambit')")
        print("\n📄 INSPIRATION CONTENT:")
        print("=" * 60)
        print(inspiration_content)
        print("=" * 60)
        
        case_name = input("\n🎯 Enter case name (lowercase_with_underscores): ").strip()
        
        if not case_name or not case_name.replace('_', '').replace('-', '').islower():
            print("❌ Invalid case name format")
            return False
        
        # Step 3: Create case directory
        case_path = self.base_path / case_name
        try:
            case_path.mkdir(exist_ok=True)
            print(f"📁 Created case directory: {case_name}")
        except Exception as e:
            print(f"❌ Failed to create directory: {e}")
            return False
        
        # Step 4: Save real life case summary
        summary_file = case_path / "real_life_case_summary.txt"
        try:
            with open(summary_file, 'w') as f:
                f.write(f"# Real-world inspiration for {case_name}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                f.write(inspiration_content)
            print(f"✅ Saved: real_life_case_summary.txt")
        except Exception as e:
            print(f"❌ Failed to save summary: {e}")
            return False
        
        # Step 5: Generate opening scene via ChatGPT
        print("\n🤖 CHATGPT OPENING SCENE GENERATION:")
        print("Using the summary to generate dramatic opening scene...")
        
        # Prepare ChatGPT prompt
        chatgpt_prompt = f"""below is a summary of a real life legal case selected completely at random from the state records of the new south wales court of appeals. it will be used to inspire a game that is in turn inspired by the Ace Attorney games. the ace attorney games usually begin with a dramatic scene showing a murder. In the Ace Attorney style, write a dramatic opening inspired by these details.

{inspiration_content}"""
        
        print("📝 ChatGPT Prompt prepared:")
        print(f"   Length: {len(chatgpt_prompt)} characters")
        print("   Content: Real life case summary + opening scene request")
        
        # Get ChatGPT API key
        openai_key_file = self.base_path / "openai_key.txt"
        if not openai_key_file.exists():
            print("❌ openai_key.txt not found - cannot generate opening scene")
            return False
        
        try:
            result = subprocess.run([
                "python3", str(Path(__file__).parent / "chatgpt_consultant.py"),
                chatgpt_prompt,
                "--output", str(case_path / "case_opening.txt"),
                "--content-only"
            ], cwd=self.base_path, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"❌ ChatGPT consultation failed: {result.stderr}")
                return False
            
            print("✅ ChatGPT opening scene generated")
            
        except subprocess.TimeoutExpired:
            print("❌ ChatGPT consultation timed out (60s)")
            return False
        except Exception as e:
            print(f"❌ Error during ChatGPT consultation: {e}")
            return False
        
        # Step 6: Append continuation prompt to opening
        opening_file = case_path / "case_opening.txt"
        try:
            with open(opening_file, 'a') as f:
                f.write("\n\ntype 'next' to continue")
            print("✅ Added continuation prompt to opening scene")
        except Exception as e:
            print(f"❌ Failed to append continuation prompt: {e}")
            return False
        
        # Step 7: Create basic game state directory
        game_state_dir = case_path / "game_state"
        try:
            game_state_dir.mkdir(exist_ok=True)
            print("✅ Created game_state directory")
        except Exception as e:
            print(f"❌ Failed to create game_state directory: {e}")
            return False
        
        # Step 8: Success summary
        print(f"\n🎉 CASE CREATION COMPLETE!")
        print("=" * 60)
        print(f"📁 Case: {case_name}")
        print(f"📂 Directory: {case_path}")
        print(f"📄 Files created:")
        print(f"   - real_life_case_summary.txt")
        print(f"   - case_opening.txt")
        print(f"   - game_state/ (directory)")
        
        print(f"\n🎮 READY FOR GAMEPLAY:")
        print(f"▶️  Start: start game {case_name}")
        print(f"📖 Opening: Will display case_opening.txt")
        print(f"🎭 Next scene: Random verb + protagonist activity")
        print(f"🎲 Improvisation: Full game state management + random inspiration available")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Create simplified improvisation-first cases')
    parser.add_argument('--base-path', default='.', help='Base directory path')
    
    args = parser.parse_args()
    
    creator = SimpleCaseCreator(args.base_path)
    success = creator.create_case()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()