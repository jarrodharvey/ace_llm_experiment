#!/usr/bin/env python3
"""
Red Herring Classification System
Provides case-length-aware character role classification with encrypted storage.
"""

import json
import base64
import random
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional


class RedHerringClassifier:
    """
    Manages character role classification for preventing predictable killer patterns.
    
    Uses deterministic RNG based on character names to assign roles:
    - 1-day cases: 1/2 chance of killer (50% red herring rate)
    - 2-day cases: 1/3 chance of killer (67% red herring rate) 
    - 3-day cases: 1/4 chance of killer (75% red herring rate)
    
    Role-based weighting adds narrative realism:
    - High Authority (0.3x): detective, judge, police, client, prosecutor, doctor
    - Normal Authority (1.0x): witness, lawyer, court staff, journalist  
    - High Suspicion (1.8x): security, business rival, ex-partner, family, debtor
    
    Classifications are stored in base64-encoded JSON for player spoiler prevention.
    """
    
    # Role weighting multipliers for killer probability
    ROLE_WEIGHTS = {
        # High Authority - Rare but impactful twists (0.3x multiplier)
        "detective": 0.3, "investigator": 0.3, "police": 0.3, "cop": 0.3,
        "judge": 0.3, "magistrate": 0.3,
        "client": 0.3, "defendant": 0.3,
        "prosecutor": 0.3, "district attorney": 0.3, "da": 0.3,
        "doctor": 0.3, "physician": 0.3, "medical examiner": 0.3, "coroner": 0.3,
        
        # Normal Authority - Standard probability (1.0x multiplier)  
        "witness": 1.0, "bystander": 1.0,
        "lawyer": 1.0, "attorney": 1.0, "counsel": 1.0,
        "court clerk": 1.0, "bailiff": 1.0, "stenographer": 1.0,
        "journalist": 1.0, "reporter": 1.0,
        "friend": 1.0, "neighbor": 1.0, "colleague": 1.0,
        
        # High Suspicion - More likely suspects (1.8x multiplier)
        "security": 1.8, "security guard": 1.8, "guard": 1.8,
        "business rival": 1.8, "competitor": 1.8, "rival": 1.8,
        "ex-spouse": 1.8, "ex-wife": 1.8, "ex-husband": 1.8, "ex-partner": 1.8,
        "family": 1.8, "relative": 1.8, "sibling": 1.8, "brother": 1.8, "sister": 1.8,
        "son": 1.8, "daughter": 1.8, "child": 1.8,
        "debtor": 1.8, "borrower": 1.8, "tenant": 1.8,
        "employee": 1.8, "worker": 1.8, "staff": 1.8,
        "landlord": 1.8, "creditor": 1.8
    }
    
    def __init__(self, case_path: str):
        self.case_path = Path(case_path)
        self.classifications_file = self.case_path / "game_state" / "character_classifications.b64"
        self.classifications = self._load_classifications()
    
    def classify_character(self, character_name: str, case_length: int, role_hint: Optional[str] = None) -> str:
        """
        Generate case-length and role-aware character classification.
        
        Args:
            character_name: The character's full name
            case_length: Case length (1, 2, or 3 days)
            role_hint: Optional role hint for weighting (e.g., "detective", "witness")
            
        Returns:
            "true_killer" or "red_herring"
        """
        # Check if already classified
        if character_name in self.classifications:
            return self.classifications[character_name]
        
        # Generate deterministic classification from character name, case length, and role
        role = self._generate_role_weighted(character_name, case_length, role_hint)
        
        # Store classification
        self.classifications[character_name] = role
        self._save_classifications()
        
        return role
    
    def get_character_role(self, character_name: str) -> Optional[str]:
        """
        Get existing character classification without generating new one.
        
        Args:
            character_name: The character's full name
            
        Returns:
            "true_killer", "red_herring", or None if not classified
        """
        return self.classifications.get(character_name)
    
    def get_all_classifications(self) -> Dict[str, str]:
        """
        Get all character classifications for GM reference.
        
        Returns:
            Dictionary mapping character names to roles
        """
        return self.classifications.copy()
    
    def get_potential_killers(self) -> list[str]:
        """
        Get list of characters classified as potential killers.
        
        Returns:
            List of character names with "true_killer" classification
        """
        return [name for name, role in self.classifications.items() 
                if role == "true_killer"]
    
    def get_red_herrings(self) -> list[str]:
        """
        Get list of characters classified as red herrings.
        
        Returns:
            List of character names with "red_herring" classification
        """
        return [name for name, role in self.classifications.items() 
                if role == "red_herring"]
    
    def _generate_role_weighted(self, character_name: str, case_length: int, role_hint: Optional[str] = None) -> str:
        """
        Generate deterministic role classification with role-based weighting.
        
        Args:
            character_name: The character's full name
            case_length: Case length determining base killer probability
            role_hint: Role hint for weighting adjustment
            
        Returns:
            "true_killer" or "red_herring"
        """
        # Create deterministic seed from character name and role
        seed_string = character_name
        if role_hint:
            seed_string += f":{role_hint.lower()}"
        
        name_hash = hashlib.md5(seed_string.encode()).hexdigest()
        seed = int(name_hash[:8], 16)  # Use first 8 hex chars as seed
        
        # Set random seed for deterministic results
        random.seed(seed)
        
        # Get base killer probability from case length
        base_killer_probability = 1.0 / (case_length + 1)
        
        # Apply role weighting
        role_weight = self._get_role_weight(role_hint)
        weighted_killer_probability = min(0.95, base_killer_probability * role_weight)  # Cap at 95%
        
        # Generate random number and compare to weighted probability
        roll = random.random()  # 0.0 to 1.0
        
        return "true_killer" if roll < weighted_killer_probability else "red_herring"
    
    def _generate_role(self, character_name: str, case_length: int) -> str:
        """
        Generate deterministic role classification from character name and case length (legacy method).
        
        Args:
            character_name: The character's full name
            case_length: Case length determining killer probability
            
        Returns:
            "true_killer" or "red_herring"
        """
        return self._generate_role_weighted(character_name, case_length, None)
    
    def _get_role_weight(self, role_hint: Optional[str]) -> float:
        """
        Get role weight multiplier for killer probability.
        
        Args:
            role_hint: Role hint string (case insensitive)
            
        Returns:
            Weight multiplier (0.3 for high authority, 1.0 for normal, 1.8 for high suspicion)
        """
        if not role_hint:
            return 1.0  # Default weight for no role hint
        
        role_lower = role_hint.lower().strip()
        
        # Check for exact matches first
        if role_lower in self.ROLE_WEIGHTS:
            return self.ROLE_WEIGHTS[role_lower]
        
        # Check for partial matches (for complex role descriptions)
        for role_key, weight in self.ROLE_WEIGHTS.items():
            if role_key in role_lower or role_lower in role_key:
                return weight
        
        # Default to normal weight if no match found
        return 1.0
    
    def _load_classifications(self) -> Dict[str, str]:
        """
        Load existing character classifications from base64-encoded file.
        
        Returns:
            Dictionary of character classifications
        """
        if not self.classifications_file.exists():
            return {}
        
        try:
            with open(self.classifications_file, 'r') as f:
                encoded_data = f.read().strip()
            
            # Decode base64 to JSON
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
            return json.loads(decoded_data)
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Could not load character classifications: {e}")
            return {}
    
    def _save_classifications(self) -> None:
        """
        Save character classifications to base64-encoded file.
        """
        # Ensure game_state directory exists
        self.classifications_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Encode JSON as base64
        json_data = json.dumps(self.classifications, indent=2)
        encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
        
        # Save to file
        with open(self.classifications_file, 'w') as f:
            f.write(encoded_data)
    
    def reset_classifications(self) -> None:
        """
        Clear all character classifications (for testing or case reset).
        """
        self.classifications = {}
        if self.classifications_file.exists():
            self.classifications_file.unlink()
    
    def get_classification_stats(self, case_length: int) -> Dict[str, Any]:
        """
        Get statistics about character classifications for this case.
        
        Args:
            case_length: Case length for probability calculations
            
        Returns:
            Dictionary with classification statistics
        """
        total_characters = len(self.classifications)
        killers = len(self.get_potential_killers())
        red_herrings = len(self.get_red_herrings())
        
        expected_killer_rate = 1.0 / (case_length + 1)
        expected_red_herring_rate = 1.0 - expected_killer_rate
        
        return {
            "total_characters": total_characters,
            "potential_killers": killers,
            "red_herrings": red_herrings,
            "actual_killer_rate": killers / total_characters if total_characters > 0 else 0,
            "actual_red_herring_rate": red_herrings / total_characters if total_characters > 0 else 0,
            "expected_killer_rate": expected_killer_rate,
            "expected_red_herring_rate": expected_red_herring_rate,
            "case_length": case_length
        }
    
    def get_weighted_probability(self, case_length: int, role_hint: Optional[str] = None) -> float:
        """
        Calculate the weighted killer probability for a given role and case length.
        
        Args:
            case_length: Case length (1, 2, or 3 days)
            role_hint: Role hint for weighting
            
        Returns:
            Weighted killer probability as a float between 0.0 and 1.0
        """
        base_probability = 1.0 / (case_length + 1)
        role_weight = self._get_role_weight(role_hint)
        return min(0.95, base_probability * role_weight)