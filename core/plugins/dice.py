"""
Dice System Plugin

Handles probability-based action resolution and dice rolling.
Provides D&D-style mechanics for action success/failure.
"""

import random
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class DicePlugin:
    """Manages dice rolling and action resolution"""
    
    def __init__(self):
        self.roll_history: List[Dict[str, Any]] = []
        self.random = random.Random()  # Use separate random instance for testing
    
    def load_state(self, dice_data: Dict[str, Any]) -> None:
        """Load dice state from game state"""
        self.roll_history = dice_data.get("history", [])
    
    def roll_action(self, action: str, modifiers: List[str] = None) -> Dict[str, Any]:
        """Roll dice for an action with automatic difficulty assessment"""
        
        # Assess action difficulty
        difficulty = self._assess_action_difficulty(action)
        
        # Parse modifiers
        modifier_total = self._parse_modifiers(modifiers or [])
        
        # Roll d20
        roll = self.random.randint(1, 20)
        total = roll + modifier_total
        
        # Determine result
        result = self._determine_result(roll, total, difficulty)
        
        # Create roll record
        roll_record = {
            "action": action,
            "roll": roll,
            "modifiers": modifiers or [],
            "modifier_total": modifier_total,
            "total": total,
            "difficulty": difficulty,
            "result": result["outcome"],
            "description": result["description"],
            "timestamp": datetime.now().isoformat(),
            "critical": roll in [1, 20]
        }
        
        # Add to history
        self.roll_history.append(roll_record)
        
        # Keep only last 50 rolls
        if len(self.roll_history) > 50:
            self.roll_history = self.roll_history[-50:]
        
        return roll_record
    
    def roll_dice(self, dice_expression: str = "1d20") -> Dict[str, Any]:
        """Roll dice with standard notation (e.g., "2d6+3")"""
        
        # Parse dice expression
        dice_parts = self._parse_dice_expression(dice_expression)
        
        # Roll dice
        rolls = []
        for _ in range(dice_parts["count"]):
            roll = self.random.randint(1, dice_parts["sides"])
            rolls.append(roll)
        
        # Calculate total
        dice_total = sum(rolls)
        final_total = dice_total + dice_parts["modifier"]
        
        # Create record
        roll_record = {
            "expression": dice_expression,
            "count": dice_parts["count"],
            "sides": dice_parts["sides"],
            "modifier": dice_parts["modifier"],
            "rolls": rolls,
            "dice_total": dice_total,
            "final_total": final_total,
            "timestamp": datetime.now().isoformat()
        }
        
        self.roll_history.append(roll_record)
        
        return roll_record
    
    def get_action_modifiers(self, evidence_count: int = 0, 
                           character_trust: int = 0,
                           additional_modifier: int = 0) -> int:
        """Calculate standard action modifiers"""
        
        total_modifier = 0
        
        # Evidence bonus (max +3)
        evidence_bonus = min(evidence_count, 3)
        total_modifier += evidence_bonus
        
        # Character trust bonus/penalty
        if character_trust >= 5:
            total_modifier += 3  # Very friendly
        elif character_trust > 0:
            total_modifier += 1  # Friendly
        elif character_trust < -2:
            total_modifier -= 2  # Hostile
        elif character_trust < 0:
            total_modifier -= 1  # Unfriendly
        
        # Additional modifier
        total_modifier += additional_modifier
        
        return total_modifier
    
    def get_recent_rolls(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent dice rolls"""
        return self.roll_history[-count:] if self.roll_history else []
    
    def get_roll_statistics(self) -> Dict[str, Any]:
        """Get statistics about dice rolls"""
        
        if not self.roll_history:
            return {"total_rolls": 0}
        
        # Filter action rolls (vs dice rolls)
        action_rolls = [r for r in self.roll_history if "action" in r]
        
        if not action_rolls:
            return {"total_rolls": len(self.roll_history), "action_rolls": 0}
        
        # Calculate statistics
        rolls = [r["roll"] for r in action_rolls]
        totals = [r["total"] for r in action_rolls]
        
        # Success rate (assuming DC 10 average)
        successes = [r for r in action_rolls if r["total"] >= 10]
        success_rate = len(successes) / len(action_rolls) * 100
        
        # Critical rates
        critical_failures = [r for r in action_rolls if r["roll"] == 1]
        critical_successes = [r for r in action_rolls if r["roll"] == 20]
        
        return {
            "total_rolls": len(self.roll_history),
            "action_rolls": len(action_rolls),
            "average_roll": sum(rolls) / len(rolls),
            "average_total": sum(totals) / len(totals),
            "success_rate": success_rate,
            "critical_failures": len(critical_failures),
            "critical_successes": len(critical_successes),
            "highest_roll": max(rolls),
            "lowest_roll": min(rolls)
        }
    
    def _assess_action_difficulty(self, action: str) -> int:
        """Assess action difficulty and return DC"""
        
        action_lower = action.lower()
        
        # Very Easy (DC 5)
        easy_actions = [
            "casual conversation", "simple question", "basic observation",
            "read document", "walk to location"
        ]
        
        # Easy (DC 8)
        moderate_easy_actions = [
            "interview cooperative witness", "examine obvious evidence",
            "ask direct question", "search public area"
        ]
        
        # Medium (DC 12)
        medium_actions = [
            "confront with evidence", "persuade reluctant witness",
            "search private area", "analyze complex evidence"
        ]
        
        # Hard (DC 15)
        hard_actions = [
            "interrogate hostile witness", "break into location",
            "deceive authority figure", "solve complex puzzle"
        ]
        
        # Very Hard (DC 18)
        very_hard_actions = [
            "get confession from killer", "access restricted area",
            "convince judge to break protocol", "uncover major conspiracy"
        ]
        
        # Nearly Impossible (DC 20)
        extreme_actions = [
            "resurrect the dead", "time travel", "mind reading",
            "impossible physical feat"
        ]
        
        # Check each difficulty tier
        for actions, dc in [
            (easy_actions, 5),
            (moderate_easy_actions, 8),
            (medium_actions, 12),
            (hard_actions, 15),
            (very_hard_actions, 18),
            (extreme_actions, 20)
        ]:
            for action_pattern in actions:
                if action_pattern in action_lower:
                    return dc
        
        # Check for keywords to determine difficulty
        if any(word in action_lower for word in ["interrogate", "confront", "accuse"]):
            return 15
        elif any(word in action_lower for word in ["persuade", "convince", "negotiate"]):
            return 12
        elif any(word in action_lower for word in ["search", "investigate", "examine"]):
            return 10
        elif any(word in action_lower for word in ["ask", "question", "interview"]):
            return 8
        
        # Default medium difficulty
        return 10
    
    def _parse_modifiers(self, modifiers: List[str]) -> int:
        """Parse modifier strings and return total"""
        
        total = 0
        
        for modifier in modifiers:
            # Handle numeric modifiers
            if modifier.startswith(('+', '-')):
                try:
                    total += int(modifier)
                    continue
                except ValueError:
                    pass
            
            # Handle named modifiers
            modifier_lower = modifier.lower()
            
            if "advantage" in modifier_lower:
                total += 2
            elif "disadvantage" in modifier_lower:
                total -= 2
            elif "evidence" in modifier_lower:
                # Extract evidence count
                numbers = re.findall(r'\d+', modifier)
                if numbers:
                    evidence_count = min(int(numbers[0]), 3)
                    total += evidence_count
                else:
                    total += 1
            elif "hostile" in modifier_lower:
                total -= 2
            elif "friendly" in modifier_lower:
                total += 2
            elif "drunk" in modifier_lower or "tired" in modifier_lower:
                total -= 1
            elif "prepared" in modifier_lower or "focused" in modifier_lower:
                total += 1
        
        return total
    
    def _determine_result(self, roll: int, total: int, difficulty: int) -> Dict[str, str]:
        """Determine action result based on roll and difficulty"""
        
        # Critical failure always fails
        if roll == 1:
            return {
                "outcome": "critical_failure",
                "description": "Critical failure - something goes very wrong"
            }
        
        # Critical success (almost) always succeeds
        if roll == 20:
            if difficulty <= 25:  # Even nat 20 can't do impossible things
                return {
                    "outcome": "critical_success", 
                    "description": "Critical success - exceptional outcome with bonus information"
                }
        
        # Standard success/failure
        if total >= difficulty + 5:
            return {
                "outcome": "great_success",
                "description": "Great success - achieves goal with additional benefits"
            }
        elif total >= difficulty:
            return {
                "outcome": "success",
                "description": "Success - achieves intended goal"
            }
        elif total >= difficulty - 3:
            return {
                "outcome": "partial_success",
                "description": "Partial success - limited success with complications"
            }
        elif total >= difficulty - 7:
            return {
                "outcome": "failure", 
                "description": "Failure - action fails but no major consequences"
            }
        else:
            return {
                "outcome": "bad_failure",
                "description": "Bad failure - action fails with negative consequences"
            }
    
    def _parse_dice_expression(self, expression: str) -> Dict[str, int]:
        """Parse dice notation like '2d6+3' or '1d20-1'"""
        
        # Default to 1d20
        expression = expression.strip() or "1d20"
        
        # Parse pattern: NdS+M or NdS-M
        pattern = r'(\d*)d(\d+)([+-]\d+)?'
        match = re.match(pattern, expression.lower())
        
        if not match:
            # If parsing fails, default to 1d20
            return {"count": 1, "sides": 20, "modifier": 0}
        
        count = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        # Sanity checks
        count = max(1, min(count, 10))  # 1-10 dice
        sides = max(2, min(sides, 100))  # 2-100 sides
        modifier = max(-20, min(modifier, 20))  # -20 to +20 modifier
        
        return {
            "count": count,
            "sides": sides, 
            "modifier": modifier
        }
    
    def get_formatted_roll_history(self, count: int = 10) -> str:
        """Get formatted string of recent rolls for display"""
        
        if not self.roll_history:
            return "🎲 No dice rolls yet."
        
        recent_rolls = self.get_recent_rolls(count)
        
        output = [f"🎲 Recent Dice Rolls (last {len(recent_rolls)}):"]
        output.append("=" * 40)
        
        for i, roll in enumerate(recent_rolls, 1):
            if "action" in roll:
                # Action roll
                result_emoji = self._get_result_emoji(roll["result"])
                critical_indicator = " 💥" if roll.get("critical") else ""
                
                output.append(f"{i}. {roll['action']}{critical_indicator}")
                output.append(f"   🎲 Rolled: {roll['roll']} + {roll['modifier_total']} = {roll['total']} vs DC{roll['difficulty']}")
                output.append(f"   {result_emoji} {roll['result'].replace('_', ' ').title()}")
                
            else:
                # Dice roll
                rolls_text = ", ".join(map(str, roll.get("rolls", [roll["final_total"]])))
                output.append(f"{i}. Dice: {roll.get('expression', 'unknown')}")
                output.append(f"   🎲 Rolled: [{rolls_text}] = {roll['final_total']}")
            
            output.append("")
        
        return "\n".join(output)
    
    def _get_result_emoji(self, result: str) -> str:
        """Get emoji for dice result"""
        result_emojis = {
            "critical_success": "🌟",
            "great_success": "✅", 
            "success": "☑️",
            "partial_success": "⚠️",
            "failure": "❌",
            "bad_failure": "💥",
            "critical_failure": "💀"
        }
        return result_emojis.get(result, "❓")