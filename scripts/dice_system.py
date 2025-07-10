#!/usr/bin/env python3
"""
Dice Rolling System for Ace Attorney Mystery Games

Provides D&D-style dice rolling functionality to add meaningful failure chances
to player actions, preventing cases from ending too early due to effortless success.
"""

import random
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

class DiceRoller:
    """Handles dice rolling with modifiers and logging for game actions."""
    
    def __init__(self, case_directory: str = None):
        """Initialize dice roller with optional case directory for logging."""
        self.case_directory = case_directory
        self.roll_history = self._load_roll_history()
        
    def roll_d20(self, modifier: int = 0, description: str = "") -> Dict[str, Any]:
        """
        Roll a d20 with optional modifier.
        
        Args:
            modifier: Bonus/penalty to add to roll (-10 to +10 recommended)
            description: Description of what this roll is for
            
        Returns:
            Dict containing roll result, modifier, total, and metadata
        """
        base_roll = random.randint(1, 20)
        total = max(1, min(20, base_roll + modifier))  # Clamp between 1-20
        
        result = {
            "base_roll": base_roll,
            "modifier": modifier,
            "total": total,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "success_level": self._assess_success(total)
        }
        
        self.roll_history.append(result)
        
        if self.case_directory:
            self._log_roll(result)
            
        return result
    
    def _assess_success(self, total: int) -> str:
        """Assess the success level based on total roll."""
        if total >= 18:
            return "critical_success"
        elif total >= 15:
            return "great_success"
        elif total >= 12:
            return "success"
        elif total >= 8:
            return "partial_success"
        elif total >= 5:
            return "failure"
        elif total >= 2:
            return "bad_failure"
        else:
            return "critical_failure"
    
    def _log_roll(self, result: Dict[str, Any]):
        """Log the roll result to the case directory."""
        if not self.case_directory:
            return
            
        log_dir = os.path.join(self.case_directory, "game_state")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "dice_rolls.json")
        
        # Load existing rolls or create new list
        rolls = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    rolls = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                rolls = []
        
        rolls.append(result)
        
        # Keep only last 100 rolls to prevent file bloat
        if len(rolls) > 100:
            rolls = rolls[-100:]
        
        with open(log_file, 'w') as f:
            json.dump(rolls, f, indent=2)
    
    def get_difficulty_modifier(self, difficulty: str) -> int:
        """Get recommended modifier based on difficulty description."""
        difficulty_modifiers = {
            "trivial": 5,
            "easy": 3,
            "moderate": 0,
            "hard": -2,
            "very_hard": -4,
            "nearly_impossible": -6
        }
        return difficulty_modifiers.get(difficulty.lower(), 0)
    
    def get_evidence_modifier(self, evidence_count: int) -> int:
        """Get modifier based on relevant evidence count."""
        if evidence_count >= 3:
            return 3
        elif evidence_count == 2:
            return 2
        elif evidence_count == 1:
            return 1
        else:
            return 0
    
    def get_trust_modifier(self, trust_level: int) -> int:
        """Get modifier based on character trust level."""
        if trust_level >= 8:
            return 3
        elif trust_level >= 5:
            return 1
        elif trust_level >= 0:
            return 0
        elif trust_level >= -3:
            return -1
        else:
            return -3
    
    def make_skill_check(self, 
                        target_difficulty: int, 
                        modifier: int = 0, 
                        description: str = "") -> Dict[str, Any]:
        """
        Make a skill check against a target difficulty.
        
        Args:
            target_difficulty: DC (Difficulty Class) to beat (1-20)
            modifier: Bonus/penalty to add to roll
            description: Description of the check
            
        Returns:
            Dict with roll result and success/failure information
        """
        roll_result = self.roll_d20(modifier, description)
        roll_result["target_difficulty"] = target_difficulty
        roll_result["succeeded"] = roll_result["total"] >= target_difficulty
        roll_result["margin"] = roll_result["total"] - target_difficulty
        
        return roll_result
    
    def get_recent_rolls(self, count: int = 5) -> list:
        """Get the most recent dice rolls."""
        return self.roll_history[-count:] if self.roll_history else []
    
    def _load_roll_history(self) -> list:
        """Load existing roll history from file."""
        if not self.case_directory:
            return []
            
        log_file = os.path.join(self.case_directory, "game_state", "dice_rolls.json")
        if not os.path.exists(log_file):
            return []
            
        try:
            with open(log_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []


def main():
    """CLI interface for dice rolling."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dice Rolling System for Mystery Games")
    parser.add_argument("--case-dir", help="Case directory for logging rolls")
    parser.add_argument("--modifier", type=int, default=0, help="Modifier to add to roll")
    parser.add_argument("--description", default="", help="Description of the roll")
    parser.add_argument("--difficulty", help="Difficulty level (trivial/easy/moderate/hard/very_hard/nearly_impossible)")
    parser.add_argument("--evidence-count", type=int, default=0, help="Number of relevant evidence pieces")
    parser.add_argument("--trust-level", type=int, default=0, help="Character trust level (-10 to +10)")
    parser.add_argument("--target", type=int, help="Target difficulty for skill check")
    parser.add_argument("--history", action="store_true", help="Show recent roll history")
    
    args = parser.parse_args()
    
    roller = DiceRoller(args.case_dir)
    
    if args.history:
        if args.case_dir:
            log_file = os.path.join(args.case_dir, "game_state", "dice_rolls.json")
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    rolls = json.load(f)
                    print("Recent Rolls:")
                    for roll in rolls[-5:]:
                        print(f"  {roll['description']}: {roll['base_roll']} + {roll['modifier']} = {roll['total']} ({roll['success_level']})")
            else:
                print("No roll history found.")
        else:
            print("No case directory specified for history.")
        return
    
    # Calculate total modifier
    total_modifier = args.modifier
    
    if args.difficulty:
        total_modifier += roller.get_difficulty_modifier(args.difficulty)
    
    if args.evidence_count > 0:
        total_modifier += roller.get_evidence_modifier(args.evidence_count)
    
    if args.trust_level != 0:
        total_modifier += roller.get_trust_modifier(args.trust_level)
    
    # Make the roll
    if args.target:
        result = roller.make_skill_check(args.target, total_modifier, args.description)
        print(f"Skill Check: {result['description']}")
        print(f"Roll: {result['base_roll']} + {result['modifier']} = {result['total']}")
        print(f"Target: {result['target_difficulty']}")
        print(f"Result: {'SUCCESS' if result['succeeded'] else 'FAILURE'} (margin: {result['margin']})")
        print(f"Level: {result['success_level']}")
    else:
        result = roller.roll_d20(total_modifier, args.description)
        print(f"Roll: {result['description']}")
        print(f"Result: {result['base_roll']} + {result['modifier']} = {result['total']}")
        print(f"Success Level: {result['success_level']}")


if __name__ == "__main__":
    main()