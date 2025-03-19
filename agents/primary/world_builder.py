"""
World Builder Agent Implementation

This module implements the World Builder Agent, which is responsible for maintaining the physical,
geographical, and environmental aspects of the game world. It creates immersive, consistent
settings with rich sensory detail and tracks how locations change over time.
"""

import logging
from typing import Dict, Any, Optional, List, Union

from ..base_agent import BaseAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorldBuilderAgent(BaseAgent):
    """
    The World Builder Agent manages physical aspects of the game world.
    
    It generates detailed descriptions of locations, maintains geographical consistency,
    tracks environmental conditions, and ensures physical world coherence.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the World Builder Agent.
        
        Args:
            config: Optional configuration dictionary for the agent.
        """
        super().__init__("World Builder", config)
        
        # Store world locations and their descriptions
        self.locations = {}
        
        # Track current environmental conditions
        self.current_environment = {
            "weather": "clear",
            "time_of_day": "noon",
            "season": "summer",
            "ambient_noise": "typical for setting",
            "lighting": "natural daylight",
            "temperature": "comfortable",
        }
        
        logger.info("World Builder Agent initialized")
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a query related to world building and generate a response.
        
        Args:
            query: The query text from the Controller Agent.
            context: Optional dictionary containing relevant context information.
            
        Returns:
            A string response with location descriptions or environmental details.
        """
        context = context or {}
        
        # Extract relevant information from the context
        current_location = context.get("current_location", "")
        query_type = context.get("query_type", "describe_location")
        sensory_focus = context.get("sensory_focus", [])  # e.g., ["visual", "auditory", "olfactory"]
        detail_level = context.get("detail_level", "standard")  # "brief", "standard", "detailed"
        
        # Update environmental conditions if provided
        if "environment" in context:
            self._update_environment(context["environment"])
        
        # Determine the response type based on the query type
        if query_type == "describe_location":
            return self._describe_location(current_location, sensory_focus, detail_level)
        elif query_type == "describe_environment":
            return self._describe_environment(current_location)
        elif query_type == "location_transition":
            destination = context.get("destination", "")
            return self._describe_transition(current_location, destination)
        elif query_type == "create_location":
            location_name = context.get("location_name", "")
            location_type = context.get("location_type", "")
            location_details = context.get("location_details", {})
            return self._create_location(location_name, location_type, location_details)
        else:
            # Default to processing as a free-form query
            return self._generate_world_response(query, context)
    
    def _describe_location(self, location_name: str, sensory_focus: List[str] = None, detail_level: str = "standard") -> str:
        """
        Generate a description of a location.
        
        Args:
            location_name: The name of the location to describe.
            sensory_focus: Optional list of sensory details to emphasize.
            detail_level: The level of detail to include.
            
        Returns:
            A description of the location.
        """
        sensory_focus = sensory_focus or ["visual"]
        
        # Check if we have this location stored
        if location_name in self.locations:
            location_data = self.locations[location_name]
            
            # Start building the prompt for the LLM
            prompt = f"Please describe the location '{location_name}' with the following characteristics:\n\n"
            
            # Add location details to the prompt
            for key, value in location_data.items():
                prompt += f"{key.upper()}: {value}\n"
            
            # Add sensory focus and detail level instructions
            prompt += f"\nSENSORY FOCUS: {', '.join(sensory_focus)}\n"
            prompt += f"DETAIL LEVEL: {detail_level}\n"
            prompt += f"CURRENT ENVIRONMENT: {self._environment_to_string()}\n\n"
            prompt += "Generate a rich, immersive description of this location that brings it to life."
            
            # Generate the description
            return self._generate_llm_response(prompt)
        else:
            # We don't have this location, so generate a new one on the fly
            logger.info(f"Location '{location_name}' not found, generating on the fly")
            return self._create_location(location_name, "", {})
    
    def _describe_environment(self, location_name: str) -> str:
        """
        Generate a description of the current environmental conditions.
        
        Args:
            location_name: The name of the current location.
            
        Returns:
            A description of the current environmental conditions.
        """
        prompt = "Please describe the current environmental conditions:\n\n"
        prompt += f"LOCATION: {location_name}\n"
        prompt += f"ENVIRONMENT: {self._environment_to_string()}\n\n"
        prompt += "Focus on how these conditions affect the atmosphere, visibility, comfort, and mood of the location."
        
        return self._generate_llm_response(prompt)
    
    def _describe_transition(self, origin: str, destination: str) -> str:
        """
        Generate a description of the transition between two locations.
        
        Args:
            origin: The name of the starting location.
            destination: The name of the destination location.
            
        Returns:
            A description of the transition between locations.
        """
        prompt = "Please describe the transition between these locations:\n\n"
        prompt += f"ORIGIN: {origin}\n"
        prompt += f"DESTINATION: {destination}\n"
        prompt += f"ENVIRONMENT: {self._environment_to_string()}\n\n"
        prompt += "Describe the journey, what the characters see along the way, and how the environment changes."
        
        return self._generate_llm_response(prompt)
    
    def _create_location(self, location_name: str, location_type: str, location_details: Dict[str, Any]) -> str:
        """
        Create a new location and generate its description.
        
        Args:
            location_name: The name of the location to create.
            location_type: The type of location (e.g., "city", "dungeon", "forest").
            location_details: Additional details about the location.
            
        Returns:
            A description of the newly created location.
        """
        # Build a prompt to generate location details
        prompt = f"Please create a detailed description for a new location named '{location_name}'.\n\n"
        
        if location_type:
            prompt += f"LOCATION TYPE: {location_type}\n"
        
        if location_details:
            for key, value in location_details.items():
                prompt += f"{key.upper()}: {value}\n"
        
        prompt += f"ENVIRONMENT: {self._environment_to_string()}\n\n"
        prompt += "Generate a comprehensive description including physical characteristics, notable features, and atmosphere."
        
        # Generate the location description
        description = self._generate_llm_response(prompt)
        
        # Store the location for future reference
        combined_details = {
            "type": location_type,
            "description": description,
            **location_details
        }
        self.locations[location_name] = combined_details
        
        logger.info(f"Created new location: {location_name}")
        
        return description
    
    def _update_environment(self, environment_updates: Dict[str, str]) -> None:
        """
        Update the current environmental conditions.
        
        Args:
            environment_updates: Dictionary of environmental aspects to update.
        """
        for key, value in environment_updates.items():
            if key in self.current_environment:
                self.current_environment[key] = value
                logger.info(f"Updated environment {key}: {value}")
    
    def _environment_to_string(self) -> str:
        """
        Convert the current environment to a string representation.
        
        Returns:
            A string describing the current environment.
        """
        parts = []
        for key, value in self.current_environment.items():
            parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return ", ".join(parts)
    
    def _generate_world_response(self, query: str, context: Dict[str, Any]) -> str:
        """
        Generate a response to a free-form world-related query.
        
        Args:
            query: The query text.
            context: Dictionary containing context information.
            
        Returns:
            A response to the query.
        """
        # Construct a prompt with the query and relevant context
        prompt = f"Please respond to this world-building query: {query}\n\n"
        
        if "current_location" in context:
            prompt += f"CURRENT LOCATION: {context['current_location']}\n"
        
        prompt += f"CURRENT ENVIRONMENT: {self._environment_to_string()}\n\n"
        
        # If we have additional context, include it
        if context:
            prompt += "ADDITIONAL CONTEXT:\n"
            for key, value in context.items():
                if key not in ["current_location", "query_type", "sensory_focus", "detail_level"]:
                    prompt += f"{key.upper()}: {value}\n"
        
        return self._generate_llm_response(prompt)
    
    def get_all_locations(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a dictionary of all known locations.
        
        Returns:
            A dictionary mapping location names to their details.
        """
        return self.locations
    
    def get_current_environment(self) -> Dict[str, str]:
        """
        Get the current environmental conditions.
        
        Returns:
            A dictionary of current environmental conditions.
        """
        return self.current_environment
