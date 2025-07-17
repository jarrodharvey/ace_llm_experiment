"""
Character Management Plugin

Handles character introductions, relationships, and trust tracking.
Prevents duplicate characters and maintains consistency.
"""

import uuid
import random
from typing import Dict, List, Any, Optional
from datetime import datetime


class CharacterPlugin:
    """Manages character introductions and relationships"""
    
    def __init__(self):
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.used_names: List[str] = []
        self.name_generator = CharacterNameGenerator()
    
    def load_state(self, character_data: Dict[str, Any]) -> None:
        """Load character state from game state"""
        self.characters = character_data.copy()
        self.used_names = [char["name"] for char in self.characters.values()]
    
    def meet_character(self, name: str, role: str,
                      age: Optional[int] = None,
                      occupation: Optional[str] = None,
                      trust_level: int = 0) -> Dict[str, Any]:
        """Introduce a new character with validation"""
        
        # Validate input
        if not name or not name.strip():
            raise ValueError("Character name cannot be empty")
        
        if not role or not role.strip():
            raise ValueError("Character role cannot be empty")
        
        # Check for duplicate names (case-insensitive)
        name_lower = name.lower().strip()
        for existing_id, existing_char in self.characters.items():
            if existing_char["name"].lower() == name_lower:
                raise ValueError(f"Character already exists: {existing_char['name']}")
        
        # Check for duplicate critical roles
        critical_roles = ["prosecutor", "judge", "client"]
        role_lower = role.lower().strip()
        
        if role_lower in critical_roles:
            for existing_char in self.characters.values():
                if existing_char["role"].lower() == role_lower:
                    raise ValueError(f"Only one {role_lower} allowed per case")
        
        # Generate character details if not provided
        if age is None:
            age = self._generate_age_for_role(role)
        
        if occupation is None:
            occupation = self._generate_occupation_for_role(role, age)
        
        # Generate unique ID
        character_id = self._generate_character_id(name)
        
        # Create character record
        character_data = {
            "id": character_id,
            "name": name.strip(),
            "role": role.strip(),
            "age": age,
            "occupation": occupation,
            "trust_level": trust_level,
            "met_at": datetime.now().isoformat(),
            "personality": self._generate_personality(),
            "interview_status": "not_interviewed",
            "notes": "",
            "relationships": {},
            "secrets": [],
            "credibility": self._assess_initial_credibility(role)
        }
        
        # Store character
        self.characters[character_id] = character_data
        self.used_names.append(name.strip())
        
        return character_data
    
    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Get specific character by ID"""
        return self.characters.get(character_id)
    
    def find_character_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find character by name (case-insensitive)"""
        name_lower = name.lower()
        for character in self.characters.values():
            if character["name"].lower() == name_lower:
                return character
        return None
    
    def list_characters(self) -> List[Dict[str, Any]]:
        """List all characters sorted by trust level"""
        character_list = list(self.characters.values())
        return sorted(character_list, key=lambda c: c["trust_level"], reverse=True)
    
    def update_trust(self, character_id: str, trust_change: int) -> int:
        """Update character trust level"""
        if character_id not in self.characters:
            raise ValueError(f"Character not found: {character_id}")
        
        character = self.characters[character_id]
        old_trust = character["trust_level"]
        new_trust = max(-10, min(10, old_trust + trust_change))  # Clamp to -10 to +10
        
        character["trust_level"] = new_trust
        character["last_trust_update"] = datetime.now().isoformat()
        
        return new_trust
    
    def interview_character(self, character_id: str, notes: str = "") -> None:
        """Mark character as interviewed"""
        if character_id not in self.characters:
            raise ValueError(f"Character not found: {character_id}")
        
        character = self.characters[character_id]
        character["interview_status"] = "interviewed"
        character["interview_date"] = datetime.now().isoformat()
        
        if notes:
            character["notes"] = notes
    
    def add_relationship(self, character1_id: str, character2_id: str, 
                        relationship_type: str) -> None:
        """Add relationship between two characters"""
        
        if character1_id not in self.characters:
            raise ValueError(f"Character not found: {character1_id}")
        
        if character2_id not in self.characters:
            raise ValueError(f"Character not found: {character2_id}")
        
        # Add relationship for both characters
        char1 = self.characters[character1_id]
        char2 = self.characters[character2_id]
        
        char1["relationships"][character2_id] = relationship_type
        char2["relationships"][character1_id] = relationship_type
    
    def get_characters_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Get all characters with specific role"""
        role_lower = role.lower()
        return [c for c in self.characters.values() 
                if c["role"].lower() == role_lower]
    
    def get_hostile_characters(self) -> List[Dict[str, Any]]:
        """Get characters with negative trust levels"""
        return [c for c in self.characters.values() if c["trust_level"] < 0]
    
    def get_friendly_characters(self) -> List[Dict[str, Any]]:
        """Get characters with positive trust levels"""
        return [c for c in self.characters.values() if c["trust_level"] > 0]
    
    def validate_characters_for_trial(self) -> Dict[str, Any]:
        """Validate character setup for trial readiness"""
        
        character_list = list(self.characters.values())
        
        # Check for required roles
        roles_present = {char["role"].lower() for char in character_list}
        required_roles = ["prosecutor", "client"]
        missing_roles = [role for role in required_roles if role not in roles_present]
        
        # Count character types
        witnesses = [c for c in character_list if "witness" in c["role"].lower()]
        suspects = [c for c in character_list if c["trust_level"] < -2]  # Hostile characters
        
        # Interview status
        interviewed = [c for c in character_list if c["interview_status"] == "interviewed"]
        
        # Trial readiness assessment
        ready_for_trial = (
            len(missing_roles) == 0 and
            len(witnesses) >= 2 and
            len(interviewed) >= len(character_list) * 0.6  # 60% interviewed
        )
        
        return {
            "ready_for_trial": ready_for_trial,
            "total_characters": len(character_list),
            "missing_roles": missing_roles,
            "witnesses": len(witnesses),
            "suspects": len(suspects),
            "interviewed": len(interviewed),
            "trust_distribution": self._get_trust_distribution(),
            "recommendations": self._get_character_recommendations(character_list)
        }
    
    def generate_unique_name(self, role: str = "") -> str:
        """Generate unique character name that hasn't been used"""
        
        attempts = 0
        while attempts < 50:  # Prevent infinite loop
            name = self.name_generator.generate_name(role)
            
            if name not in self.used_names:
                return name
            
            attempts += 1
        
        # Fallback to UUID-based name
        return f"Character_{uuid.uuid4().hex[:6]}"
    
    def _generate_character_id(self, name: str) -> str:
        """Generate unique character ID"""
        base_id = name.lower().replace(" ", "_").replace("-", "_")
        base_id = "".join(c for c in base_id if c.isalnum() or c == "_")
        
        if base_id not in self.characters:
            return base_id
        
        # Add number suffix if needed
        counter = 1
        while f"{base_id}_{counter}" in self.characters:
            counter += 1
        
        return f"{base_id}_{counter}"
    
    def _generate_age_for_role(self, role: str) -> int:
        """Generate appropriate age for character role"""
        role_lower = role.lower()
        
        age_ranges = {
            "judge": (45, 70),
            "prosecutor": (28, 55),
            "detective": (25, 50),
            "police": (21, 55),
            "lawyer": (25, 60),
            "doctor": (28, 65),
            "student": (18, 30),
            "security": (21, 55),
            "witness": (18, 80),
            "client": (18, 70)
        }
        
        # Find matching role
        for role_key, (min_age, max_age) in age_ranges.items():
            if role_key in role_lower:
                return random.randint(min_age, max_age)
        
        # Default range
        return random.randint(25, 60)
    
    def _generate_occupation_for_role(self, role: str, age: int) -> str:
        """Generate occupation based on role and age"""
        role_lower = role.lower()
        
        # Direct role mappings
        occupation_mappings = {
            "judge": "Judge",
            "prosecutor": "Prosecutor", 
            "detective": "Detective",
            "police": "Police Officer",
            "lawyer": "Lawyer",
            "doctor": "Doctor",
            "security": "Security Guard"
        }
        
        for role_key, occupation in occupation_mappings.items():
            if role_key in role_lower:
                return occupation
        
        # Age-based occupations for generic roles
        if age < 25:
            return random.choice(["Student", "Intern", "Assistant", "Clerk"])
        elif age > 60:
            return random.choice(["Retired", "Consultant", "Professor", "Manager"])
        else:
            return random.choice([
                "Accountant", "Teacher", "Engineer", "Manager", "Salesperson",
                "Nurse", "Technician", "Analyst", "Coordinator", "Specialist"
            ])
    
    def _generate_personality(self) -> str:
        """Generate random personality trait"""
        personalities = [
            "Adamant", "Bashful", "Bold", "Brave", "Calm", "Careful", "Docile", 
            "Gentle", "Hardy", "Hasty", "Impish", "Jolly", "Lax", "Lonely", 
            "Mild", "Modest", "Naive", "Naughty", "Quiet", "Quirky", "Rash", 
            "Relaxed", "Sassy", "Serious", "Timid"
        ]
        return random.choice(personalities)
    
    def _assess_initial_credibility(self, role: str) -> int:
        """Assess initial character credibility based on role"""
        role_lower = role.lower()
        
        # High credibility roles
        if any(keyword in role_lower for keyword in ["judge", "prosecutor", "police", "detective"]):
            return random.randint(7, 9)
        
        # Medium credibility roles
        elif any(keyword in role_lower for keyword in ["lawyer", "doctor", "witness"]):
            return random.randint(5, 7)
        
        # Variable credibility roles
        else:
            return random.randint(3, 8)
    
    def _get_trust_distribution(self) -> Dict[str, int]:
        """Get distribution of character trust levels"""
        
        hostile = len([c for c in self.characters.values() if c["trust_level"] < -2])
        unfriendly = len([c for c in self.characters.values() if -2 <= c["trust_level"] < 0])
        neutral = len([c for c in self.characters.values() if c["trust_level"] == 0])
        friendly = len([c for c in self.characters.values() if 0 < c["trust_level"] <= 5])
        very_friendly = len([c for c in self.characters.values() if c["trust_level"] > 5])
        
        return {
            "hostile": hostile,
            "unfriendly": unfriendly, 
            "neutral": neutral,
            "friendly": friendly,
            "very_friendly": very_friendly
        }
    
    def _get_character_recommendations(self, character_list: List[Dict[str, Any]]) -> List[str]:
        """Get recommendations for character development"""
        
        recommendations = []
        
        if len(character_list) < 4:
            recommendations.append("Introduce more characters to build a complex case")
        
        # Check for required roles
        roles_present = {char["role"].lower() for char in character_list}
        if "prosecutor" not in roles_present:
            recommendations.append("Find the prosecutor for this case")
        
        if "client" not in roles_present:
            recommendations.append("Identify your client in this case")
        
        # Interview progress
        interviewed = [c for c in character_list if c["interview_status"] == "interviewed"]
        if len(interviewed) < len(character_list) * 0.5:
            recommendations.append("Interview more characters to gather information")
        
        # Trust distribution
        hostile_count = len([c for c in character_list if c["trust_level"] < -2])
        if hostile_count == 0:
            recommendations.append("Find hostile characters who might be hiding something")
        
        if not recommendations:
            recommendations.append("Character development looks good for trial")
        
        return recommendations
    
    def get_formatted_character_list(self) -> str:
        """Get formatted string of all characters for display"""
        
        if not self.characters:
            return "👥 No characters met yet."
        
        character_list = self.list_characters()
        
        output = ["👥 Characters Met:"]
        output.append("=" * 40)
        
        for i, character in enumerate(character_list, 1):
            trust_indicator = self._get_trust_indicator(character["trust_level"])
            interview_status = "✅" if character["interview_status"] == "interviewed" else "❌"
            
            output.append(f"{i}. {character['name']} {trust_indicator}")
            output.append(f"   👤 {character['role']} | Age: {character['age']} | {character['occupation']}")
            output.append(f"   🎭 {character['personality']} | Interviewed: {interview_status}")
            
            if character.get("notes"):
                output.append(f"   📝 {character['notes']}")
            
            output.append("")
        
        # Add summary
        total = len(character_list)
        interviewed = len([c for c in character_list if c["interview_status"] == "interviewed"])
        
        output.append(f"📊 Summary: {total} characters, {interviewed} interviewed")
        
        return "\n".join(output)
    
    def _get_trust_indicator(self, trust_level: int) -> str:
        """Get emoji indicator for trust level"""
        if trust_level >= 5:
            return "😊"  # Very friendly
        elif trust_level > 0:
            return "🙂"  # Friendly
        elif trust_level == 0:
            return "😐"  # Neutral
        elif trust_level >= -2:
            return "🙄"  # Unfriendly
        else:
            return "😠"  # Hostile


class CharacterNameGenerator:
    """Generates unique character names"""
    
    def __init__(self):
        self.first_names = [
            "Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry",
            "Iris", "Jack", "Kate", "Leo", "Mary", "Nathan", "Olivia", "Paul",
            "Quinn", "Rachel", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xavier",
            "Yvonne", "Zack", "Anna", "Ben", "Claire", "Dan", "Eva", "Felix"
        ]
        
        self.last_names = [
            "Anderson", "Brown", "Clark", "Davis", "Evans", "Fisher", "Garcia",
            "Harris", "Jackson", "King", "Lee", "Miller", "Nelson", "Parker",
            "Quinn", "Roberts", "Smith", "Taylor", "Wilson", "Young", "Allen",
            "Baker", "Cooper", "Green", "Hall", "Johnson", "Lewis", "Moore"
        ]
    
    def generate_name(self, role_hint: str = "") -> str:
        """Generate a random name with optional role consideration"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        return f"{first_name} {last_name}"