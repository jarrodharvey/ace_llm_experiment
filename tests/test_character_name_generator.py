#!/usr/bin/env python3
"""
Unit tests for character name generator
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module to test
import sys
sys.path.append(str(Path(__file__).parent.parent / "scripts"))
from character_name_generator import CharacterNameGenerator


class TestCharacterNameGenerator:
    
    def test_initialization_without_case_path(self):
        """Test generator initializes properly without case path"""
        generator = CharacterNameGenerator()
        assert generator.fake is not None
        assert generator.case_path is None
        assert isinstance(generator.used_names, set)
    
    def test_initialization_with_case_path(self):
        """Test generator initializes properly with case path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = CharacterNameGenerator(temp_dir)
            assert generator.case_path == Path(temp_dir)
            assert isinstance(generator.used_names, set)
    
    def test_is_person_name_filter(self):
        """Test person name filtering logic"""
        generator = CharacterNameGenerator()
        
        # Valid person names
        assert generator._is_person_name("John Smith")
        assert generator._is_person_name("Mary Jane Watson")
        assert generator._is_person_name("Dr. House")
        
        # Invalid person names (case files, evidence, etc.)
        assert not generator._is_person_name("Prosecution Case File")
        assert not generator._is_person_name("Evidence Report")
        assert not generator._is_person_name("Trial Document")
        assert not generator._is_person_name("Simple Investigation")
        
        # Invalid format (single words, numbers, etc.)
        assert not generator._is_person_name("John")
        assert not generator._is_person_name("123")
        assert not generator._is_person_name("John123")
    
    def test_generate_unique_name(self):
        """Test basic name generation"""
        generator = CharacterNameGenerator()
        
        name = generator.generate_unique_name()
        assert isinstance(name, str)
        assert len(name.split()) >= 2  # Should have at least first and last name
        assert name in generator.used_names  # Should be added to used names
    
    def test_generate_unique_name_with_role(self):
        """Test name generation with role hint"""
        generator = CharacterNameGenerator()
        
        name = generator.generate_unique_name("judge")
        assert isinstance(name, str)
        assert len(name.split()) >= 2
        assert name in generator.used_names
    
    def test_uniqueness_enforcement(self):
        """Test that generated names are unique"""
        generator = CharacterNameGenerator()
        
        # Mock faker to return predictable names for testing
        with patch.object(generator.fake, 'first_name') as mock_first, \
             patch.object(generator.fake, 'last_name') as mock_last:
            
            # First call returns John Smith
            mock_first.side_effect = ["John", "John", "Jane"]
            mock_last.side_effect = ["Smith", "Smith", "Doe"]
            
            # First name should work
            name1 = generator.generate_unique_name()
            assert name1 == "John Smith"
            
            # Second attempt with same name should try again and get Jane Doe
            name2 = generator.generate_unique_name()
            assert name2 == "Jane Doe"
            assert name1 != name2
    
    def test_generate_multiple_names(self):
        """Test generation of multiple names"""
        generator = CharacterNameGenerator()
        
        names = generator.generate_multiple_names(3)
        assert len(names) == 3
        assert len(set(names)) == 3  # All names should be unique
        
        for name in names:
            assert isinstance(name, str)
            assert len(name.split()) >= 2
            assert name in generator.used_names
    
    def test_generate_multiple_names_with_roles(self):
        """Test generation of multiple names with role hints"""
        generator = CharacterNameGenerator()
        
        roles = ["judge", "prosecutor", "witness"]
        names = generator.generate_multiple_names(3, roles)
        assert len(names) == 3
        assert len(set(names)) == 3
    
    def test_generate_multiple_names_mismatched_roles(self):
        """Test multiple name generation with mismatched role count"""
        generator = CharacterNameGenerator()
        
        # Should work fine and ignore roles if count doesn't match
        names = generator.generate_multiple_names(3, ["judge"])
        assert len(names) == 3
    
    def test_get_character_suggestions(self):
        """Test character suggestion generation"""
        generator = CharacterNameGenerator()
        
        suggestions = generator.get_character_suggestions("mysterious witness")
        assert isinstance(suggestions, dict)
        assert len(suggestions) == 3  # Should provide 3 options
        assert "option_1" in suggestions
        assert "option_2" in suggestions
        assert "option_3" in suggestions
        
        # All suggestions should be unique
        values = list(suggestions.values())
        assert len(set(values)) == len(values)
    
    def test_extract_names_from_json_data(self):
        """Test extraction of names from complex JSON structures"""
        generator = CharacterNameGenerator()
        used_names = set()
        
        # Test data with various structures
        test_data = {
            "characters": [
                {"name": "John Smith", "role": "witness"},
                {"name": "Jane Doe", "role": "prosecutor"}
            ],
            "evidence": {"name": "Evidence File"},  # Should be filtered out
            "case_info": {
                "defendant": {"name": "Bob Johnson"},
                "file_name": "Case Report"  # Should be filtered out
            }
        }
        
        generator._extract_names_from_data(test_data, used_names)
        
        # Should contain person names but not file names
        assert "John Smith" in used_names
        assert "Jane Doe" in used_names
        assert "Bob Johnson" in used_names
        assert "Evidence File" not in used_names
        assert "Case Report" not in used_names
    
    def test_name_persistence_with_case_path(self):
        """Test saving and loading used names for a specific case"""
        with tempfile.TemporaryDirectory() as temp_dir:
            case_path = Path(temp_dir)
            game_state_dir = case_path / "game_state"
            game_state_dir.mkdir(parents=True)
            
            generator = CharacterNameGenerator(str(case_path))
            
            # Generate some names
            name1 = generator.generate_unique_name()
            name2 = generator.generate_unique_name()
            
            # Save the used names
            generator.save_used_names()
            
            # Check that file was created
            names_file = game_state_dir / "used_character_names.json"
            assert names_file.exists()
            
            # Verify content
            with open(names_file) as f:
                saved_names = json.load(f)
            assert isinstance(saved_names, list)
            assert len(saved_names) >= 2
    
    def test_fallback_name_generation(self):
        """Test fallback behavior when uniqueness is impossible"""
        generator = CharacterNameGenerator()
        
        # This is a bit tricky to test since faker has a huge name pool
        # Instead, test the fallback logic by mocking a limited name set
        original_generate = generator.generate_unique_name
        
        with patch.object(generator.fake, 'first_name', return_value="Test"):
            with patch.object(generator.fake, 'last_name', return_value="Name"):
                with patch.object(generator.fake, 'random_number', return_value=123):
                    # Fill up the name pool to force iteration
                    generator.used_names.add("Test Name")
                    
                    # Since we can't easily test the 100-attempt limit,
                    # just verify that fallback naming works
                    fallback_name = f"Test Name-123"
                    assert fallback_name not in generator.used_names
                    
                    # The method should eventually return a valid name
                    name = generator.generate_unique_name()
                    assert isinstance(name, str)
                    assert len(name.split()) >= 2


