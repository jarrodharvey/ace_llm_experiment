#!/usr/bin/env python3
"""
Start Game with Validation
Comprehensive game startup script that enforces validation and root cause analysis.
"""

import sys
import os
from pathlib import Path
from start_game_validator import StartGameValidator

def main():
    """Main entry point for validated game startup"""
    if len(sys.argv) != 2:
        print("Usage: python3 start_game_with_validation.py <case_name>")
        print("Example: python3 start_game_with_validation.py the_midnight_masquerade")
        sys.exit(1)
    
    case_name = sys.argv[1]
    
    print("🚀 STARTING GAME WITH COMPREHENSIVE VALIDATION")
    print(f"Case: {case_name}")
    print("="*60)
    
    # Phase 1: Run comprehensive validation
    validator = StartGameValidator(case_name)
    validation_result = validator.run_full_validation()
    
    if not validation_result["valid"]:
        print("\n🛑 GAME START BLOCKED")
        print("Validation failed. You MUST fix all issues before proceeding.")
        print("This enforces the permanent rule: investigate and fix root causes.")
        print("\nDO NOT:")
        print("  - Attempt manual workarounds")
        print("  - Skip validation steps") 
        print("  - Proceed with partial functionality")
        print("\nInstead, follow the next steps above to fix the root causes.")
        sys.exit(1)
    
    # Phase 2: Start the actual game
    print("\n🎮 VALIDATION PASSED - STARTING GAME")
    print("="*60)
    
    # Execute game startup with proper environment
    import subprocess
    
    try:
        # Show opening scene
        opening_file = Path(case_name) / "case_opening.txt"
        if opening_file.exists():
            print("📖 CASE OPENING:")
            print("-" * 40)
            
            try:
                with open(opening_file, 'r') as f:
                    content = f.read()
                    # Handle both plain text and JSON format
                    if content.strip().startswith('{'):
                        import json
                        data = json.loads(content)
                        if "content" in data:
                            print(data["content"])
                        else:
                            print(content)
                    else:
                        print(content)
            except Exception as e:
                print(f"Error reading opening: {e}")
            
            print("-" * 40)
            print("\\nType 'next' to continue")
            
            # Wait for user input
            user_input = input().strip().lower()
            if user_input != 'next':
                print("Game startup cancelled.")
                sys.exit(0)
        
        # Start interactive game session with game state manager
        print("\\n🎯 STARTING INTERACTIVE SESSION")
        print("Remember to follow the forcing function requirements:")
        print("  - Use --must-inspire for ALL improvised content")
        print("  - Use --action-check or --roll for actions with reasonable failure chance")
        print("  - Use --status, --resume, --actions for state management")
        print()
        
        # Launch game state manager in resume mode
        cmd = [sys.executable, "scripts/game_state_manager.py", case_name, "--resume"]
        result = subprocess.run(cmd, cwd=Path.cwd())
        
        if result.returncode != 0:
            print(f"\\n❌ Game session ended with error code {result.returncode}")
            print("This may indicate an issue that needs investigation.")
            sys.exit(result.returncode)
        
        print("\\n✅ Game session completed successfully")
        
    except KeyboardInterrupt:
        print("\\n\\n🛑 Game session interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\\n❌ Unexpected error during game startup: {e}")
        print("This indicates a root cause that needs investigation.")
        sys.exit(1)

if __name__ == "__main__":
    main()