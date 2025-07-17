"""
CourtRoom Core Module

Event-sourced game engine with plugin architecture for AI-driven mystery games.
"""

from .engine import CourtRoomEngine
from .state import EventStore, GameState
from .ai_director import AIDirector

__version__ = "2.0.0"
__all__ = ["CourtRoomEngine", "EventStore", "GameState", "AIDirector"]