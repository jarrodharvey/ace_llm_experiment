#!/usr/bin/env python3
"""
Ace Attorney Mystery Investigation Game V4 - The Uphill Battle
An interactive murder mystery where you play as Phoenix Wright defending a client who appears ABSOLUTELY GUILTY.
"""

import json
import os
import random
from pathlib import Path

class AceAttorneyGameV4:
    def __init__(self):
        self.game_dir = Path(__file__).parent
        self.load_game_data()
        self.current_phase = "briefing"
        self.evidence_discovered = []
        self.witnesses_interviewed = []
        self.locations_visited = []
        self.client_trust = 3
        self.prosecution_pressure = 8
        self.phoenix_morale = "determined_but_worried"
        
    def load_game_data(self):
        """Load all game data from JSON files"""
        try:
            with open(self.game_dir / "case_overview.json") as f:
                self.case_data = json.load(f)
            with open(self.game_dir / "evidence/damning_evidence.json") as f:
                self.evidence_data = json.load(f)
            with open(self.game_dir / "witnesses/hostile_witnesses.json") as f:
                self.witness_data = json.load(f)
            with open(self.game_dir / "locations/investigation_locations.json") as f:
                self.location_data = json.load(f)
            with open(self.game_dir / "witnesses/prosecutor_valentina_vex.json") as f:
                self.prosecutor_data = json.load(f)
            with open(self.game_dir / "witnesses/detective_gumshoe.json") as f:
                self.gumshoe_data = json.load(f)
        except FileNotFoundError as e:
            print(f"Error loading game data: {e}")
            
    def start_game(self):
        """Begin the uphill battle"""
        print("=" * 60)
        print("ACE ATTORNEY MYSTERY INVESTIGATION GAME V4")
        print("THE UPHILL BATTLE")
        print("=" * 60)
        print()
        print("You are Phoenix Wright, defense attorney.")
        print("You've been court-appointed to defend a client who appears ABSOLUTELY GUILTY.")
        print("This is going to be the most difficult case of your career.")
        print()
        print("Type 'help' for commands or 'begin' to start the briefing.")
        
    def briefing_phase(self):
        """Initial case briefing - establish the hopeless situation"""
        print("\n" + "=" * 50)
        print("CASE BRIEFING")
        print("=" * 50)
        print()
        print(f"Case: {self.case_data['case_name']}")
        print(f"Client: {self.case_data['client']['name']}")
        print(f"Victim: {self.case_data['victim']['name']}")
        print()
        print("THE SITUATION:")
        print("Your client, Marcus Ashford, has been charged with murder.")
        print("The evidence against him is... overwhelming.")
        print()
        print("EVIDENCE AGAINST YOUR CLIENT:")
        for evidence in self.case_data['overwhelming_evidence_against_client']['physical_evidence']:
            print(f"• {evidence}")
        print()
        print("MOTIVE:")
        for motive in self.case_data['overwhelming_evidence_against_client']['motive']:
            print(f"• {motive}")
        print()
        print("Even you're starting to doubt his innocence...")
        print("But everyone deserves a defense.")
        print()
        print("Available commands: 'investigate', 'meet_client', 'court', 'help'")
        
    def investigation_phase(self):
        """Handle investigation - make client look MORE guilty"""
        print("\n" + "=" * 50)
        print("INVESTIGATION PHASE")
        print("=" * 50)
        print()
        print("You need to gather evidence for your defense.")
        print("But Prosecutor Valentina Vex has blocked your access to most information.")
        print()
        print("Available locations:")
        for i, location in enumerate(self.location_data['locations'], 1):
            print(f"{i}. {location['name']}")
        print()
        print("Choose a location number, or type 'witnesses' to interview people.")
        
    def visit_location(self, location_index):
        """Visit a location and make things worse for Marcus"""
        if location_index < 1 or location_index > len(self.location_data['locations']):
            print("Invalid location number.")
            return
            
        location = self.location_data['locations'][location_index - 1]
        
        print(f"\n--- {location['name']} ---")
        print(f"Accessibility: {location['accessibility']}")
        print()
        print(f"Investigation outcome: {location['investigation_outcome']}")
        print(f"Information gained: {location['information_gained']}")
        print()
        print(f"How this hurts your case: {location['how_it_makes_case_worse']}")
        print()
        
        if location['name'] not in self.locations_visited:
            self.locations_visited.append(location['name'])
            self.prosecution_pressure += 1
            print(f"Prosecution pressure increased to {self.prosecution_pressure}/10")
            
        if self.prosecution_pressure >= 10:
            print("\nThe case against Marcus looks hopeless...")
            print("You should probably head to court soon.")
            
    def interview_witnesses(self):
        """Interview hostile, uncooperative witnesses"""
        print("\n" + "=" * 50)
        print("WITNESS INTERVIEWS")
        print("=" * 50)
        print()
        print("Available witnesses:")
        for i, witness in enumerate(self.witness_data['witnesses'], 1):
            print(f"{i}. {witness['name']} - {witness['relationship']}")
        print()
        print("Choose a witness number to interview:")
        
    def interview_witness(self, witness_index):
        """Interview a specific witness"""
        if witness_index < 1 or witness_index > len(self.witness_data['witnesses']):
            print("Invalid witness number.")
            return
            
        witness = self.witness_data['witnesses'][witness_index - 1]
        
        print(f"\n--- Interview with {witness['name']} ---")
        print(f"Age: {witness['age']}")
        print(f"Relationship to case: {witness['relationship']}")
        print(f"Cooperation level: {witness['cooperation_level']}")
        print()
        print("Sample quotes:")
        for quote in witness['quotes']:
            print(f'"{quote}"')
        print()
        print(f"How this hurts your case: {witness['how_she_hurts_case'] if 'how_she_hurts_case' in witness else witness['how_he_hurts_case']}")
        
        if witness['name'] not in self.witnesses_interviewed:
            self.witnesses_interviewed.append(witness['name'])
            if witness['cooperation_level'] == 'Hostile':
                self.client_trust -= 1
                print(f"\nClient trust decreased to {self.client_trust}/10")
                
    def meet_with_gumshoe(self):
        """Meet with Detective Gumshoe who wants to help but can't"""
        print("\n--- Meeting with Detective Gumshoe ---")
        print("You find Gumshoe at the precinct, looking nervous.")
        print()
        print('Gumshoe: "Hey there, Phoenix! I wish I could help, but..."')
        print()
        
        random_quote = random.choice(self.gumshoe_data['quotes_during_investigation'])
        print(f'Gumshoe: "{random_quote}"')
        print()
        
        print("What little he can tell you:")
        hint = random.choice(self.gumshoe_data['tiny_hints_he_can_provide'])
        print(f"• {hint}")
        print()
        print("But this information doesn't really help your case...")
        
    def court_phase(self):
        """Enter the trial phase with almost nothing"""
        print("\n" + "=" * 60)
        print("DISTRICT COURT - TRIAL BEGINS")
        print("=" * 60)
        print()
        print("You enter the courtroom with almost no useful evidence.")
        print("Prosecutor Valentina Vex looks supremely confident.")
        print("Your client Marcus appears resigned to his fate.")
        print()
        print("The judge gavels the court to order.")
        print()
        print("This is where the real battle begins...")
        print("Your only hope is to find flaws in the prosecution's case through cross-examination.")
        print()
        print("Available commands: 'opening', 'prosecution_case', 'defense_case', 'help'")
        
    def show_help(self):
        """Show available commands"""
        print("\n--- AVAILABLE COMMANDS ---")
        print("help - Show this help message")
        print("begin - Start the case briefing")
        print("investigate - Begin investigation phase")
        print("meet_client - Meet with your client")
        print("court - Enter the courtroom")
        print("witnesses - Interview witnesses")
        print("gumshoe - Meet with Detective Gumshoe")
        print("status - Check current case status")
        print("! - Enter troubleshooting mode")
        print("quit - End the game")
        
    def show_status(self):
        """Show current game status"""
        print(f"\n--- CASE STATUS ---")
        print(f"Phase: {self.current_phase}")
        print(f"Client Trust: {self.client_trust}/10")
        print(f"Prosecution Pressure: {self.prosecution_pressure}/10")
        print(f"Evidence Discovered: {len(self.evidence_discovered)}")
        print(f"Witnesses Interviewed: {len(self.witnesses_interviewed)}")
        print(f"Locations Visited: {len(self.locations_visited)}")
        print(f"Phoenix's Morale: {self.phoenix_morale}")
        print()
        if self.prosecution_pressure >= 8:
            print("The case looks hopeless. You should head to court.")
        
    def run_game(self):
        """Main game loop"""
        self.start_game()
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'quit':
                    print("Thanks for playing!")
                    break
                elif command == 'help':
                    self.show_help()
                elif command == 'begin':
                    self.briefing_phase()
                    self.current_phase = "investigation"
                elif command == 'investigate':
                    self.investigation_phase()
                elif command == 'witnesses':
                    self.interview_witnesses()
                elif command == 'gumshoe':
                    self.meet_with_gumshoe()
                elif command == 'court':
                    self.court_phase()
                    self.current_phase = "trial"
                elif command == 'status':
                    self.show_status()
                elif command.startswith('location '):
                    try:
                        loc_num = int(command.split()[1])
                        self.visit_location(loc_num)
                    except (ValueError, IndexError):
                        print("Usage: location <number>")
                elif command.startswith('witness '):
                    try:
                        wit_num = int(command.split()[1])
                        self.interview_witness(wit_num)
                    except (ValueError, IndexError):
                        print("Usage: witness <number>")
                elif command == '!':
                    print("TROUBLESHOOTING MODE: Technical support available without spoilers.")
                    print("Type 'help' for commands or 'back' to return to game.")
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nThanks for playing!")
                break
            except Exception as e:
                print(f"Error: {e}")
                print("Type 'help' for available commands.")

if __name__ == "__main__":
    game = AceAttorneyGameV4()
    game.run_game()