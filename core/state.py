"""
Event-Sourced State Management

Immutable event log provides single source of truth.
Game state is computed from events, preventing corruption.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional


class EventStore:
    """Manages immutable event log for game state"""
    
    def __init__(self, events_file: Path):
        self.events_file = events_file
        self._events: List[Dict[str, Any]] = []
        self._load_events()
    
    def _load_events(self) -> None:
        """Load events from disk"""
        if self.events_file.exists():
            try:
                with open(self.events_file, 'r') as f:
                    data = json.load(f)
                    self._events = data.get("events", [])
            except (json.JSONDecodeError, KeyError):
                # Corrupted file, start fresh
                self._events = []
        else:
            self._events = []
    
    def add_event(self, event_data: Dict[str, Any]) -> str:
        """Add new event to the log"""
        
        # Create complete event with metadata
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_data["type"],
            "data": event_data["data"]
        }
        
        # Add to memory
        self._events.append(event)
        
        # Persist to disk
        self._save_events()
        
        return event["id"]
    
    def get_events(self, since_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get events, optionally since a specific event ID"""
        if since_id is None:
            return self._events.copy()
        
        # Find the index of the since_id event
        since_index = 0
        for i, event in enumerate(self._events):
            if event["id"] == since_id:
                since_index = i + 1
                break
        
        return self._events[since_index:].copy()
    
    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Get all events of a specific type"""
        return [e for e in self._events if e["type"] == event_type]
    
    def _save_events(self) -> None:
        """Persist events to disk"""
        
        # Create backup before writing
        if self.events_file.exists():
            backup_file = self.events_file.with_suffix('.json.backup')
            import shutil
            shutil.copy2(self.events_file, backup_file)
        
        # Write events atomically
        temp_file = self.events_file.with_suffix('.json.temp')
        
        data = {
            "version": "2.0",
            "created": datetime.now(timezone.utc).isoformat(),
            "event_count": len(self._events),
            "events": self._events
        }
        
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Atomic move
        temp_file.replace(self.events_file)
    
    def validate_integrity(self) -> Dict[str, Any]:
        """Validate event log integrity"""
        
        issues = []
        
        # Check for duplicate event IDs
        event_ids = [e["id"] for e in self._events]
        if len(event_ids) != len(set(event_ids)):
            issues.append("Duplicate event IDs found")
        
        # Check chronological ordering
        timestamps = [e["timestamp"] for e in self._events]
        if timestamps != sorted(timestamps):
            issues.append("Events not in chronological order")
        
        # Check required fields
        for i, event in enumerate(self._events):
            required_fields = ["id", "timestamp", "type", "data"]
            missing_fields = [f for f in required_fields if f not in event]
            if missing_fields:
                issues.append(f"Event {i}: missing fields {missing_fields}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "event_count": len(self._events),
            "first_event": self._events[0]["timestamp"] if self._events else None,
            "last_event": self._events[-1]["timestamp"] if self._events else None
        }


class GameState:
    """Computes current game state from event log"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self._cached_state: Optional[Dict[str, Any]] = None
        self._cache_valid_until_event: Optional[str] = None
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current game state computed from all events"""
        
        # Check if cache is still valid
        events = self.event_store.get_events()
        if (self._cached_state is not None and 
            events and 
            events[-1]["id"] == self._cache_valid_until_event):
            return self._cached_state.copy()
        
        # Rebuild state from events
        state = self._rebuild_state_from_events(events)
        
        # Update cache
        self._cached_state = state
        self._cache_valid_until_event = events[-1]["id"] if events else None
        
        return state.copy()
    
    def _rebuild_state_from_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rebuild complete state from event log"""
        
        # Initialize empty state
        state = {
            "case_info": {},
            "phase": "investigation",
            "status": "created",
            "gates": [],
            "evidence": {},
            "characters": {},
            "dice": {"rolls": [], "history": []},
            "trial": {"status": "not_started"},
            "saves": [],
            "current_location": "law_office",
            "metadata": {
                "created": None,
                "last_updated": None,
                "event_count": 0
            }
        }
        
        # Process events in order
        for event in events:
            self._apply_event_to_state(state, event)
        
        # Update metadata
        state["metadata"]["event_count"] = len(events)
        if events:
            state["metadata"]["created"] = events[0]["timestamp"]
            state["metadata"]["last_updated"] = events[-1]["timestamp"]
        
        return state
    
    def _apply_event_to_state(self, state: Dict[str, Any], event: Dict[str, Any]) -> None:
        """Apply a single event to the state"""
        
        event_type = event["type"]
        event_data = event["data"]
        
        if event_type == "case_created":
            state["case_info"] = {
                "case_name": event_data["case_name"],
                "case_id": event_data["case_id"], 
                "test_mode": event_data.get("test_mode", False),
                "created_by": event_data.get("created_by", "unknown"),
                "game_version": event_data.get("game_version", "1.0")
            }
            state["status"] = "created"
        
        elif event_type == "case_initialized":
            state["phase"] = event_data.get("phase", "investigation")
            state["status"] = event_data.get("status", "ready_to_play")
            state["gates"] = event_data.get("gates", [])
            state["current_location"] = event_data.get("current_location", "law_office")
        
        elif event_type == "evidence_added":
            evidence_id = event_data.get("id", event_data["name"])
            state["evidence"][evidence_id] = {
                "name": event_data["name"],
                "description": event_data["description"],
                "added_at": event["timestamp"],
                "location": event_data.get("location"),
                "tags": event_data.get("tags", [])
            }
        
        elif event_type == "character_met":
            character_id = event_data.get("id", event_data["name"])
            state["characters"][character_id] = {
                "name": event_data["name"],
                "role": event_data["role"],
                "trust_level": event_data.get("trust_level", 0),
                "met_at": event["timestamp"],
                "location": event_data.get("location"),
                "notes": event_data.get("notes", "")
            }
        
        elif event_type == "character_trust_updated":
            character_id = event_data["character_id"]
            if character_id in state["characters"]:
                state["characters"][character_id]["trust_level"] = event_data["new_trust_level"]
        
        elif event_type == "gate_started":
            gate_id = event_data["gate_id"]
            for gate in state["gates"]:
                if gate["id"] == gate_id:
                    gate["status"] = "in_progress"
                    gate["started_at"] = event["timestamp"]
                    break
        
        elif event_type == "gate_completed":
            gate_id = event_data["gate_id"]
            for gate in state["gates"]:
                if gate["id"] == gate_id:
                    gate["status"] = "completed"
                    gate["completed_at"] = event["timestamp"]
                    break
        
        elif event_type == "dice_rolled":
            roll_record = {
                "action": event_data["action"],
                "roll": event_data["roll"],
                "modifiers": event_data.get("modifiers", []),
                "total": event_data["total"],
                "result": event_data["result"],
                "timestamp": event["timestamp"]
            }
            state["dice"]["rolls"].append(roll_record)
            state["dice"]["history"] = state["dice"]["rolls"][-20:]  # Keep last 20
        
        elif event_type == "trial_started":
            state["phase"] = "trial"
            state["trial"]["status"] = "in_progress"
            state["trial"]["started_at"] = event["timestamp"]
        
        elif event_type == "location_changed":
            state["current_location"] = event_data["new_location"]
        
        elif event_type == "save_created":
            save_record = {
                "name": event_data["save_name"],
                "created_at": event["timestamp"],
                "event_id": event["id"]
            }
            state["saves"].append(save_record)
        
        # Add more event types as needed...
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get high-level summary of current state"""
        state = self.get_current_state()
        
        completed_gates = [g for g in state["gates"] if g.get("status") == "completed"]
        in_progress_gates = [g for g in state["gates"] if g.get("status") == "in_progress"]
        
        return {
            "case_name": state["case_info"].get("case_name", "Unknown"),
            "phase": state["phase"],
            "status": state["status"],
            "location": state["current_location"],
            "progress": {
                "gates_completed": len(completed_gates),
                "gates_total": len(state["gates"]),
                "current_gate": in_progress_gates[0]["name"] if in_progress_gates else None
            },
            "inventory": {
                "evidence_count": len(state["evidence"]),
                "character_count": len(state["characters"]),
                "dice_rolls": len(state["dice"]["rolls"])
            },
            "last_updated": state["metadata"]["last_updated"]
        }