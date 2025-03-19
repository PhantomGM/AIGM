"""
Game State Management

This module manages the overall state of a game session, tracking important information such as
the current location, active characters, game timeline, and environmental conditions.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Set, Tuple, Union
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GameState:
    """
    Manages the overall state of a game session.
    
    The GameState class tracks important information about the current game session,
    including location, characters, time, and environmental conditions. It provides
    methods to update and query this state and maintains a history of significant events.
    """
    
    def __init__(self, game_id: str = None, system: str = "dnd5e"):
        """
        Initialize a new game state.
        
        Args:
            game_id: Unique identifier for this game session.
            system: The game system being used (e.g., "dnd5e", "pathfinder").
        """
        self.game_id = game_id or f"game_{int(time.time())}"
        self.system = system
        
        # Basic game state
        self.current_location = ""
        self.active_characters = {}
        self.active_npcs = set()
        self.active_quests = {}
        self.discovered_locations = set()
        self.game_time = {
            "day": 1,
            "hour": 8,
            "minute": 0
        }
        
        # Environmental conditions
        self.environment = {
            "weather": "clear",
            "time_of_day": "morning",
            "season": "summer",
            "lighting": "natural daylight",
            "temperature": "comfortable",
            "ambient_noise": "typical for setting"
        }
        
        # Track significant events in the game
        self.event_history = []
        
        # Game mode ("exploration", "combat", "social", "downtime")
        self.game_mode = "exploration"
        
        # Session tracking
        self.session_start_time = time.time()
        self.session_number = 1
        
        logger.info(f"Initialized new game state with ID {self.game_id}")
    
    def update_location(self, location_name: str) -> None:
        """
        Update the current location.
        
        Args:
            location_name: The name of the new location.
        """
        self.current_location = location_name
        self.discovered_locations.add(location_name)
        
        # Record this as an event
        self.add_event("location_change", {
            "previous_location": self.current_location,
            "new_location": location_name
        })
        
        logger.info(f"Updated location to {location_name}")
    
    def add_active_character(self, character_id: str, character_data: Dict[str, Any]) -> None:
        """
        Add or update an active player character.
        
        Args:
            character_id: Unique identifier for the character.
            character_data: Dictionary of character information.
        """
        self.active_characters[character_id] = character_data
        logger.info(f"Added active character {character_id}")
    
    def remove_active_character(self, character_id: str) -> bool:
        """
        Remove a character from the active characters.
        
        Args:
            character_id: Unique identifier for the character.
            
        Returns:
            True if the character was removed, False if not found.
        """
        if character_id in self.active_characters:
            del self.active_characters[character_id]
            logger.info(f"Removed active character {character_id}")
            return True
        else:
            logger.warning(f"Attempted to remove non-existent character {character_id}")
            return False
    
    def add_active_npc(self, npc_name: str) -> None:
        """
        Add an NPC to the active NPCs in the current scene.
        
        Args:
            npc_name: The name of the NPC.
        """
        self.active_npcs.add(npc_name)
        logger.info(f"Added active NPC {npc_name}")
    
    def remove_active_npc(self, npc_name: str) -> bool:
        """
        Remove an NPC from the active NPCs.
        
        Args:
            npc_name: The name of the NPC.
            
        Returns:
            True if the NPC was removed, False if not found.
        """
        if npc_name in self.active_npcs:
            self.active_npcs.remove(npc_name)
            logger.info(f"Removed active NPC {npc_name}")
            return True
        else:
            logger.warning(f"Attempted to remove non-existent active NPC {npc_name}")
            return False
    
    def update_game_time(self, days: int = 0, hours: int = 0, minutes: int = 0) -> None:
        """
        Update the in-game time by the specified amount.
        
        Args:
            days: Number of days to add.
            hours: Number of hours to add.
            minutes: Number of minutes to add.
        """
        # Convert the time to total minutes for easier calculation
        total_minutes = (
            self.game_time["day"] * 24 * 60 +
            self.game_time["hour"] * 60 +
            self.game_time["minute"]
        )
        
        # Add the specified time
        total_minutes += days * 24 * 60 + hours * 60 + minutes
        
        # Convert back to days, hours, minutes
        self.game_time["day"] = total_minutes // (24 * 60)
        remaining_minutes = total_minutes % (24 * 60)
        self.game_time["hour"] = remaining_minutes // 60
        self.game_time["minute"] = remaining_minutes % 60
        
        # Update time of day based on the hour
        if 5 <= self.game_time["hour"] < 8:
            self.environment["time_of_day"] = "early morning"
        elif 8 <= self.game_time["hour"] < 12:
            self.environment["time_of_day"] = "morning"
        elif 12 <= self.game_time["hour"] < 14:
            self.environment["time_of_day"] = "noon"
        elif 14 <= self.game_time["hour"] < 17:
            self.environment["time_of_day"] = "afternoon"
        elif 17 <= self.game_time["hour"] < 20:
            self.environment["time_of_day"] = "evening"
        elif 20 <= self.game_time["hour"] < 23:
            self.environment["time_of_day"] = "night"
        else:
            self.environment["time_of_day"] = "late night"
        
        # Update lighting based on time of day
        if 6 <= self.game_time["hour"] < 19:
            self.environment["lighting"] = "natural daylight"
        else:
            self.environment["lighting"] = "darkness"
        
        logger.info(f"Updated game time to Day {self.game_time['day']}, {self.game_time['hour']}:{self.game_time['minute']:02d}")
    
    def update_environment(self, updates: Dict[str, str]) -> None:
        """
        Update environmental conditions.
        
        Args:
            updates: Dictionary of environmental aspects to update.
        """
        for key, value in updates.items():
            if key in self.environment:
                self.environment[key] = value
                logger.info(f"Updated environment {key}: {value}")
    
    def add_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Add a significant event to the event history.
        
        Args:
            event_type: The type of event.
            event_data: Additional data about the event.
        """
        event = {
            "type": event_type,
            "data": event_data,
            "game_time": self.game_time.copy(),
            "real_time": time.time(),
            "location": self.current_location
        }
        
        self.event_history.append(event)
        logger.info(f"Added event: {event_type}")
    
    def set_game_mode(self, mode: str) -> None:
        """
        Set the current game mode.
        
        Args:
            mode: The game mode to set (e.g., "exploration", "combat", "social", "downtime").
        """
        valid_modes = ["exploration", "combat", "social", "downtime"]
        if mode not in valid_modes:
            logger.warning(f"Invalid game mode: {mode}. Valid modes are {valid_modes}")
            return
        
        self.game_mode = mode
        logger.info(f"Set game mode to {mode}")
    
    def get_active_character_ids(self) -> List[str]:
        """
        Get the list of active character IDs.
        
        Returns:
            A list of character IDs.
        """
        return list(self.active_characters.keys())
    
    def get_active_npc_names(self) -> List[str]:
        """
        Get the list of active NPC names.
        
        Returns:
            A list of NPC names.
        """
        return list(self.active_npcs)
    
    def get_recent_events(self, count: int = 5, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the most recent events from the event history.
        
        Args:
            count: The number of events to retrieve.
            event_type: Optional filter for event type.
            
        Returns:
            A list of recent events.
        """
        if event_type:
            filtered_events = [e for e in self.event_history if e["type"] == event_type]
            return filtered_events[-count:]
        else:
            return self.event_history[-count:]
    
    def get_game_time_string(self) -> str:
        """
        Get a formatted string representing the current game time.
        
        Returns:
            A string representation of the game time.
        """
        return f"Day {self.game_time['day']}, {self.game_time['hour']}:{self.game_time['minute']:02d}"
    
    def get_environment_description(self) -> str:
        """
        Get a description of the current environmental conditions.
        
        Returns:
            A string describing the environment.
        """
        return f"It is {self.environment['time_of_day']} on a {self.environment['weather']} {self.environment['season']} day. " \
               f"The temperature is {self.environment['temperature']} and the lighting is {self.environment['lighting']}."
    
    def save_to_file(self, filepath: str) -> bool:
        """
        Save the game state to a file.
        
        Args:
            filepath: Path to the file to save.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Convert sets to lists for JSON serialization
            state_dict = self.__dict__.copy()
            state_dict["active_npcs"] = list(self.active_npcs)
            state_dict["discovered_locations"] = list(self.discovered_locations)
            
            with open(filepath, 'w') as f:
                json.dump(state_dict, f, indent=2)
            
            logger.info(f"Saved game state to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving game state to {filepath}: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'GameState':
        """
        Load a game state from a file.
        
        Args:
            filepath: Path to the file to load.
            
        Returns:
            A new GameState instance with the loaded state.
        """
        try:
            with open(filepath, 'r') as f:
                state_dict = json.load(f)
            
            # Create a new instance
            game_state = cls(game_id=state_dict.get("game_id"), system=state_dict.get("system"))
            
            # Update attributes from the loaded state
            game_state.current_location = state_dict.get("current_location", "")
            game_state.active_characters = state_dict.get("active_characters", {})
            game_state.active_npcs = set(state_dict.get("active_npcs", []))
            game_state.active_quests = state_dict.get("active_quests", {})
            game_state.discovered_locations = set(state_dict.get("discovered_locations", []))
            game_state.game_time = state_dict.get("game_time", {"day": 1, "hour": 8, "minute": 0})
            game_state.environment = state_dict.get("environment", {})
            game_state.event_history = state_dict.get("event_history", [])
            game_state.game_mode = state_dict.get("game_mode", "exploration")
            game_state.session_number = state_dict.get("session_number", 1)
            
            logger.info(f"Loaded game state from {filepath}")
            return game_state
        except Exception as e:
            logger.error(f"Error loading game state from {filepath}: {e}")
            return cls()  # Return a new default instance
    
    def to_context_dict(self) -> Dict[str, Any]:
        """
        Convert the game state to a dictionary suitable for providing as context to agents.
        
        Returns:
            A dictionary with key game state information.
        """
        # Create a simplified version of the game state for context
        context = {
            "current_location": self.current_location,
            "active_characters": self.active_characters,
            "active_npcs": list(self.active_npcs),
            "game_time": self.get_game_time_string(),
            "environment": self.environment,
            "game_mode": self.game_mode,
        }
        
        # Add recent events (last 3)
        context["recent_events"] = self.get_recent_events(count=3)
        
        return context
