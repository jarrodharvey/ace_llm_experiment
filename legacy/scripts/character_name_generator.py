#!/usr/bin/env python3
"""
Character Name Generator
Provides unique character name generation using faker to prevent repetition.
"""

from faker import Faker
import json
import os
from pathlib import Path
from typing import Set, Optional, Dict, Any, List


class CharacterNameGenerator:
    def __init__(self, case_path: Optional[str] = None):
        self.fake = Faker()
        self.case_path = Path(case_path) if case_path else None
        self.used_names = self._load_used_names()
        self.surname_families = self._load_surname_families()  # Track which surnames belong to which families
        
        # Personality traits list
        self.personality_traits = [
            "Adamant", "Bashful", "Bold", "Brave", "Calm", "Careful", "Docile", 
            "Gentle", "Hardy", "Hasty", "Impish", "Jolly", "Lax", "Lonely", 
            "Mild", "Modest", "Naive", "Naughty", "Quiet", "Quirky", "Rash", 
            "Relaxed", "Sassy", "Serious", "Timid"
        ]
        
        # Initialize red herring classifier if case path provided
        self.red_herring_classifier = None
        if case_path:
            from red_herring_system import RedHerringClassifier
            self.red_herring_classifier = RedHerringClassifier(case_path)
        
    def _load_used_names(self) -> Set[str]:
        """Load all character names already used in the project to avoid duplicates"""
        used_names = set()
        
        # Get project root directory
        project_root = Path(__file__).parent.parent
        
        # Scan all JSON files for existing character names
        for json_file in project_root.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._extract_names_from_data(data, used_names)
            except (json.JSONDecodeError, UnicodeDecodeError, PermissionError):
                # Skip files that can't be read or aren't valid JSON
                continue
                
        return used_names
    
    def _load_surname_families(self) -> Dict[str, str]:
        """Load surname-to-family mappings to track related characters"""
        surname_families = {}
        
        if not self.case_path:
            return surname_families
            
        # Try to load existing family mapping from case
        families_file = self.case_path / "game_state" / "character_families.json"
        if families_file.exists():
            try:
                with open(families_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    surname_families = data.get("surname_to_family", {})
            except (json.JSONDecodeError, KeyError):
                pass  # Start fresh if file is corrupted
                
        return surname_families
    
    def _extract_names_from_data(self, data: Any, used_names: Set[str]) -> None:
        """Recursively extract names from JSON data structures"""
        if isinstance(data, dict):
            # Look for name fields
            if "name" in data and isinstance(data["name"], str):
                # Filter out non-person names (case files, evidence, etc.)
                name = data["name"].strip()
                if self._is_person_name(name):
                    used_names.add(name)
            
            # Recursively check all values
            for value in data.values():
                self._extract_names_from_data(value, used_names)
                
        elif isinstance(data, list):
            # Recursively check all items
            for item in data:
                self._extract_names_from_data(item, used_names)
    
    def _is_person_name(self, name: str) -> bool:
        """Determine if a name represents a person rather than an object/file"""
        # Filter out obvious non-person names
        non_person_indicators = [
            "case", "file", "evidence", "document", "report", "prosecution",
            "defense", "trial", "investigation", "simple", "complex", "full"
        ]
        
        name_lower = name.lower()
        if any(indicator in name_lower for indicator in non_person_indicators):
            return False
            
        # Must have at least first and last name (2 words minimum)
        words = name.split()
        # Allow periods and other common name characters (Dr., Jr., etc.)
        return len(words) >= 2 and all(word.replace('.', '').isalpha() for word in words)
    
    def generate_unique_name(self, role: Optional[str] = None, age: Optional[int] = None, include_personality: bool = False) -> str:
        """
        Generate a unique character name not used elsewhere in the project
        
        Args:
            role: Optional role hint (e.g., "judge", "prosecutor", "witness")
                 Can influence name style but doesn't guarantee specific patterns
            age: Optional age for the character (affects name style)
            include_personality: Whether to include personality trait in output
        
        Returns:
            A unique full name (first + last), optionally with personality trait
        """
        max_attempts = 100
        
        for _ in range(max_attempts):
            # Generate name based on role hint if provided
            if role and role.lower() == "judge":
                # Judges often have more formal/traditional names
                first_name = self.fake.first_name()
                last_name = self.fake.last_name()
            else:
                # Standard name generation for all other roles
                first_name = self.fake.first_name()
                last_name = self.fake.last_name()
            
            full_name = f"{first_name} {last_name}"
            
            # Check if this name is already used
            if full_name not in self.used_names:
                # Add to used names to prevent future duplicates
                self.used_names.add(full_name)
                
                if include_personality:
                    personality = self.generate_personality_trait()
                    return f"{full_name} ({personality})"
                else:
                    return full_name
        
        # Fallback if we somehow can't generate a unique name
        # This should be extremely rare with faker's name pool
        fallback_name = f"{self.fake.first_name()} {self.fake.last_name()}-{self.fake.random_number(digits=3)}"
        
        if include_personality:
            personality = self.generate_personality_trait()
            return f"{fallback_name} ({personality})"
        else:
            return fallback_name
    
    def generate_age(self, role: Optional[str] = None) -> int:
        """
        Generate appropriate age for character based on role.
        
        Args:
            role: Optional role hint that may influence age range
            
        Returns:
            Age between 18-75, adjusted for role appropriateness
        """
        if not role:
            return self.fake.random_int(min=18, max=75)
        
        role_lower = role.lower().strip()
        
        # Age ranges based on role requirements
        if role_lower in ["judge", "magistrate"]:
            # Judges typically older, experienced
            return self.fake.random_int(min=40, max=70)
        elif role_lower in ["detective", "investigator", "police", "cop"]:
            # Law enforcement, broad range but typically experienced
            return self.fake.random_int(min=25, max=65)
        elif role_lower in ["prosecutor", "district attorney", "da", "lawyer", "attorney"]:
            # Legal professionals need law school + experience
            return self.fake.random_int(min=28, max=65)
        elif role_lower in ["doctor", "physician", "medical examiner", "coroner"]:
            # Medical professionals need extensive education
            return self.fake.random_int(min=30, max=70)
        elif role_lower in ["client", "defendant"]:
            # Can be any adult age
            return self.fake.random_int(min=18, max=75)
        elif role_lower in ["witness", "bystander"]:
            # Any adult age
            return self.fake.random_int(min=18, max=80)
        elif role_lower in ["security", "security guard", "guard"]:
            # Physical job, typically younger to middle-aged
            return self.fake.random_int(min=21, max=55)
        elif role_lower in ["student"]:
            # Students can be adult learners too
            return self.fake.random_int(min=18, max=30)
        else:
            # Default range for other roles
            return self.fake.random_int(min=18, max=75)
    
    def generate_occupation(self, age: int, role: Optional[str] = None) -> str:
        """
        Generate appropriate occupation based on age and optional role hint.
        
        Args:
            age: Character's age
            role: Optional role hint that may override occupation
            
        Returns:
            Occupation string
        """
        # Under 18 should be student (though our system generates 18+ only)
        if age < 18:
            return "student"
        
        # If role hint matches a profession, use it directly
        if role:
            role_lower = role.lower().strip()
            profession_map = {
                "detective": "detective", "investigator": "private investigator",
                "police": "police officer", "cop": "police officer",
                "judge": "judge", "magistrate": "magistrate",
                "prosecutor": "prosecutor", "district attorney": "district attorney",
                "lawyer": "lawyer", "attorney": "attorney", "counsel": "defense attorney",
                "doctor": "doctor", "physician": "physician", 
                "medical examiner": "medical examiner", "coroner": "coroner",
                "security": "security guard", "security guard": "security guard", "guard": "security officer",
                "journalist": "journalist", "reporter": "reporter",
                "court clerk": "court clerk", "bailiff": "bailiff", "stenographer": "court stenographer",
                "student": "student"
            }
            
            if role_lower in profession_map:
                return profession_map[role_lower]
        
        # For student age range (18-22), chance of being student
        if 18 <= age <= 22 and self.fake.random_int(1, 3) == 1:
            return "student"
        
        # Generate random occupation using Faker
        return self.fake.job()
    
    def generate_personality_trait(self) -> str:
        """
        Generate a random personality trait for a character.
        
        Returns:
            A single personality trait from the predefined list
        """
        return self.fake.random_element(self.personality_traits)
    
    def generate_name_with_classification(self, case_length: int, role: Optional[str] = None) -> tuple[str, str, int, str, str]:
        """
        Generate a unique character name with age, occupation, personality, and automatic classification for red herring system.
        
        Args:
            case_length: Case length (1, 2, or 3 days) for classification probability
            role: Optional role hint for name generation, age, occupation, and classification weighting
            
        Returns:
            Tuple of (full_name, classification, age, occupation, personality)
        """
        if not self.red_herring_classifier:
            # Fallback if no classifier available
            full_name = self.generate_unique_name(role)
            age = self.generate_age(role)
            occupation = self.generate_occupation(age, role)
            personality = self.generate_personality_trait()
            return full_name, "unknown", age, occupation, personality
        
        # Generate unique name, age, occupation, and personality
        full_name = self.generate_unique_name(role)
        age = self.generate_age(role)
        occupation = self.generate_occupation(age, role)
        personality = self.generate_personality_trait()
        
        # Classify character role with role-based weighting
        classification = self.red_herring_classifier.classify_character(full_name, case_length, role)
        
        return full_name, classification, age, occupation, personality
    
    def generate_family_member(self, family_surname: str, relationship: str = "sibling", 
                             reference_name: Optional[str] = None) -> str:
        """
        Generate a family member with shared surname
        
        Args:
            family_surname: The surname to use for this family member
            relationship: Type of relationship (spouse, sibling, parent, child, etc.)
            reference_name: Existing family member name for context
            
        Returns:
            Full name with the family surname
        """
        max_attempts = 100
        
        for _ in range(max_attempts):
            # Generate appropriate first name based on relationship
            first_name = self._generate_contextual_first_name(relationship, reference_name)
            full_name = f"{first_name} {family_surname}"
            
            if full_name not in self.used_names:
                self.used_names.add(full_name)
                
                # Track this surname as part of a family
                if family_surname not in self.surname_families:
                    family_id = f"family_{len(self.surname_families) + 1}_{family_surname.lower()}"
                    self.surname_families[family_surname] = family_id
                    
                return full_name
        
        # Fallback with number suffix
        first_name = self._generate_contextual_first_name(relationship, reference_name)
        return f"{first_name} {family_surname}-{self.fake.random_number(digits=3)}"
    
    def _generate_contextual_first_name(self, relationship: str, reference_name: Optional[str] = None) -> str:
        """Generate contextually appropriate first name based on relationship type"""
        
        # For spouses, consider gender-complementary names (though not required)
        if relationship.lower() == "spouse" and reference_name:
            # Simple approach: just generate any first name
            return self.fake.first_name()
        
        # For parent/child relationships, consider generational appropriateness
        elif relationship.lower() in ["parent", "father", "mother"]:
            # Use slightly more traditional/older generation names
            return self.fake.first_name()
        
        elif relationship.lower() in ["child", "son", "daughter"]:
            # Use contemporary names
            return self.fake.first_name()
        
        # For siblings, any contemporary name works
        else:
            return self.fake.first_name()
    
    def create_family(self, family_size: int, family_surname: Optional[str] = None, 
                     family_structure: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Create an entire family with related names
        
        Args:
            family_size: Number of family members to create
            family_surname: Specific surname to use (generates one if None)
            family_structure: Optional mapping of relationships {"role": "relationship_type"}
            
        Returns:
            Dictionary mapping roles to generated names
        """
        if not family_surname:
            # Generate a unique family surname
            for _ in range(100):
                candidate_surname = self.fake.last_name()
                if not any(name.endswith(candidate_surname) for name in self.used_names):
                    family_surname = candidate_surname
                    break
            else:
                family_surname = f"{self.fake.last_name()}-{self.fake.random_number(digits=3)}"
        
        family_members = {}
        
        if family_structure:
            # Use specified structure
            for role, relationship in family_structure.items():
                name = self.generate_family_member(family_surname, relationship)
                family_members[role] = name
        else:
            # Default family structure
            roles = ["parent1", "parent2", "child1", "child2", "child3"][:family_size]
            relationships = ["parent", "parent", "child", "child", "child"][:family_size]
            
            for role, relationship in zip(roles, relationships):
                name = self.generate_family_member(family_surname, relationship)
                family_members[role] = name
        
        return family_members
    
    def get_family_surname_suggestions(self, existing_names: List[str]) -> List[str]:
        """
        Get surname suggestions that would work well with existing character names
        
        Args:
            existing_names: List of existing character names in the case
            
        Returns:
            List of surname suggestions that don't conflict
        """
        existing_surnames = {name.split()[-1] for name in existing_names if ' ' in name}
        suggestions = []
        
        for _ in range(10):  # Generate multiple options
            candidate = self.fake.last_name()
            if candidate not in existing_surnames and \
               not any(f"{candidate}" in existing_name for existing_name in existing_names):
                suggestions.append(candidate)
                
        return suggestions[:5]  # Return top 5 suggestions
    
    def add_family_member_to_existing(self, existing_family_member: str, 
                                    relationship: str) -> str:
        """
        Add a new family member to an existing character's family
        
        Args:
            existing_family_member: Full name of existing character
            relationship: Relationship to existing character
            
        Returns:
            Name of new family member
        """
        if ' ' not in existing_family_member:
            raise ValueError("Existing family member must have both first and last name")
            
        family_surname = existing_family_member.split()[-1]
        return self.generate_family_member(family_surname, relationship, existing_family_member)
    
    def generate_multiple_names(self, count: int, roles: Optional[List[str]] = None) -> List[str]:
        """
        Generate multiple unique names at once
        
        Args:
            count: Number of names to generate
            roles: Optional list of role hints for each name
        
        Returns:
            List of unique names
        """
        if roles and len(roles) != count:
            roles = None  # Ignore roles if count doesn't match
            
        names = []
        for i in range(count):
            role = roles[i] if roles else None
            names.append(self.generate_unique_name(role))
            
        return names
    
    def get_character_suggestions(self, description: str) -> Dict[str, str]:
        """
        Generate character name suggestions based on description
        
        Args:
            description: Brief character description
            
        Returns:
            Dictionary with multiple name options
        """
        suggestions = {}
        
        # Generate 3 different name options
        for i in range(3):
            name = self.generate_unique_name()
            suggestions[f"option_{i+1}"] = name
            
        return suggestions
    
    def save_used_names(self) -> None:
        """Save used names and family data to prevent duplicates across sessions (if case_path provided)"""
        if not self.case_path:
            return
            
        # Save to case-specific file to track names used in this case
        names_file = self.case_path / "game_state" / "used_character_names.json"
        names_file.parent.mkdir(parents=True, exist_ok=True)
        
        case_names = {name for name in self.used_names if self._is_recent_name(name)}
        
        with open(names_file, 'w', encoding='utf-8') as f:
            json.dump(list(case_names), f, indent=2)
            
        # Save family data
        families_file = self.case_path / "game_state" / "character_families.json"
        family_data = {
            "surname_to_family": self.surname_families,
            "last_updated": str(Path(__file__).stat().st_mtime)
        }
        
        with open(families_file, 'w', encoding='utf-8') as f:
            json.dump(family_data, f, indent=2)
    
    def _is_recent_name(self, name: str) -> bool:
        """Determine if a name was generated recently (simple heuristic)"""
        # For now, just save all names. Could be enhanced with timestamp tracking
        return True


def main():
    """CLI interface for character name generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate unique character names with family support")
    parser.add_argument("--count", type=int, default=1, help="Number of names to generate")
    parser.add_argument("--role", type=str, help="Character role hint")
    parser.add_argument("--case-path", type=str, help="Case directory path for tracking")
    
    # Family-related commands
    parser.add_argument("--family-member", type=str, help="Generate family member with this surname")
    parser.add_argument("--relationship", type=str, default="sibling", help="Relationship type (spouse, sibling, parent, child)")
    parser.add_argument("--reference-name", type=str, help="Existing family member name for context")
    parser.add_argument("--create-family", type=int, metavar="SIZE", help="Create entire family of specified size")
    parser.add_argument("--family-surname", type=str, help="Specific surname for family creation")
    parser.add_argument("--add-to-family", type=str, help="Add family member to existing character")
    parser.add_argument("--surname-suggestions", nargs="+", help="Get surname suggestions avoiding these existing names")
    
    args = parser.parse_args()
    
    generator = CharacterNameGenerator(args.case_path)
    
    if args.family_member:
        # Generate family member with specified surname
        name = generator.generate_family_member(args.family_member, args.relationship, args.reference_name)
        print(f"Family member: {name}")
        print(f"Relationship: {args.relationship}")
        if args.reference_name:
            print(f"Related to: {args.reference_name}")
            
    elif args.create_family:
        # Create entire family
        family = generator.create_family(args.create_family, args.family_surname)
        print(f"Created family of {args.create_family}:")
        for role, name in family.items():
            print(f"  {role}: {name}")
            
    elif args.add_to_family:
        # Add member to existing family
        try:
            new_member = generator.add_family_member_to_existing(args.add_to_family, args.relationship)
            print(f"Added family member: {new_member}")
            print(f"Relationship to {args.add_to_family}: {args.relationship}")
        except ValueError as e:
            print(f"Error: {e}")
            
    elif args.surname_suggestions:
        # Get surname suggestions
        suggestions = generator.get_family_surname_suggestions(args.surname_suggestions)
        print("Surname suggestions:")
        for i, surname in enumerate(suggestions, 1):
            print(f"  {i}. {surname}")
            
    elif args.count == 1:
        # Standard single name generation
        name = generator.generate_unique_name(args.role)
        print(name)
    else:
        # Multiple name generation
        names = generator.generate_multiple_names(args.count)
        for name in names:
            print(name)
    
    # Save any changes
    generator.save_used_names()


if __name__ == "__main__":
    main()