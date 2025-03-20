"""
World Builder Agent Implementation

This module implements the World Builder Agent, which is responsible for maintaining the physical,
geographical, and environmental aspects of the game world. It creates immersive, consistent
settings with rich sensory detail and tracks how locations change over time.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import json
import sys
import os
import random
import asyncio

from ..base_agent import BaseAgent
from core.dna_generator import WorldDNA, WorldDNAGenerator

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
        
        # World DNA for consistent world generation
        self.world_dna = None
        
        # World traits derived from DNA
        self.world_traits = {}
        
        # Path for storing world DNA
        self.dna_storage_path = Path("storage/world_dna")
        self.dna_storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("World Builder Agent initialized")
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
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
            return await self._describe_location(current_location, sensory_focus, detail_level)
        elif query_type == "describe_environment":
            return await self._describe_environment(current_location)
        elif query_type == "location_transition":
            destination = context.get("destination", "")
            return await self._describe_transition(current_location, destination)
        elif query_type == "create_location":
            location_name = context.get("location_name", "")
            location_type = context.get("location_type", "")
            location_details = context.get("location_details", {})
            return await self._create_location(location_name, location_type, location_details)
        elif query_type == "generate_world_with_dna":
            world_name = context.get("world_name", "")
            dna_string = context.get("dna_string", None)
            return await self.generate_world_with_dna(world_name, dna_string)
        elif query_type == "generate_random_world":
            world_name = context.get("world_name", "")
            return await self.generate_random_world(world_name)
        elif query_type == "generate_advanced_world":
            world_name = context.get("world_name", "")
            bias = context.get("bias", None)
            return await self.generate_advanced_world(world_name, bias)
        elif query_type == "evolve_world":
            world_name = context.get("world_name", "")
            time_periods = context.get("time_periods", 1)
            focus_traits = context.get("focus_traits", None)
            return await self.evolve_world(world_name, time_periods, focus_traits)
        else:
            # Default to processing as a free-form query
            return await self._generate_world_response(query, context)
    
    async def _describe_location(self, location_name: str, sensory_focus: List[str] = None, detail_level: str = "standard") -> str:
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
            return await self._generate_llm_response(prompt)
        else:
            # We don't have this location, so generate a new one on the fly
            logger.info(f"Location '{location_name}' not found, generating on the fly")
            return await self._create_location(location_name, "", {})
    
    async def _describe_environment(self, location_name: str) -> str:
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
        
        return await self._generate_llm_response(prompt)
    
    async def _describe_transition(self, origin: str, destination: str) -> str:
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
        
        return await self._generate_llm_response(prompt)
    
    async def _create_location(self, location_name: str, location_type: str, location_details: Dict[str, Any]) -> str:
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
        description = await self._generate_llm_response(prompt)
        
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
    
    async def _generate_world_response(self, query: str, context: Dict[str, Any]) -> str:
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
        
        return await self._generate_llm_response(prompt)
    
    async def generate_world_with_dna(self, world_name: str, dna_string: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a complete world using DNA-based technology.
        
        This method either uses a provided DNA string or generates a new random one,
        then uses it to create a consistent world with all necessary components.
        
        Args:
            world_name: The name of the world to generate
            dna_string: Optional DNA string. If not provided, a new random one is generated.
            
        Returns:
            Dictionary containing the generated world information.
        """
        logger.info(f"Generating world '{world_name}' with DNA")
        
        # Create or load WorldDNA
        if dna_string:
            self.world_dna = WorldDNA(dna_string)
        else:
            self.world_dna = WorldDNA()  # Generate random DNA
        
        # Store DNA traits for easier access
        self.world_traits = self.world_dna.traits
        
        # Generate world description based on DNA
        world_prompt = self.world_dna.to_prompt()
        
        # Save DNA for future reference
        dna_file = self.dna_storage_path / f"{world_name.lower().replace(' ', '_')}_dna.json"
        self.world_dna.save(dna_file)
        
        # Parse DNA traits into world components
        world_info = {
            "name": world_name,
            "dna": self.world_dna.dna_string,
            "description": await self._expand_world_description(world_prompt),
            "geography": {
                "terrain": self.world_traits["terrain"],
                "climate": self.world_traits["climate"],
                "resources": self.world_traits["resources"]
            },
            "society": {
                "government": self.world_traits["government"],
                "stability": self.world_traits["stability"],
                "factions": self.world_traits["factions"]
            },
            "technology": {
                "level": self.world_traits["tech_level"],
                "magic": self.world_traits["magic"],
                "supernatural": self.world_traits["supernatural"]
            },
            "danger": {
                "conflict": self.world_traits["conflict"],
                "threats": self.world_traits["threats"],
                "level": self.world_traits["danger_level"]
            },
            "culture": {
                "type": self.world_traits["culture_type"],
                "values": self.world_traits["values"],
                "openness": self.world_traits["openness"]
            }
        }
        
        # Add special features if present
        if self.world_traits["special_features"] != "none":
            world_info["special_features"] = self.world_traits["special_features"]
        
        # Generate some initial locations based on the world traits
        world_info["locations"] = await self._generate_initial_locations(world_name)
        
        # Update the agent's internal state
        self.locations.update(world_info["locations"])
        
        return world_info
    
    async def _expand_world_description(self, prompt: str) -> str:
        """
        Expand a basic world prompt into a detailed description.
        
        In a real implementation, this would use an LLM to generate more descriptive text.
        For now, we'll use a simple template-based approach.
        
        Args:
            prompt: The basic world prompt derived from DNA.
            
        Returns:
            A more detailed world description.
        """
        # In a real implementation, this would call the LLM with the prompt
        # For now, we'll just return the prompt as is with an introductory line
        return f"# World Description\n\n{prompt}\n\nThis world awaits adventurers to explore its depths and uncover its secrets."
    
    async def _generate_initial_locations(self, world_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Generate initial locations based on world traits.
        
        Args:
            world_name: The name of the world.
            
        Returns:
            Dictionary of location information.
        """
        locations = {}
        
        # Generate a capital city based on government type
        capital_name = f"Capital of {world_name}"
        
        government = self.world_traits["government"]
        if government == "monarchy":
            capital_name = "Royal City"
        elif government == "democracy":
            capital_name = "Parliament City"
        elif government == "empire":
            capital_name = "Imperial Capital"
        elif government == "theocracy":
            capital_name = "Divine Seat"
        elif government == "feudal":
            capital_name = "Lord's Keep"
        elif government == "tribal":
            capital_name = "Ancestral Gathering"
        elif government == "republic":
            capital_name = "Republic Plaza"
        
        locations[capital_name] = {
            "type": "settlement",
            "description": f"The {capital_name} is the seat of {self.world_traits['government']} power. " +
                          f"It reflects the {self.world_traits['values']} values of the culture.",
            "notable_features": [],
            "connected_to": []
        }
        
        # Generate a location based on terrain
        terrain_location_name = f"{self.world_traits['terrain'].capitalize()} Region"
        locations[terrain_location_name] = {
            "type": "wilderness",
            "description": f"A vast expanse of {self.world_traits['terrain']} terrain with {self.world_traits['climate']} climate.",
            "notable_features": [],
            "connected_to": [capital_name]
        }
        
        # Connect capital to terrain location
        locations[capital_name]["connected_to"].append(terrain_location_name)
        
        # Add a special location based on special_features if present
        if self.world_traits["special_features"] != "none":
            special_name = f"The {self.world_traits['special_features'].replace('_', ' ').title()}"
            locations[special_name] = {
                "type": "special",
                "description": f"A location known for its {self.world_traits['special_features'].replace('_', ' ')}.",
                "notable_features": [self.world_traits['special_features'].replace('_', ' ')],
                "connected_to": [terrain_location_name]
            }
            
            # Connect terrain location to special location
            locations[terrain_location_name]["connected_to"].append(special_name)
        
        return locations
    
    async def generate_random_world(self, world_name: str) -> Dict[str, Any]:
        """
        Generate a random world with its DNA and description.
        
        Args:
            world_name: The name of the world to generate.
        
        Returns:
            Dictionary containing world details.
        """
        # Generate random world DNA
        world_dna = WorldDNA()
        
        return await self.generate_world_with_dna(world_name, world_dna.dna_string)
    
    async def generate_advanced_world(self, 
                                   world_name: str, 
                                   bias: Optional[Dict[str, tuple]] = None) -> Dict[str, Any]:
        """
        Generate a world using the advanced DNA generator.
        
        Args:
            world_name: The name of the world to generate.
            bias: Optional dictionary of trait biases in the format:
                  {trait_name: (prevalence_bias, intensity_bias)}
                  
        Returns:
            Dictionary containing world details with the advanced DNA.
        """
        # Generate advanced world DNA
        generator = WorldDNAGenerator()
        advanced_dna = generator.generate_dna(bias)
        
        # Also get simplified version for backward compatibility
        world_dna = WorldDNA.from_advanced_dna(advanced_dna)
        
        # Generate the world using the simplified DNA
        world_data = await self.generate_world_with_dna(world_name, world_dna.dna_string)
        
        # Parse advanced DNA for additional information
        version = "1.0"
        thresholds = []
        evolution = {}
        
        if advanced_dna:
            # Extract version
            if advanced_dna.startswith("V"):
                version_part = advanced_dna.split(" ")[0]
                version = version_part[1:]
            
            # Extract thresholds
            if "THRESH{" in advanced_dna:
                thresh_part = advanced_dna.split("THRESH{")[1].split("}")[0]
                thresholds = thresh_part.split(";")
            
            # Extract evolution (simplified for API response)
            if "EVO{" in advanced_dna:
                evo_part = advanced_dna.split("EVO{")[1].split("}")[0]
                for evo_item in evo_part.split(";"):
                    if ":" in evo_item and "[" in evo_item and "]" in evo_item:
                        trait, pattern_values = evo_item.split(":", 1)
                        pattern = pattern_values.split("[")[0]
                        values = pattern_values.split("[")[1].split("]")[0]
                        evolution[trait] = {
                            "pattern": pattern,
                            "values": values.split(",")
                        }
        
        # Store advanced DNA for future retrieval
        storage_dir = Path("storage/world_dna/advanced")
        
        advanced_data = {
            "name": world_name,
            "dna_string": advanced_dna,
            "version": version,
            "thresholds": thresholds,
            "evolution": evolution,
            "traits": world_data.get("dna_traits", {})
        }
        
        with open(storage_dir / f"{world_name.lower().replace(' ', '_')}_advanced_dna.json", 'w') as f:
            json.dump(advanced_data, f, indent=2)
        
        # Enhance the world data with advanced information
        world_data["advanced_dna"] = advanced_dna
        world_data["dna_version"] = version
        world_data["dna_thresholds"] = thresholds
        world_data["dna_evolution"] = evolution
        
        return world_data
    
    async def evolve_world(self, 
                         world_name: str, 
                         time_periods: int = 1,
                         focus_traits: List[str] = None) -> Dict[str, Any]:
        """
        Evolve a world through time periods based on its DNA evolution patterns.
        
        Args:
            world_name: Name of the world to evolve.
            time_periods: Number of time periods to evolve (default 1).
            focus_traits: Optional list of traits to focus evolution on.
            
        Returns:
            The evolved world data.
        """
        # Check if advanced DNA exists
        storage_path = Path(f"storage/world_dna/advanced/{world_name.lower().replace(' ', '_')}_advanced_dna.json")
        
        if not storage_path.exists():
            raise ValueError(f"Advanced DNA for world '{world_name}' not found")
        
        # Load existing advanced DNA
        with open(storage_path, 'r') as f:
            data = json.load(f)
        
        original_dna = data.get("dna_string", "")
        
        # Parse the DNA to extract evolution information
        evolution_info = {}
        if "EVO{" in original_dna:
            evo_part = original_dna.split("EVO{")[1].split("}")[0]
            for evo_item in evo_part.split(";"):
                if ":" in evo_item and "[" in evo_item and "]" in evo_item:
                    trait, pattern_values = evo_item.split(":", 1)
                    pattern = pattern_values.split("[")[0]
                    values = pattern_values.split("[")[1].split("]")[0]
                    evolution_info[trait] = {
                        "pattern": pattern,
                        "values": values.split(",")
                    }
        
        # Extract traits section
        traits_section = ""
        if "TRAITS{" in original_dna:
            traits_section = original_dna.split("TRAITS{")[1].split("}")[0]
        
        # Create a modified traits section with evolved values
        if traits_section:
            traits_parts = traits_section.split(";")
            evolved_traits_parts = []
            
            for trait_part in traits_parts:
                if ":" in trait_part:
                    trait_name, value = trait_part.split(":")
                    
                    # Check if this trait has evolution info
                    if trait_name in evolution_info:
                        # Get the evolved value based on time periods
                        evo_data = evolution_info[trait_name]
                        values = evo_data["values"]
                        
                        # Calculate the index of the evolved value
                        # PAST, PRESENT, NEAR, FAR
                        # Start at PRESENT (index 1) and move forward
                        target_index = 1 + time_periods  # PRESENT + time_periods
                        
                        if target_index < len(values):
                            evolved_value = values[target_index]
                            evolved_traits_parts.append(f"{trait_name}:{evolved_value}")
                        else:
                            # If we're evolving beyond what's defined, use the last value
                            evolved_value = values[-1]
                            evolved_traits_parts.append(f"{trait_name}:{evolved_value}")
                    elif focus_traits and trait_name in focus_traits:
                        # Special handling for focused traits without defined evolution
                        # For simplicity, we'll just increase their prevalence
                        if len(value) >= 2:
                            prevalence = int(value[0]) if value[0].isdigit() else 5
                            intensity = int(value[1]) if value[1].isdigit() else 3
                            
                            # Increase prevalence (cap at 9)
                            prevalence = min(9, prevalence + 1)
                            evolved_traits_parts.append(f"{trait_name}:{prevalence}{intensity}")
                        else:
                            evolved_traits_parts.append(trait_part)
                    else:
                        # Keep unchanged for non-evolving traits
                        evolved_traits_parts.append(trait_part)
            
            # Create the new traits section
            evolved_traits_section = ";".join(evolved_traits_parts)
            
            # Replace the traits section in the DNA
            evolved_dna = original_dna.replace(f"TRAITS{{{traits_section}}}", f"TRAITS{{{evolved_traits_section}}}")
            
            # Create a world based on the evolved DNA
            world_dna = WorldDNA.from_advanced_dna(evolved_dna)
            
            # Generate a world description
            evolved_world_name = f"{world_name} (Evolved +{time_periods})"
            evolved_world = await self.generate_world_with_dna(evolved_world_name, world_dna.dna_string)
            
            # Store the evolved DNA
            storage_dir = Path("storage/world_dna/advanced")
            evolved_data = {
                "name": evolved_world_name,
                "dna_string": evolved_dna,
                "original_world": world_name,
                "time_periods": time_periods,
                "thresholds": data.get("thresholds", []),
                "evolution": data.get("evolution", {}),
                "traits": evolved_world.get("dna_traits", {}),
                "focus_traits": focus_traits or []
            }
            
            with open(storage_dir / f"{evolved_world_name.lower().replace(' ', '_')}_advanced_dna.json", 'w') as f:
                json.dump(evolved_data, f, indent=2)
            
            # Enhance the evolved world data
            evolved_world["advanced_dna"] = evolved_dna
            evolved_world["original_world"] = world_name
            evolved_world["time_periods"] = time_periods
            evolved_world["focus_traits"] = focus_traits or []
            
            return evolved_world
        else:
            raise ValueError("Could not parse traits from DNA")
    
    def load_world_dna(self, world_name: str) -> bool:
        """
        Load a world DNA from storage.
        
        Args:
            world_name: The name of the world to load DNA for.
            
        Returns:
            True if loaded successfully, False otherwise.
        """
        dna_file = self.dna_storage_path / f"{world_name.lower().replace(' ', '_')}_dna.json"
        
        world_dna = WorldDNA.load(dna_file)
        if world_dna:
            self.world_dna = world_dna
            self.world_traits = world_dna.traits
            logger.info(f"Loaded DNA for world '{world_name}'")
            return True
        
        logger.warning(f"Failed to load DNA for world '{world_name}'")
        return False
    
    def mutate_world_dna(self, mutation_rate: float = 0.2) -> Dict[str, Any]:
        """
        Create a mutation of the current world DNA.
        
        Args:
            mutation_rate: Probability (0-1) of each trait mutating.
            
        Returns:
            Dictionary containing the new DNA and changes made.
        """
        if not self.world_dna:
            logger.warning("No world DNA to mutate, generating a new one")
            self.world_dna = WorldDNA()
            return {"dna": self.world_dna.dna_string, "changes": "New DNA generated"}
        
        # Create a mutation
        old_traits = self.world_dna.traits.copy()
        mutated_dna = self.world_dna.mutate(mutation_rate)
        
        # Track changes
        changes = []
        for component, new_value in mutated_dna.traits.items():
            old_value = old_traits.get(component)
            if new_value != old_value:
                changes.append(f"{component}: {old_value} -> {new_value}")
        
        # Update current DNA
        self.world_dna = mutated_dna
        self.world_traits = mutated_dna.traits
        
        return {
            "dna": self.world_dna.dna_string,
            "changes": changes
        }
    
    def crossover_world_dna(self, other_dna_string: str) -> Dict[str, Any]:
        """
        Create a new world DNA by combining the current DNA with another.
        
        Args:
            other_dna_string: Another DNA string to combine with.
            
        Returns:
            Dictionary containing the new DNA and traits.
        """
        if not self.world_dna:
            logger.warning("No primary world DNA for crossover, generating a new one")
            self.world_dna = WorldDNA()
        
        # Create the other DNA
        other_dna = WorldDNA(other_dna_string)
        
        # Perform crossover
        child_dna = self.world_dna.crossover(other_dna)
        
        # Update current DNA
        self.world_dna = child_dna
        self.world_traits = child_dna.traits
        
        return {
            "dna": self.world_dna.dna_string,
            "traits": self.world_traits
        }
    
    def get_dna_prompt(self) -> str:
        """
        Get the natural language prompt derived from the current DNA.
        
        Returns:
            A textual description of the world based on DNA traits.
        """
        if not self.world_dna:
            logger.warning("No world DNA loaded, generating a new one")
            self.world_dna = WorldDNA()
            self.world_traits = self.world_dna.traits
        
        return self.world_dna.to_prompt()

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
