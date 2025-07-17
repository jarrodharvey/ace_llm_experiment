"""
AI Director - Unified AI Management System

Coordinates multiple AI services and applies forcing functions.
Handles context management, conversation flow, and response generation.
"""

import json
import random
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class AIDirector:
    """Central coordinator for AI-driven gameplay"""
    
    def __init__(self):
        self.forcing_functions = ForcingFunctionManager()
        self.context_manager = ContextManager()
        self.conversation_history: List[Dict[str, Any]] = []
        
        # AI service interfaces (to be implemented)
        self.claude_interface = None  # Will integrate with Claude API
        self.chatgpt_interface = None  # Will integrate with ChatGPT API
        self.context7_interface = None  # Will integrate with Context7 MCP
    
    def process_user_input(self, user_input: str, game_state: Dict[str, Any]) -> str:
        """Process user input and generate AI response"""
        
        # Record user input
        self.conversation_history.append({
            "type": "user_input",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Parse input for commands
        command_result = self._parse_gameplay_commands(user_input, game_state)
        if command_result:
            return command_result
        
        # Determine if we need forcing function
        requires_improvisation = self._requires_improvisation(user_input, game_state)
        
        if requires_improvisation:
            # Apply forcing function for improvised response
            inspiration_word = self.forcing_functions.get_random_inspiration()
            
            response = self._generate_improvised_response(
                user_input, 
                game_state, 
                inspiration_word
            )
        else:
            # Generate standard response
            response = self._generate_standard_response(user_input, game_state)
        
        # Record AI response
        self.conversation_history.append({
            "type": "ai_response",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _parse_gameplay_commands(self, user_input: str, 
                                game_state: Dict[str, Any]) -> Optional[str]:
        """Parse and execute gameplay commands"""
        
        input_lower = user_input.lower().strip()
        
        # Evidence commands
        if input_lower.startswith("evidence"):
            return self._handle_evidence_command(input_lower, game_state)
        
        # Character commands
        if input_lower.startswith("character"):
            return self._handle_character_command(input_lower, game_state)
        
        # Dice commands
        if input_lower.startswith("dice") or input_lower.startswith("roll"):
            return self._handle_dice_command(input_lower, game_state)
        
        # Save commands
        if input_lower.startswith("save"):
            return self._handle_save_command(input_lower, game_state)
        
        # Quick commands
        quick_commands = {
            "evidence list": "📋 Evidence collected: [evidence would be listed here]",
            "character list": "👥 Characters met: [characters would be listed here]", 
            "status": "📊 Current status: [status would be shown here]"
        }
        
        if input_lower in quick_commands:
            return quick_commands[input_lower]
        
        return None
    
    def _handle_evidence_command(self, command: str, game_state: Dict[str, Any]) -> str:
        """Handle evidence-related commands"""
        
        if "list" in command:
            evidence = game_state.get("evidence", {})
            if not evidence:
                return "📋 No evidence collected yet."
            
            output = ["📋 Evidence Collected:"]
            for i, (key, item) in enumerate(evidence.items(), 1):
                output.append(f"{i}. {item['name']} - {item['description']}")
            
            return "\n".join(output)
        
        elif "add" in command:
            # Parse "evidence add 'name' 'description'"
            match = re.search(r"add ['\"]([^'\"]+)['\"] ['\"]([^'\"]+)['\"]", command)
            if match:
                name, description = match.groups()
                return f"✅ Added evidence: {name} - {description}"
            else:
                return "❌ Format: evidence add 'name' 'description'"
        
        return "❓ Available: evidence list, evidence add 'name' 'description'"
    
    def _handle_character_command(self, command: str, game_state: Dict[str, Any]) -> str:
        """Handle character-related commands"""
        
        if "list" in command:
            characters = game_state.get("characters", {})
            if not characters:
                return "👥 No characters met yet."
            
            output = ["👥 Characters Met:"]
            for i, (key, char) in enumerate(characters.items(), 1):
                trust_indicator = "😊" if char["trust_level"] > 0 else "😐" if char["trust_level"] == 0 else "😠"
                output.append(f"{i}. {char['name']} ({char['role']}) {trust_indicator}")
            
            return "\n".join(output)
        
        elif "meet" in command:
            # Parse "character meet 'name' 'role'"
            match = re.search(r"meet ['\"]([^'\"]+)['\"] ['\"]([^'\"]+)['\"]", command)
            if match:
                name, role = match.groups()
                return f"👋 Met {name}, {role}"
            else:
                return "❌ Format: character meet 'name' 'role'"
        
        return "❓ Available: character list, character meet 'name' 'role'"
    
    def _handle_dice_command(self, command: str, game_state: Dict[str, Any]) -> str:
        """Handle dice rolling commands"""
        
        # Parse "dice roll 'action'" or "roll 'action'"
        match = re.search(r"(?:dice\s+)?roll ['\"]([^'\"]+)['\"]", command)
        if match:
            action = match.group(1)
            
            # Simulate dice roll (would use DicePlugin in real implementation)
            roll = random.randint(1, 20)
            modifier = random.randint(-2, 3)
            total = roll + modifier
            
            if total >= 15:
                result = "Great Success!"
            elif total >= 12:
                result = "Success"
            elif total >= 8:
                result = "Partial Success"
            else:
                result = "Failure"
            
            return f"🎲 Rolling for '{action}': {roll} + {modifier} = {total} - {result}"
        
        return "❓ Format: dice roll 'action description'"
    
    def _handle_save_command(self, command: str, game_state: Dict[str, Any]) -> str:
        """Handle save game commands"""
        
        # Parse save name
        match = re.search(r"save ['\"]([^'\"]+)['\"]", command)
        if match:
            save_name = match.group(1)
            return f"💾 Game saved as '{save_name}'"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"💾 Game saved as 'auto_save_{timestamp}'"
    
    def _requires_improvisation(self, user_input: str, game_state: Dict[str, Any]) -> bool:
        """Determine if user input requires improvised AI response"""
        
        # Commands don't require improvisation
        if self._parse_gameplay_commands(user_input, game_state):
            return False
        
        # Simple questions might not need improvisation
        simple_patterns = [
            r"what\s+is\s+\w+",
            r"where\s+is\s+\w+", 
            r"who\s+is\s+\w+",
            r"show\s+me\s+\w+",
            r"list\s+\w+"
        ]
        
        input_lower = user_input.lower()
        for pattern in simple_patterns:
            if re.search(pattern, input_lower):
                return False
        
        # Complex interactions, character dialogue, plot development = improvisation
        improvisation_indicators = [
            "talk to", "ask", "confront", "investigate", "examine",
            "what happens", "what does", "how does", "why did",
            "tell me about", "explain", "describe"
        ]
        
        for indicator in improvisation_indicators:
            if indicator in input_lower:
                return True
        
        # Default to improvisation for safety
        return True
    
    def _generate_improvised_response(self, user_input: str, 
                                    game_state: Dict[str, Any],
                                    inspiration_word: str) -> str:
        """Generate improvised response using forcing function"""
        
        # A-to-C Process:
        # A = Current situation + user input
        # B = Random inspiration word (forcing function)
        # C = Creative solution maintaining logical consistency
        
        context_summary = self._summarize_game_context(game_state)
        
        # For demo purposes, return structured response
        # In real implementation, this would call Claude API with forcing function
        
        return f"""🎮 Processing your action: "{user_input}"

📋 Current Context: {context_summary}

🎲 Inspiration Word: {inspiration_word}

[AI would use A-to-C process here to generate unique response]

💡 Result: Your action leads to an unexpected development involving {inspiration_word.lower()}...

Available Actions:
1. Investigate further
2. Ask more questions  
3. Present evidence
4. Roll dice for outcome
5. Save game"""
    
    def _generate_standard_response(self, user_input: str, 
                                  game_state: Dict[str, Any]) -> str:
        """Generate standard response for non-improvised situations"""
        
        # Handle standard game responses without forcing functions
        return f"""🎮 Continuing the case...

Your input: "{user_input}"

[Standard game response based on current state]

Available Actions:
1. Gather evidence
2. Interview witnesses
3. Examine locations
4. Check status
5. Save progress"""
    
    def _summarize_game_context(self, game_state: Dict[str, Any]) -> str:
        """Summarize current game context"""
        
        phase = game_state.get("phase", "investigation")
        evidence_count = len(game_state.get("evidence", {}))
        character_count = len(game_state.get("characters", {}))
        
        return f"{phase} phase, {evidence_count} evidence, {character_count} characters"
    
    def get_context_for_ai(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for AI services"""
        
        return {
            "game_state": game_state,
            "conversation_history": self.conversation_history[-10:],  # Last 10 exchanges
            "current_phase": game_state.get("phase", "investigation"),
            "available_actions": self._get_available_actions(game_state),
            "forcing_function_available": True
        }
    
    def _get_available_actions(self, game_state: Dict[str, Any]) -> List[str]:
        """Get contextually appropriate actions"""
        
        phase = game_state.get("phase", "investigation")
        
        if phase == "investigation":
            return [
                "gather evidence",
                "interview witness", 
                "examine location",
                "present evidence to character",
                "check trial readiness"
            ]
        elif phase == "trial":
            return [
                "call witness",
                "start cross-examination",
                "present evidence",
                "object to testimony",
                "give closing argument"
            ]
        else:
            return [
                "continue case",
                "check status",
                "save progress"
            ]


class ForcingFunctionManager:
    """Manages forcing functions for AI improvisation"""
    
    def __init__(self):
        self.inspiration_history: List[Dict[str, Any]] = []
        
        # Load word list for forcing functions
        self.word_list = self._load_word_list()
    
    def get_random_inspiration(self) -> str:
        """Get completely random word for forcing function"""
        
        word = random.choice(self.word_list)
        
        # Record usage
        self.inspiration_history.append({
            "word": word,
            "timestamp": datetime.now().isoformat(),
            "context": "random_inspiration"
        })
        
        # Keep history manageable
        if len(self.inspiration_history) > 100:
            self.inspiration_history = self.inspiration_history[-50:]
        
        return word
    
    def get_contextual_inspiration(self, context: str) -> str:
        """Get random word with context description"""
        
        word = self.get_random_inspiration()
        
        # Update last entry with context
        if self.inspiration_history:
            self.inspiration_history[-1]["context"] = context
        
        return word
    
    def _load_word_list(self) -> List[str]:
        """Load word list for inspiration"""
        
        # Basic word list for forcing functions
        # In real implementation, would use wonderwords package
        return [
            "apple", "bridge", "candle", "diamond", "elephant", "feather", "guitar",
            "hammer", "island", "jacket", "keyboard", "ladder", "mirror", "needle",
            "ocean", "pencil", "question", "rainbow", "shadow", "telescope", "umbrella",
            "violin", "whisper", "xylophone", "yellow", "zebra", "anchor", "butterfly",
            "crystal", "dragon", "emerald", "flame", "ghost", "harvest", "ink", "journey",
            "knot", "lightning", "mountain", "night", "opal", "puzzle", "quilt", "river",
            "star", "thunder", "universe", "valley", "wind", "xenon", "youth", "zephyr"
        ]


class ContextManager:
    """Manages conversation context and memory"""
    
    def __init__(self):
        self.context_window_size = 50  # Number of exchanges to remember
        self.key_events: List[Dict[str, Any]] = []
    
    def add_key_event(self, event_type: str, description: str, 
                     metadata: Dict[str, Any] = None) -> None:
        """Record key event for context preservation"""
        
        event = {
            "type": event_type,
            "description": description,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.key_events.append(event)
        
        # Keep reasonable size
        if len(self.key_events) > 20:
            self.key_events = self.key_events[-15:]
    
    def get_context_summary(self) -> str:
        """Get summary of key events for context restoration"""
        
        if not self.key_events:
            return "No significant events recorded."
        
        summary = ["Key Events:"]
        for event in self.key_events[-10:]:  # Last 10 events
            summary.append(f"- {event['description']}")
        
        return "\n".join(summary)
    
    def validate_context_continuity(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that context is consistent"""
        
        # Check for potential context breaks
        issues = []
        
        # Placeholder validation - would implement real checks
        case_info = game_state.get("case_info", {})
        if not case_info.get("case_name"):
            issues.append("Case name not found in context")
        
        phase = game_state.get("phase")
        if not phase:
            issues.append("Game phase unclear")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "context_age": len(self.key_events),
            "recommendations": [
                "Restore context from narrative save" if issues else "Context looks good"
            ]
        }