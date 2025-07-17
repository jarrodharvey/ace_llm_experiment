"""
CourtRoom Game Plugins

Modular game mechanics for evidence, characters, dice, and trial systems.
"""

from .evidence import EvidencePlugin
from .characters import CharacterPlugin
from .dice import DicePlugin
from .trial import TrialPlugin

__all__ = ["EvidencePlugin", "CharacterPlugin", "DicePlugin", "TrialPlugin"]