"""
Game State Management

This module manages the overall state of a game session, tracking important information such as
the current location, active characters, game timeline, and environmental conditions.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Set, Tuple, Union
import json
from pathlib import Path
import os

# Import the system manager
from core.system_manager import SystemManager

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
    
    def __init__(self, game_id: str = None, system_id: str = "dnd5e"):
        """
        Initialize a new game state.
        
        Args:
            game_id: Unique identifier for this game session.
            system_id: The game system being used (e.g., "dnd5e", "pathfinder2e").
        """
        self.game_id = game_id or f"game_{int(time.time())}"
        
        # Initialize the system manager and select the system
        self.system_manager = SystemManager()
        self.system_id = system_id
        self.system_manager.select_system(system_id)
        self.system = self.system_manager.get_active_system()
        
        if not self.system:
            logger.warning(f"Game system '{system_id}' not found. Using default rules.")
        else:
            logger.info(f"Using game system: {self.system.name} (v{self.system.version})")
        
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
        
        # Session history for summaries and recall
        self.session_summaries = []
        
        # Knowledge base management
        self.knowledge_base = {
            "npcs": {},         # NPC information
            "locations": {},    # Location descriptions
            "items": {},        # Notable items and artifacts
            "factions": {},     # Organizations and factions
            "lore": {},         # World lore and history
            "quests": {},       # Additional quest details
            "player_notes": {}, # Optional player-added notes
            "custom": {}        # Custom knowledge entries
        }
        
        # Multimodal settings
        self.multimodal_settings = {
            "text_to_speech": False,
            "speech_to_text": False,
            "image_generation": False
        }
        
        logger.info(f"Initialized new game state with ID {self.game_id}")
    
    def change_system(self, system_id: str) -> bool:
        """
        Change the game system being used.
        
        Args:
            system_id: The ID of the new system to use
            
        Returns:
            True if the system was changed successfully, False otherwise
        """
        if self.system_manager.select_system(system_id):
            self.system_id = system_id
            self.system = self.system_manager.get_active_system()
            logger.info(f"Changed game system to: {self.system.name} (v{self.system.version})")
            
            # Add a game event for the system change
            self.add_event("system_change", {
                "previous_system": self.system_id,
                "new_system": system_id
            })
            
            return True
        else:
            logger.warning(f"Failed to change game system to '{system_id}'")
            return False
    
    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific rule from the current game system.
        
        Args:
            rule_id: Identifier for the rule
            
        Returns:
            Rule data if found, None otherwise
        """
        if self.system:
            return self.system.get_rule(rule_id)
        return None
    
    def update_location(self, location_name: str) -> None:
        """
        Update the current location.
        
        Args:
            location_name: The name of the new location.
        """
        previous_location = self.current_location
        self.current_location = location_name
        self.discovered_locations.add(location_name)
        
        # Record this as an event
        self.add_event("location_change", {
            "previous_location": previous_location,
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
    
    def add_session_summary(self, summary: Dict[str, Any]) -> None:
        """
        Add a summary of the current session.
        
        Args:
            summary: Dictionary containing session summary information.
                    Should include at least "title" and "content" keys.
        """
        # Add timestamp and session number
        summary["timestamp"] = time.time()
        summary["session_number"] = self.session_number
        
        # Add the current state information
        summary["location"] = self.current_location
        summary["characters"] = list(self.active_characters.keys())
        summary["npcs"] = list(self.active_npcs)
        summary["game_time"] = self.get_game_time_string()
        
        # Generate a unique ID for the summary if not provided
        if "id" not in summary:
            summary["id"] = f"summary_{int(time.time())}"
        
        self.session_summaries.append(summary)
        logger.info(f"Added summary for session {self.session_number}")
        
        # Create a directory for session summaries if it doesn't exist
        summaries_dir = Path(f"game_data/{self.game_id}/session_summaries")
        summaries_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the summary to a file
        summary_path = summaries_dir / f"session_{self.session_number}_{summary['id']}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Saved session summary to {summary_path}")
    
    def get_session_summaries(self, count: int = None) -> List[Dict[str, Any]]:
        """
        Get session summaries.
        
        Args:
            count: Number of most recent summaries to retrieve. If None, returns all.
            
        Returns:
            List of session summaries, newest first.
        """
        if count is None:
            return list(reversed(self.session_summaries))
        else:
            return list(reversed(self.session_summaries))[:count]
    
    def generate_session_summary(self) -> Dict[str, Any]:
        """
        Generate a basic session summary based on current game state and recent events.
        
        Returns:
            A dictionary containing the auto-generated session summary.
        """
        # Get the recent events for the summary
        recent_events = self.get_recent_events(count=10)
        
        # Build a title based on location and major events
        title = f"Session {self.session_number}: Adventures in {self.current_location}"
        
        # Create a basic content summary from recent events
        content_parts = [
            f"Session {self.session_number} Summary",
            f"Game Time: {self.get_game_time_string()}",
            f"Location: {self.current_location}",
            "\nKey Events:"
        ]
        
        # Add bullet points for each event
        for event in recent_events:
            event_time = f"Day {event['game_time']['day']}, {event['game_time']['hour']}:{event['game_time']['minute']:02d}"
            event_type = event['type'].replace('_', ' ').title()
            
            # Format the event description based on event type
            if event['type'] == 'location_change':
                desc = f"Party traveled from {event['data']['previous_location']} to {event['data']['new_location']}"
            elif event['type'] == 'combat_start':
                desc = f"Combat began against {event['data'].get('enemies', 'unknown foes')}"
            elif event['type'] == 'combat_end':
                desc = f"Combat ended with outcome: {event['data'].get('outcome', 'unknown')}"
            else:
                # Generic event description
                desc = f"{event_type} event occurred"
                
            content_parts.append(f"- {event_time}: {desc}")
        
        # Add active characters and NPCs
        content_parts.append("\nActive Characters:")
        for char_id, char_data in self.active_characters.items():
            char_name = char_data.get('name', char_id)
            content_parts.append(f"- {char_name}")
        
        content_parts.append("\nActive NPCs:")
        for npc in self.active_npcs:
            content_parts.append(f"- {npc}")
        
        # Combine all parts into content
        content = "\n".join(content_parts)
        
        return {
            "title": title,
            "content": content,
            "auto_generated": True,
            "id": f"auto_summary_{int(time.time())}"
        }
    
    def add_knowledge_entry(self, category: str, key: str, data: Dict[str, Any]) -> bool:
        """
        Add or update an entry in the knowledge base.
        
        Args:
            category: The category of knowledge (npcs, locations, items, etc.)
            key: Unique identifier for this entry within the category
            data: The data to store
            
        Returns:
            True if the entry was added successfully, False otherwise
        """
        if category not in self.knowledge_base:
            logger.warning(f"Invalid knowledge category: {category}")
            return False
        
        # Add metadata
        data["last_updated"] = time.time()
        if "first_added" not in data:
            data["first_added"] = time.time()
        
        # Add to knowledge base
        self.knowledge_base[category][key] = data
        logger.info(f"Added knowledge entry: {category}/{key}")
        
        # Automatically save the knowledge base
        self._save_knowledge_base()
        
        return True
    
    def get_knowledge_entry(self, category: str, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an entry from the knowledge base.
        
        Args:
            category: The category of knowledge
            key: The entry key
            
        Returns:
            The knowledge entry if found, None otherwise
        """
        if category not in self.knowledge_base:
            logger.warning(f"Invalid knowledge category: {category}")
            return None
        
        return self.knowledge_base[category].get(key)
    
    def search_knowledge_base(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for entries matching the query.
        
        Args:
            query: The search query string
            category: Optional category to limit the search
            
        Returns:
            List of matching knowledge entries with category and key information
        """
        results = []
        query = query.lower()
        
        categories = [category] if category else self.knowledge_base.keys()
        
        for cat in categories:
            if cat not in self.knowledge_base:
                continue
                
            for key, entry in self.knowledge_base[cat].items():
                # Check for match in key
                if query in key.lower():
                    results.append({
                        "category": cat,
                        "key": key,
                        "data": entry,
                        "match_type": "key"
                    })
                    continue
                
                # Check for match in name field if it exists
                if "name" in entry and query in entry["name"].lower():
                    results.append({
                        "category": cat,
                        "key": key,
                        "data": entry,
                        "match_type": "name"
                    })
                    continue
                
                # Check for match in description if it exists
                if "description" in entry and query in entry["description"].lower():
                    results.append({
                        "category": cat,
                        "key": key,
                        "data": entry,
                        "match_type": "description"
                    })
                    continue
        
        return results
    
    def _save_knowledge_base(self) -> bool:
        """
        Save the knowledge base to disk.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create directories if they don't exist
            kb_dir = Path(f"game_data/{self.game_id}/knowledge_base")
            kb_dir.mkdir(parents=True, exist_ok=True)
            
            # Save each category to a separate file
            for category, entries in self.knowledge_base.items():
                if entries:  # Only save non-empty categories
                    file_path = kb_dir / f"{category}.json"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(entries, f, indent=2)
            
            logger.info("Saved knowledge base to disk")
            return True
        
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
            return False
    
    def _load_knowledge_base(self) -> bool:
        """
        Load the knowledge base from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Check if knowledge base directory exists
            kb_dir = Path(f"game_data/{self.game_id}/knowledge_base")
            if not kb_dir.exists():
                logger.info(f"No knowledge base found for game {self.game_id}")
                return False
            
            # Load each category from its file
            for category in self.knowledge_base.keys():
                file_path = kb_dir / f"{category}.json"
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.knowledge_base[category] = json.load(f)
            
            logger.info("Loaded knowledge base from disk")
            return True
        
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            return False
    
    def update_multimodal_settings(self, settings: Dict[str, bool]) -> None:
        """
        Update multimodal interaction settings.
        
        Args:
            settings: Dictionary of settings to update
        """
        for key, value in settings.items():
            if key in self.multimodal_settings:
                self.multimodal_settings[key] = value
                logger.info(f"Updated multimodal setting {key}: {value}")
    
    def to_context_dict(self) -> Dict[str, Any]:
        """
        Convert the game state to a dictionary for use in AI context.
        
        Returns:
            Dictionary representation of the game state.
        """
        context = {
            "game_id": self.game_id,
            "system": {
                "id": self.system_id,
                "name": self.system.name if self.system else self.system_id,
                "version": self.system.version if self.system else "unknown"
            },
            "current_location": self.current_location,
            "game_time": self.game_time,
            "environment": self.environment,
            "game_mode": self.game_mode,
            "session_number": self.session_number,
            "active_characters": self.active_characters,
            "active_npcs": list(self.active_npcs),
            "active_quests": self.active_quests,
            "discovered_locations": list(self.discovered_locations),
            "recent_events": self.get_recent_events(count=5),
            "multimodal_settings": self.multimodal_settings
        }
        
        # Include the most recent session summary if available
        if self.session_summaries:
            context["latest_summary"] = self.session_summaries[-1]
        
        return context
    
    def save_to_file(self, file_path: Optional[str] = None) -> str:
        """
        Save the game state to a file.
        
        Args:
            file_path: Path to save the game state. If None, a default path is used.
            
        Returns:
            Path to the saved file.
        """
        if file_path is None:
            # Create a default path using the game ID
            saves_dir = Path("saves")
            saves_dir.mkdir(exist_ok=True)
            
            file_path = str(saves_dir / f"{self.game_id}.json")
        
        # Convert the game state to a serializable dictionary
        state_dict = {
            "game_id": self.game_id,
            "system_id": self.system_id,
            "current_location": self.current_location,
            "active_characters": self.active_characters,
            "active_npcs": list(self.active_npcs),
            "active_quests": self.active_quests,
            "discovered_locations": list(self.discovered_locations),
            "game_time": self.game_time,
            "environment": self.environment,
            "event_history": self.event_history,
            "game_mode": self.game_mode,
            "session_number": self.session_number,
            "session_start_time": self.session_start_time,
            "session_summaries": self.session_summaries,
            "multimodal_settings": self.multimodal_settings
        }
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(state_dict, f, indent=2)
        
        logger.info(f"Saved game state to {file_path}")
        
        # Also save the knowledge base
        self._save_knowledge_base()
        
        return file_path
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load the game state from a file.
        
        Args:
            file_path: Path to the saved game state file.
            
        Returns:
            True if the game state was loaded successfully, False otherwise.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                state_dict = json.load(f)
            
            # Load basic properties
            self.game_id = state_dict["game_id"]
            
            # Load system
            system_id = state_dict.get("system_id", "dnd5e")
            self.change_system(system_id)
            
            self.current_location = state_dict["current_location"]
            self.active_characters = state_dict["active_characters"]
            self.active_npcs = set(state_dict["active_npcs"])
            self.active_quests = state_dict["active_quests"]
            self.discovered_locations = set(state_dict["discovered_locations"])
            self.game_time = state_dict["game_time"]
            self.environment = state_dict["environment"]
            self.event_history = state_dict["event_history"]
            self.game_mode = state_dict["game_mode"]
            self.session_number = state_dict["session_number"]
            self.session_start_time = state_dict["session_start_time"]
            
            # Load session summaries if available
            self.session_summaries = state_dict.get("session_summaries", [])
            
            # Load multimodal settings if available
            self.multimodal_settings.update(state_dict.get("multimodal_settings", {}))
            
            # Load knowledge base
            self._load_knowledge_base()
            
            logger.info(f"Loaded game state from {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading game state: {e}")
            return False
