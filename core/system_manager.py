"""
Game System Manager

This module manages the loading, selection, and integration of different game systems.
It provides a framework for modular game systems that can be loaded dynamically.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GameSystem:
    """
    Represents a game system with its rules, assets, and configuration.
    """
    
    def __init__(self, system_id: str, system_path: Path):
        """
        Initialize a game system.
        
        Args:
            system_id: Unique identifier for the game system
            system_path: Path to the game system directory
        """
        self.system_id = system_id
        self.system_path = system_path
        self.name = system_id  # Default name to ID
        self.version = "1.0.0"  # Default version
        self.description = ""
        self.authors = []
        
        # Load system metadata if available
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load system metadata from the system.json file if it exists."""
        metadata_path = self.system_path / "system.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Update system properties
                self.name = metadata.get("name", self.name)
                self.version = metadata.get("version", self.version)
                self.description = metadata.get("description", self.description)
                self.authors = metadata.get("authors", self.authors)
                
                logger.info(f"Loaded metadata for game system: {self.name} (v{self.version})")
            except Exception as e:
                logger.error(f"Error loading system metadata: {e}")
    
    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific rule from the game system.
        
        Args:
            rule_id: Identifier for the rule
            
        Returns:
            Rule data if found, None otherwise
        """
        rule_path = self.system_path / "rules" / f"{rule_id}.json"
        if rule_path.exists():
            try:
                with open(rule_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading rule {rule_id}: {e}")
        return None
    
    def get_asset(self, asset_path: str) -> Optional[str]:
        """
        Get the path to a system asset.
        
        Args:
            asset_path: Relative path to the asset within the system
            
        Returns:
            Full path to the asset if found, None otherwise
        """
        full_path = self.system_path / "assets" / asset_path
        if full_path.exists():
            return str(full_path)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the game system to a dictionary representation.
        
        Returns:
            Dictionary with system information
        """
        return {
            "id": self.system_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "authors": self.authors,
            "path": str(self.system_path)
        }


class SystemManager:
    """
    Manages game systems, including discovery, loading, and selection.
    """
    
    def __init__(self, systems_dir: Optional[str] = None):
        """
        Initialize the system manager.
        
        Args:
            systems_dir: Directory containing game systems
        """
        # Default systems directory is in the project root
        if systems_dir is None:
            # Get the parent directory of the core module (project root)
            project_root = Path(__file__).parent.parent
            systems_dir = project_root / "systems"
        else:
            systems_dir = Path(systems_dir)
        
        self.systems_dir = systems_dir
        self.available_systems: Dict[str, GameSystem] = {}
        self.active_system: Optional[GameSystem] = None
        
        # Create systems directory if it doesn't exist
        if not self.systems_dir.exists():
            self.systems_dir.mkdir(parents=True)
            logger.info(f"Created systems directory: {self.systems_dir}")
        
        # Discover available systems
        self.discover_systems()
    
    def discover_systems(self) -> None:
        """Scan the systems directory and load available game systems."""
        self.available_systems = {}
        
        if not self.systems_dir.exists():
            logger.warning(f"Systems directory does not exist: {self.systems_dir}")
            return
        
        # Find all subdirectories in the systems directory
        for system_dir in self.systems_dir.iterdir():
            if system_dir.is_dir():
                system_id = system_dir.name
                try:
                    # Create a GameSystem object for this directory
                    game_system = GameSystem(system_id, system_dir)
                    self.available_systems[system_id] = game_system
                    logger.info(f"Discovered game system: {system_id}")
                except Exception as e:
                    logger.error(f"Error loading game system {system_id}: {e}")
        
        logger.info(f"Discovered {len(self.available_systems)} game systems")
    
    def get_available_systems(self) -> List[Dict[str, Any]]:
        """
        Get information about all available game systems.
        
        Returns:
            List of dictionaries with system information
        """
        return [system.to_dict() for system in self.available_systems.values()]
    
    def select_system(self, system_id: str) -> bool:
        """
        Select a game system as the active system.
        
        Args:
            system_id: ID of the system to select
            
        Returns:
            True if the system was selected successfully, False otherwise
        """
        if system_id in self.available_systems:
            self.active_system = self.available_systems[system_id]
            logger.info(f"Selected game system: {system_id}")
            return True
        else:
            logger.warning(f"Game system not found: {system_id}")
            return False
    
    def get_active_system(self) -> Optional[GameSystem]:
        """
        Get the currently active game system.
        
        Returns:
            The active GameSystem object, or None if no system is active
        """
        return self.active_system
    
    def create_system_template(self, system_id: str, name: str, description: str = "", version: str = "1.0.0", authors: List[str] = None) -> bool:
        """
        Create a new game system template with basic structure.
        
        Args:
            system_id: Unique identifier for the new system
            name: Display name for the system
            description: Optional description of the system
            version: System version string
            authors: List of author names
            
        Returns:
            True if the system was created successfully, False otherwise
        """
        # Validate system ID (only allow alphanumeric chars and underscores)
        if not system_id.isalnum() and not all(c.isalnum() or c == '_' for c in system_id):
            logger.error(f"Invalid system ID: {system_id}. Use only alphanumeric characters and underscores.")
            return False
        
        # Check if the system already exists
        system_path = self.systems_dir / system_id
        if system_path.exists():
            logger.error(f"Game system already exists: {system_id}")
            return False
        
        try:
            # Create system directory and subdirectories
            system_path.mkdir(parents=True)
            (system_path / "rules").mkdir()
            (system_path / "assets").mkdir()
            (system_path / "templates").mkdir()
            
            # Create system.json metadata file
            metadata = {
                "name": name,
                "version": version,
                "description": description,
                "authors": authors or [],
                "created": datetime.now().isoformat()
            }
            
            with open(system_path / "system.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Create a basic README
            with open(system_path / "README.md", 'w', encoding='utf-8') as f:
                f.write(f"# {name}\n\n{description}\n\n## Version\n\n{version}\n\n## Authors\n\n")
                for author in (authors or []):
                    f.write(f"- {author}\n")
            
            logger.info(f"Created new game system template: {system_id}")
            
            # Rediscover systems to include the new one
            self.discover_systems()
            return True
            
        except Exception as e:
            logger.error(f"Error creating game system template: {e}")
            return False
