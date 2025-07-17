#!/usr/bin/env python3
"""
CourtRoom CLI - Unified interface for AI Courtroom Mystery Games

Simple, intuitive commands for creating and playing interactive mystery games.
Replaces complex multi-script architecture with single entry point.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add core directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "core"))

from engine import CourtRoomEngine
from ai_director import AIDirector


class CourtRoomCLI:
    """Main CLI interface for CourtRoom game system"""
    
    def __init__(self):
        self.engine = CourtRoomEngine()
        self.ai_director = AIDirector()
    
    def create_case(self, case_name: str, test_mode: bool = False) -> None:
        """Create a new mystery case"""
        print(f"Creating new case: {case_name}")
        
        if test_mode:
            print("⚠️  Test mode enabled - case will be isolated")
        
        try:
            case_id = self.engine.create_case(case_name, test_mode=test_mode)
            print(f"✅ Case created successfully: {case_id}")
            print(f"📁 Location: cases/{case_id}/")
            print(f"\nNext step: courtroom play {case_id}")
            
        except Exception as e:
            print(f"❌ Failed to create case: {e}")
            sys.exit(1)
    
    def play_case(self, case_id: str) -> None:
        """Start playing a case from the beginning"""
        print(f"Starting case: {case_id}")
        
        try:
            # Load case and validate
            if not self.engine.case_exists(case_id):
                print(f"❌ Case not found: {case_id}")
                print("Available cases:")
                for case in self.engine.list_cases():
                    print(f"  - {case}")
                sys.exit(1)
            
            # Load case state
            self.engine.load_case(case_id)
            
            # Display opening
            opening = self.engine.get_opening_text()
            print("\n" + "="*60)
            print(opening)
            print("="*60)
            print("\nType 'next' to continue...")
            
            user_input = input("> ").strip().lower()
            if user_input == 'next':
                self.continue_case(case_id)
            else:
                print("Game paused. Use 'courtroom continue' to resume.")
                
        except Exception as e:
            print(f"❌ Failed to start case: {e}")
            sys.exit(1)
    
    def continue_case(self, case_id: str) -> None:
        """Continue playing an existing case"""
        print(f"Continuing case: {case_id}")
        
        try:
            # Load case state
            self.engine.load_case(case_id)
            
            # Get current context and start AI-driven gameplay
            context = self.engine.get_resume_context()
            print(f"\n📋 Current Status: {context['status']}")
            print(f"🎯 Next Actions: {', '.join(context['available_actions'])}")
            
            # Start interactive gameplay loop
            self._interactive_gameplay_loop()
            
        except Exception as e:
            print(f"❌ Failed to continue case: {e}")
            sys.exit(1)
    
    def _interactive_gameplay_loop(self) -> None:
        """Main interactive gameplay loop"""
        print("\n🎮 Interactive mode started. Type 'help' for commands or 'quit' to exit.")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("Game saved. Use 'courtroom continue' to resume.")
                    break
                elif user_input.lower() == 'help':
                    self._show_gameplay_help()
                elif user_input.lower() == 'status':
                    context = self.engine.get_resume_context()
                    print(f"📋 Status: {context['status']}")
                    print(f"🎯 Available: {', '.join(context['available_actions'])}")
                else:
                    # Process input through AI Director
                    response = self.ai_director.process_user_input(
                        user_input, 
                        self.engine.get_current_state()
                    )
                    print(response)
                    
            except KeyboardInterrupt:
                print("\n\nGame paused. Use 'courtroom continue' to resume.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _show_gameplay_help(self) -> None:
        """Show in-game help commands"""
        print("""
🎮 Gameplay Commands:
  status           - Show current case status
  evidence list    - Show all evidence
  evidence add "name" "description" - Add evidence
  character list   - Show all characters  
  character meet "name" "role" - Introduce character
  dice roll "action" - Roll dice for action
  save "name"      - Create save point
  help             - Show this help
  quit             - Exit game
  
💡 You can also type natural language and the AI will interpret it!
""")
    
    def list_cases(self) -> None:
        """List all available cases"""
        cases = self.engine.list_cases()
        if cases:
            print("📁 Available cases:")
            for case in cases:
                status = self.engine.get_case_status(case)
                print(f"  - {case} ({status})")
        else:
            print("📁 No cases found. Create one with: courtroom create \"Case Name\"")
    
    def archive_case(self, case_id: str) -> None:
        """Archive a completed case"""
        try:
            self.engine.archive_case(case_id)
            print(f"📦 Case archived: {case_id}")
        except Exception as e:
            print(f"❌ Failed to archive case: {e}")
            sys.exit(1)
    
    def doctor(self) -> None:
        """Run system health check"""
        print("🏥 Running system health check...")
        
        # Check virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Virtual environment active")
        else:
            print("⚠️  Virtual environment not detected")
        
        # Check dependencies
        try:
            import requests
            import wonderwords
            print("✅ Required packages available")
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
        
        # Check directory structure
        required_dirs = ['core', 'cases', 'tests']
        for dir_name in required_dirs:
            if Path(dir_name).exists():
                print(f"✅ Directory exists: {dir_name}")
            else:
                print(f"❌ Missing directory: {dir_name}")
        
        print("🏥 Health check complete")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='CourtRoom CLI - AI Courtroom Mystery Games',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  courtroom create "The Missing Witness"
  courtroom play the_missing_witness  
  courtroom continue the_missing_witness
  courtroom list
  courtroom doctor
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new case')
    create_parser.add_argument('case_name', help='Name of the case to create')
    create_parser.add_argument('--test-mode', action='store_true', 
                              help='Create in test mode (isolated)')
    
    # Play command
    play_parser = subparsers.add_parser('play', help='Start playing a case')
    play_parser.add_argument('case_id', help='Case ID to play')
    
    # Continue command
    continue_parser = subparsers.add_parser('continue', help='Continue an existing case')
    continue_parser.add_argument('case_id', help='Case ID to continue')
    
    # List command
    subparsers.add_parser('list', help='List all cases')
    
    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Archive a case')
    archive_parser.add_argument('case_id', help='Case ID to archive')
    
    # Doctor command
    subparsers.add_parser('doctor', help='Run system health check')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = CourtRoomCLI()
    
    try:
        if args.command == 'create':
            cli.create_case(args.case_name, test_mode=args.test_mode)
        elif args.command == 'play':
            cli.play_case(args.case_id)
        elif args.command == 'continue':
            cli.continue_case(args.case_id)
        elif args.command == 'list':
            cli.list_cases()
        elif args.command == 'archive':
            cli.archive_case(args.case_id)
        elif args.command == 'doctor':
            cli.doctor()
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        sys.exit(1)


if __name__ == '__main__':
    main()