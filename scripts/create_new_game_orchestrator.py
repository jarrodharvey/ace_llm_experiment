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
        
    def _derive_case_name(self, content):
        """Derive case name from legal case content"""
        content_lower = content.lower()
        
        # Look for key terms to build case name
        crime_terms = {
            'murder': 'murder',
            'homicide': 'murder', 
            'kill': 'murder',
            'death': 'murder',
            'fraud': 'fraud',
            'theft': 'theft',
            'robbery': 'robbery',
            'burglary': 'burglary',
            'assault': 'assault',
            'conspiracy': 'conspiracy',
            'import': 'smuggling',
            'drug': 'drug',
            'ecstasy': 'drug',
            'trafficking': 'trafficking',
            'blackmail': 'blackmail',
            'extortion': 'extortion',
            'kidnap': 'kidnapping',
            'arson': 'arson',
            'embezzlement': 'embezzlement'
        }
        
        location_terms = {
            'court': 'courthouse',
            'gallery': 'gallery',
            'museum': 'museum',
            'office': 'office',
            'building': 'tower',
            'hotel': 'hotel',
            'restaurant': 'restaurant',
            'club': 'club',
            'warehouse': 'warehouse',
            'airport': 'airport',
            'hospital': 'hospital',
            'school': 'academy',
            'university': 'academy',
            'bank': 'bank',
            'shop': 'shop',
            'store': 'shop',
            'mall': 'mall',
            'theater': 'theater',
            'theatre': 'theater'
        }
        
        # Find crime type
        crime_type = 'mystery'
        for term, crime in crime_terms.items():
            if term in content_lower:
                crime_type = crime
                break
        
        # Find location or use generic terms
        location = 'midnight'
        for term, loc in location_terms.items():
            if term in content_lower:
                location = loc
                break
        
        # Create case name
        case_name = f"the_{location}_{crime_type}"
        return case_name
    
    def _create_case_summary(self, content):
        """Create a concise case summary from full legal content"""
        # Extract key sections and limit length
        lines = content.split('\n')
        
        # Look for key legal sections
        summary_lines = []
        case_name = ""
        charges = ""
        facts = ""
        
        # Extract case name
        for line in lines[:50]:  # Check first 50 lines
            if ' v ' in line and len(line.split()) < 10:
                case_name = line.strip()
                break
        
        # Extract charges/offences
        for i, line in enumerate(lines):
            if any(term in line.lower() for term in ['charge', 'offence', 'count', 'conviction']):
                charges += line.strip() + " "
                # Get next few lines for context
                for j in range(1, 3):
                    if i + j < len(lines):
                        charges += lines[i + j].strip() + " "
                break
        
        # Extract basic facts (look for common legal section headers)
        in_facts = False
        fact_lines = 0
        for line in lines:
            if any(term in line.lower() for term in ['background', 'facts', 'evidence', 'circumstances']):
                in_facts = True
                continue
            if in_facts and fact_lines < 20:  # Limit facts to 20 lines
                facts += line.strip() + " "
                fact_lines += 1
        
        # Build summary
        summary = f"Case: {case_name}\n\n"
        if charges:
            summary += f"Charges: {charges[:500]}...\n\n"
        if facts:
            summary += f"Key Facts: {facts[:1000]}...\n\n"
        
        # Add first 2000 chars of original content as fallback
        if len(summary) < 500:
            summary += content[:2000] + "..."
        
        # Ensure reasonable length (max 3000 chars)
        if len(summary) > 3000:
            summary = summary[:3000] + "..."
            
        return summary
        
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
        
        # Step 2: Claude analyzes inspiration and derives case name + summary
        print("\n📋 CLAUDE ANALYSIS:")
        print("Claude analyzing inspiration content and creating case summary...")
        
        # Auto-derive case name from content
        case_name = self._derive_case_name(inspiration_content)
        print(f"🎯 Derived case name: {case_name}")
        
        # Create case summary for ChatGPT (this is where Claude analysis would go)
        # For now, truncate to manageable size and extract key elements
        case_summary = self._create_case_summary(inspiration_content)
        print(f"📝 Case summary created ({len(case_summary)} characters)")
        print("\n📄 CASE SUMMARY FOR CHATGPT:")
        print("=" * 60)
        print(case_summary)
        print("=" * 60)
        
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
        
        # Prepare ChatGPT prompt with case summary (not raw content)
        chatgpt_prompt = f"""below is a summary of a real life legal case selected completely at random from the state records of the new south wales court of appeals. it will be used to inspire a game that is in turn inspired by the Ace Attorney games. the ace attorney games usually begin with a dramatic scene showing a murder. In the Ace Attorney style, write a dramatic opening inspired by these details.

{case_summary}"""
        
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