class TestCharacterNameGeneratorCLI:
    
    def test_cli_single_name(self, capsys):
        """Test CLI with single name generation"""
        with patch('sys.argv', ['character_name_generator.py']):
            from character_name_generator import main
            main()
            captured = capsys.readouterr()
            assert len(captured.out.strip().split()) >= 2  # Should be first + last name
    
    def test_cli_multiple_names(self, capsys):
        """Test CLI with multiple name generation"""
        with patch('sys.argv', ['character_name_generator.py', '--count', '3']):
            from character_name_generator import main
            main()
            captured = capsys.readouterr()
            lines = captured.out.strip().split('\n')
            assert len(lines) == 3
    
    def test_cli_with_role(self, capsys):
        """Test CLI with role hint"""
        with patch('sys.argv', ['character_name_generator.py', '--role', 'judge']):
            from character_name_generator import main
            main()
            captured = capsys.readouterr()
            assert len(captured.out.strip().split()) >= 2


class TestFamilyNameGeneration:
    
    def test_generate_family_member_basic(self):
        """Test basic family member generation with shared surname"""
        generator = CharacterNameGenerator()
        
        family_member = generator.generate_family_member("Smith", "sibling")
        assert family_member.endswith(" Smith")
        assert len(family_member.split()) == 2
        assert family_member in generator.used_names
    
    def test_generate_family_member_with_relationship(self):
        """Test family member generation with different relationship types"""
        generator = CharacterNameGenerator()
        
        # Test different relationship types
        relationships = ["spouse", "sibling", "parent", "child", "father", "mother", "son", "daughter"]
        
        for relationship in relationships:
            family_member = generator.generate_family_member("Johnson", relationship)
            assert family_member.endswith(" Johnson")
            assert family_member in generator.used_names
    
    def test_family_surname_tracking(self):
        """Test that family surnames are properly tracked"""
        generator = CharacterNameGenerator()
        
        # Generate first family member
        member1 = generator.generate_family_member("Wilson", "parent")
        assert "Wilson" in generator.surname_families
        
        # Generate second family member with same surname
        member2 = generator.generate_family_member("Wilson", "child")
        assert member2.endswith(" Wilson")
        assert member1 != member2  # Different first names
        
        # Both should share the same family ID
        family_id = generator.surname_families["Wilson"]
        assert family_id.startswith("family_")
        assert "wilson" in family_id.lower()
    
    def test_create_family_basic(self):
        """Test basic family creation"""
        generator = CharacterNameGenerator()
        
        family = generator.create_family(3)
        assert len(family) == 3
        assert "parent1" in family
        assert "parent2" in family
        assert "child1" in family
        
        # All should share same surname
        surnames = [name.split()[-1] for name in family.values()]
        assert len(set(surnames)) == 1  # All same surname
        
        # All names should be unique
        assert len(set(family.values())) == 3
    
    def test_create_family_with_custom_surname(self):
        """Test family creation with specified surname"""
        generator = CharacterNameGenerator()
        
        family = generator.create_family(2, family_surname="Custom")
        assert len(family) == 2
        
        # All should have specified surname
        for name in family.values():
            assert name.endswith(" Custom")
    
    def test_create_family_with_structure(self):
        """Test family creation with custom structure"""
        generator = CharacterNameGenerator()
        
        structure = {
            "husband": "spouse",
            "wife": "spouse", 
            "son": "child",
            "daughter": "child"
        }
        
        family = generator.create_family(4, family_structure=structure)
        assert len(family) == 4
        assert "husband" in family
        assert "wife" in family
        assert "son" in family
        assert "daughter" in family
        
        # All should share same surname
        surnames = [name.split()[-1] for name in family.values()]
        assert len(set(surnames)) == 1
    
    def test_add_family_member_to_existing(self):
        """Test adding family member to existing character"""
        generator = CharacterNameGenerator()
        
        # Create base character
        existing_name = "John Smith"
        generator.used_names.add(existing_name)
        
        # Add family member
        new_member = generator.add_family_member_to_existing(existing_name, "brother")
        
        assert new_member.endswith(" Smith")
        assert new_member != existing_name
        assert new_member in generator.used_names
    
    def test_add_family_member_error_handling(self):
        """Test error handling for invalid existing names"""
        generator = CharacterNameGenerator()
        
        with pytest.raises(ValueError):
            generator.add_family_member_to_existing("OneName", "sibling")
    
    def test_surname_suggestions(self):
        """Test surname suggestion generation"""
        generator = CharacterNameGenerator()
        
        existing_names = ["John Smith", "Jane Doe", "Bob Johnson"]
        suggestions = generator.get_family_surname_suggestions(existing_names)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5
        
        # None of the suggestions should conflict with existing names
        existing_surnames = {"Smith", "Doe", "Johnson"}
        for suggestion in suggestions:
            assert suggestion not in existing_surnames
    
    def test_contextual_first_name_generation(self):
        """Test contextual first name generation based on relationship"""
        generator = CharacterNameGenerator()
        
        # Test different relationship types
        relationships = ["spouse", "parent", "child", "sibling"]
        
        for relationship in relationships:
            first_name = generator._generate_contextual_first_name(relationship)
            assert isinstance(first_name, str)
            assert len(first_name) > 0
            assert first_name.replace(".", "").isalpha()  # Allow for names like "Dr."
    
    def test_family_persistence(self):
        """Test saving and loading family data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            case_path = Path(temp_dir)
            generator = CharacterNameGenerator(str(case_path))
            
            # Create family
            family = generator.create_family(2, "TestFamily")
            generator.save_used_names()
            
            # Check that family data is saved
            families_file = case_path / "game_state" / "character_families.json"
            assert families_file.exists()
            
            with open(families_file) as f:
                family_data = json.load(f)
            
            assert "surname_to_family" in family_data
            assert "TestFamily" in family_data["surname_to_family"]
    
    def test_family_uniqueness_across_cases(self):
        """Test that family names remain unique across different cases"""
        generator1 = CharacterNameGenerator()
        generator2 = CharacterNameGenerator()
        
        # Generate families in both generators
        family1 = generator1.create_family(2, "CommonName")
        family2 = generator2.create_family(2, "CommonName")
        
        # Names within each family should be unique
        all_names = list(family1.values()) + list(family2.values())
        assert len(set(all_names)) == len(all_names)  # All unique
    
    def test_large_family_generation(self):
        """Test generation of larger families"""
        generator = CharacterNameGenerator()
        
        family = generator.create_family(5)
        assert len(family) == 5
        
        # Should include parents and children
        roles = list(family.keys())
        assert "parent1" in roles
        assert "parent2" in roles
        assert "child1" in roles
        assert "child2" in roles
        assert "child3" in roles
        
        # All should share surname
        surnames = [name.split()[-1] for name in family.values()]
        assert len(set(surnames)) == 1


class TestFamilyNameGeneratorCLI:
    
    def test_cli_family_creation(self, capsys):
        """Test CLI family creation"""
        with patch('sys.argv', ['character_name_generator.py', '--create-family', '2']):
            from character_name_generator import main
            main()
            captured = capsys.readouterr()
            assert "Created family of 2:" in captured.out
            assert "parent1:" in captured.out
            assert "parent2:" in captured.out
    
    def test_cli_add_family_member(self, capsys):
        """Test CLI adding family member"""
        with patch('sys.argv', ['character_name_generator.py', '--add-to-family', 'John Smith', '--relationship', 'brother']):
            from character_name_generator import main
            main()
            captured = capsys.readouterr()
            assert "Added family member:" in captured.out
            assert "Smith" in captured.out
            assert "brother" in captured.out
    
    def test_cli_surname_suggestions(self, capsys):
        """Test CLI surname suggestions"""
        with patch('sys.argv', ['character_name_generator.py', '--surname-suggestions', 'John Smith', 'Jane Doe']):
            from character_name_generator import main
            main()
            captured = capsys.readouterr()
            assert "Surname suggestions:" in captured.out


class TestAgeAndOccupationGeneration:
    """Test age and occupation generation features"""
    
    def setup_method(self):
        self.generator = CharacterNameGenerator()
    
    def test_age_generation_without_role(self):
        """Test age generation without role hint"""
        age = self.generator.generate_age()
        assert isinstance(age, int)
        assert 18 <= age <= 75
    
    def test_age_generation_with_role_hints(self):
        """Test age generation with various role hints"""
        # Judge should be older and experienced
        judge_age = self.generator.generate_age("judge")
        assert 40 <= judge_age <= 70
        
        # Student should be younger
        student_age = self.generator.generate_age("student")
        assert 18 <= student_age <= 30
        
        # Security guard should be in physical job range
        guard_age = self.generator.generate_age("security guard")
        assert 21 <= guard_age <= 55
        
        # Doctor should need extensive education
        doctor_age = self.generator.generate_age("doctor")
        assert 30 <= doctor_age <= 70
    
    def test_occupation_generation_with_role_mapping(self):
        """Test occupation generation with role hint mapping"""
        # Direct role mappings should work
        assert self.generator.generate_occupation(35, "detective") == "detective"
        assert self.generator.generate_occupation(45, "judge") == "judge"
        assert self.generator.generate_occupation(20, "student") == "student"
        assert self.generator.generate_occupation(30, "doctor") == "doctor"
        assert self.generator.generate_occupation(25, "security guard") == "security guard"
    
    def test_occupation_generation_without_role(self):
        """Test occupation generation without role hint"""
        # Should generate random occupation using Faker
        occupation = self.generator.generate_occupation(35, None)
        assert isinstance(occupation, str)
        assert len(occupation) > 0
        
        # Young adults might get student randomly
        occupation_young = self.generator.generate_occupation(19, None)
        assert isinstance(occupation_young, str)
        assert len(occupation_young) > 0
    
    def test_generate_name_with_classification_includes_age_occupation(self):
        """Test that name generation includes age and occupation"""
        # Create a temporary case directory for testing
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        temp_case = Path(temp_dir) / "test_case"
        temp_case.mkdir(exist_ok=True)
        (temp_case / "game_state").mkdir(exist_ok=True)
        
        try:
            generator_with_case = CharacterNameGenerator(str(temp_case))
            
            # Test with role hint
            result = generator_with_case.generate_name_with_classification(2, "judge")
            assert isinstance(result, tuple)
            assert len(result) == 5
            
            name, classification, age, occupation, personality = result
            assert isinstance(name, str)
            assert classification in ["true_killer", "red_herring", "conspirator"]
            assert isinstance(age, int)
            assert isinstance(occupation, str)
            assert isinstance(personality, str)
            
            # Judge should have appropriate age and occupation
            assert 40 <= age <= 70
            assert occupation == "judge"
            
            # Personality should be from the predefined list
            expected_traits = [
                "Adamant", "Bashful", "Bold", "Brave", "Calm", "Careful", "Docile", 
                "Gentle", "Hardy", "Hasty", "Impish", "Jolly", "Lax", "Lonely", 
                "Mild", "Modest", "Naive", "Naughty", "Quiet", "Quirky", "Rash", 
                "Relaxed", "Sassy", "Serious", "Timid"
            ]
            assert personality in expected_traits
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_personality_trait_generation(self):
        """Test that personality traits are generated correctly"""
        expected_traits = [
            "Adamant", "Bashful", "Bold", "Brave", "Calm", "Careful", "Docile", 
            "Gentle", "Hardy", "Hasty", "Impish", "Jolly", "Lax", "Lonely", 
            "Mild", "Modest", "Naive", "Naughty", "Quiet", "Quirky", "Rash", 
            "Relaxed", "Sassy", "Serious", "Timid"
        ]
        
        # Test single personality trait generation
        personality = self.generator.generate_personality_trait()
        assert personality in expected_traits
        
        # Test that different calls can produce different traits
        personalities = [self.generator.generate_personality_trait() for _ in range(20)]
        assert len(set(personalities)) > 1  # Should have some variety
    
    def test_name_generation_with_personality(self):
        """Test name generation with personality traits"""
        # Test basic name with personality
        name_with_personality = self.generator.generate_unique_name(include_personality=True)
        assert "(" in name_with_personality
        assert ")" in name_with_personality
        
        # Extract personality from name
        personality = name_with_personality.split("(")[1].split(")")[0]
        expected_traits = [
            "Adamant", "Bashful", "Bold", "Brave", "Calm", "Careful", "Docile", 
            "Gentle", "Hardy", "Hasty", "Impish", "Jolly", "Lax", "Lonely", 
            "Mild", "Modest", "Naive", "Naughty", "Quiet", "Quirky", "Rash", 
            "Relaxed", "Sassy", "Serious", "Timid"
        ]
        assert personality in expected_traits
        
        # Test name generation without personality
        name_without_personality = self.generator.generate_unique_name(include_personality=False)
        assert "(" not in name_without_personality
        assert ")" not in name_without_personality
    
    def test_age_consistency_for_roles(self):
        """Test that generated ages are consistent with role requirements"""
        roles_with_education = ["lawyer", "attorney", "prosecutor", "doctor", "physician"]
        
        for role in roles_with_education:
            age = self.generator.generate_age(role)
            # These roles require higher education, so minimum age should be reasonable
            assert age >= 25, f"{role} should be at least 25 due to education requirements"
    
    def test_occupation_fallback_to_faker(self):
        """Test that occupation falls back to Faker for unrecognized roles"""
        occupation = self.generator.generate_occupation(30, "alien investigator")
        assert isinstance(occupation, str)
        assert len(occupation) > 0
        # Should not be "alien investigator" since it's not in our mapping
        assert occupation != "alien investigator"


if __name__ == "__main__":
    pytest.main([__file__])