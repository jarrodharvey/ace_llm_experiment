"""
Pytest configuration and shared fixtures
"""
import pytest
import tempfile
import shutil
import json
from pathlib import Path
import sys

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

@pytest.fixture
def temp_case_dir():
    """Create a temporary case directory for testing"""
    temp_dir = tempfile.mkdtemp()
    case_path = Path(temp_dir) / "test_case"
    
    # Create basic structure
    case_path.mkdir()
    (case_path / "backbone").mkdir()
    (case_path / "game_state").mkdir()
    (case_path / "saves").mkdir()
    
    yield case_path
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def minimal_case_structure(temp_case_dir):
    """Create minimal case structure with required files"""
    # Create backbone files
    backbone_dir = temp_case_dir / "backbone"
    with open(backbone_dir / "case_structure.json", 'w') as f:
        json.dump({"case_title": "Test Case", "case_id": "test_case"}, f)
    
    # Create game state files
    game_state_dir = temp_case_dir / "game_state"
    
    investigation_state = {
        "investigation_gates": {
            "gate1": "pending",
            "gate2": "pending", 
            "gate3": "pending"
        },
        "current_phase": "investigation",
        "case_length": 1,
        "evidence_collected": [],
        "character_trust_levels": {},
        "witnesses_interviewed": [],
        "current_location": "detention_center",
        "available_locations": ["detention_center", "courthouse"]
    }
    
    trial_state = {
        "trial_status": "not_started"
    }
    
    with open(game_state_dir / "investigation_progress.json", 'w') as f:
        json.dump(investigation_state, f, indent=2)
        
    with open(game_state_dir / "trial_progress.json", 'w') as f:
        json.dump(trial_state, f, indent=2)
    
    return temp_case_dir

@pytest.fixture
def case_with_inspiration_pool(minimal_case_structure):
    """Create case structure with legacy inspiration pool"""
    inspiration_pool = {
        "character_motivations": ["loyalty", "greed", "fear"],
        "relationship_dynamics": ["trust", "conflict", "alliance"],
        "evidence_obstacles": ["hidden", "destroyed", "corrupted"]
    }
    
    with open(minimal_case_structure / "inspiration_pool.json", 'w') as f:
        json.dump(inspiration_pool, f, indent=2)
    
    return minimal_case_structure

@pytest.fixture
def config_manager():
    """Create a mock configuration manager for testing"""
    from case_config import get_config_manager
    return get_config_manager()