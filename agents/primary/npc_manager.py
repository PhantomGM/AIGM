"""
NPC Manager Agent Implementation

This module implements the NPC Manager Agent, which is responsible for creating and controlling
non-player characters with consistent personalities and motivations. It generates appropriate
dialogue, tracks NPC knowledge and relationships, and determines NPC actions.
"""

import logging
import random
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import json

from ..base_agent import BaseAgent
from core.dna_generator import NPCPersonalityDNA
from core.npc_decoder import NPCPersonalityDecoder

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NPCManagerAgent(BaseAgent):
    """
    The NPC Manager Agent creates and controls non-player characters.
    
    It develops and maintains consistent NPC personalities, generates appropriate dialogue,
    tracks NPC knowledge and relationships, and determines NPC actions based on motivations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the NPC Manager Agent.
        
        Args:
            config: Optional configuration dictionary for the agent.
        """
        super().__init__("NPC Manager", config)
        
        # Store NPC data
        self.npcs = {}
        
        # Track NPC relationships
        self.relationships = {}
        
        logger.info("NPC Manager Agent initialized")
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a query related to NPCs and generate a response.
        
        Args:
            query: The query text from the Controller Agent.
            context: Optional dictionary containing relevant context information.
            
        Returns:
            A string response with NPC dialogue, actions, or information.
        """
        context = context or {}
        
        # Extract relevant information from the context
        query_type = context.get("query_type", "npc_dialogue")
        npc_name = context.get("npc_name", "")
        player_input = context.get("player_input", "")
        current_location = context.get("current_location", "")
        situation = context.get("situation", "")
        
        # Determine the response type based on the query type
        if query_type == "npc_dialogue":
            return await self._generate_npc_dialogue(npc_name, player_input, situation, current_location)
        elif query_type == "npc_action":
            return await self._determine_npc_action(npc_name, situation, current_location)
        elif query_type == "npc_creation":
            npc_type = context.get("npc_type", "")
            npc_role = context.get("npc_role", "")
            initial_traits = context.get("initial_traits", {})
            return await self._create_npc(npc_name, npc_type, npc_role, initial_traits)
        elif query_type == "npc_information":
            return await self._retrieve_npc_information(npc_name)
        else:
            # Default to processing as a free-form query
            return await self._generate_npc_response(query, context)
    
    async def _generate_npc_dialogue(self, npc_name: str, player_input: str, situation: str, location: str) -> str:
        """
        Generate dialogue for an NPC in response to player input.
        
        Args:
            npc_name: The name of the NPC.
            player_input: What the player said or did.
            situation: The current situation or context.
            location: The current location.
            
        Returns:
            Dialogue from the NPC.
        """
        # Check if we know this NPC
        if npc_name not in self.npcs:
            logger.warning(f"NPC {npc_name} not found, creating on the fly")
            await self._create_npc(npc_name, "", "", {})
        
        npc_data = self.npcs[npc_name]
        
        # Build a prompt to generate the NPC's dialogue
        prompt = f"Generate dialogue for {npc_name} in response to a player.\n\n"
        prompt += f"NPC INFORMATION:\n"
        
        # Add NPC traits to the prompt
        for key, value in npc_data.items():
            if key not in ["knowledge", "dialogue_history"]:
                prompt += f"{key.upper()}: {value}\n"
        
        # Add relevant NPC knowledge
        prompt += "\nNPC KNOWLEDGE:\n"
        for topic, knowledge in npc_data.get("knowledge", {}).items():
            prompt += f"- {topic}: {knowledge}\n"
        
        # Add NPC relationships if any
        if npc_name in self.relationships:
            prompt += "\nNPC RELATIONSHIPS:\n"
            for other_npc, relation in self.relationships[npc_name].items():
                prompt += f"- {other_npc}: {relation['type']} (Strength: {relation['strength']})\n"
        
        # Add context information
        prompt += f"\nCURRENT SITUATION: {situation}\n"
        prompt += f"CURRENT LOCATION: {location}\n"
        prompt += f"PLAYER INPUT: {player_input}\n\n"
        
        # Add dialogue history if available
        dialogue_history = npc_data.get("dialogue_history", [])
        if dialogue_history:
            prompt += "RECENT DIALOGUE:\n"
            # Include the last few exchanges
            for exchange in dialogue_history[-3:]:
                prompt += f"Player: {exchange['player']}\n"
                prompt += f"{npc_name}: {exchange['npc']}\n"
            prompt += "\n"
        
        prompt += f"Generate {npc_name}'s response that is consistent with their personality and knowledge."
        
        # Generate the dialogue
        dialogue = await self._generate_llm_response(prompt)
        
        # Update dialogue history
        if "dialogue_history" not in npc_data:
            npc_data["dialogue_history"] = []
        npc_data["dialogue_history"].append({
            "player": player_input,
            "npc": dialogue
        })
        
        return dialogue
    
    async def _determine_npc_action(self, npc_name: str, situation: str, location: str) -> str:
        """
        Determine what action an NPC would take in the current situation.
        
        Args:
            npc_name: The name of the NPC.
            situation: The current situation or context.
            location: The current location.
            
        Returns:
            A description of the NPC's action.
        """
        # Check if we know this NPC
        if npc_name not in self.npcs:
            logger.warning(f"NPC {npc_name} not found, creating on the fly")
            await self._create_npc(npc_name, "", "", {})
        
        npc_data = self.npcs[npc_name]
        
        # Build a prompt to determine the NPC's action
        prompt = f"Determine what action {npc_name} would take in the current situation.\n\n"
        prompt += f"NPC INFORMATION:\n"
        
        # Add NPC traits to the prompt
        for key, value in npc_data.items():
            if key not in ["knowledge", "dialogue_history"]:
                prompt += f"{key.upper()}: {value}\n"
        
        # Add relevant NPC knowledge
        prompt += "\nNPC KNOWLEDGE:\n"
        for topic, knowledge in npc_data.get("knowledge", {}).items():
            prompt += f"- {topic}: {knowledge}\n"
        
        # Add NPC relationships if any
        if npc_name in self.relationships:
            prompt += "\nNPC RELATIONSHIPS:\n"
            for other_npc, relation in self.relationships[npc_name].items():
                prompt += f"- {other_npc}: {relation['type']} (Strength: {relation['strength']})\n"
        
        # Add context information
        prompt += f"\nCURRENT SITUATION: {situation}\n"
        prompt += f"CURRENT LOCATION: {location}\n\n"
        prompt += f"Based on {npc_name}'s personality, motivations, and the current situation, describe what action they would take."
        
        # Generate the action
        return await self._generate_llm_response(prompt)
    
    async def _create_npc(self, npc_name: str, npc_type: str, npc_role: str, initial_traits: Dict[str, Any]) -> str:
        """
        Create a new NPC with a consistent personality.
        
        Args:
            npc_name: The name of the NPC.
            npc_type: The type of NPC (e.g., "vendor", "guard", "villain").
            npc_role: The role of the NPC in the story.
            initial_traits: Initial traits to assign to the NPC.
            
        Returns:
            A description of the newly created NPC.
        """
        # Build a prompt to generate NPC personality and details
        prompt = f"Create a detailed NPC named {npc_name}.\n\n"
        
        if npc_type:
            prompt += f"NPC TYPE: {npc_type}\n"
        
        if npc_role:
            prompt += f"NPC ROLE: {npc_role}\n"
        
        if initial_traits:
            prompt += "INITIAL TRAITS:\n"
            for trait, value in initial_traits.items():
                prompt += f"- {trait}: {value}\n"
        
        prompt += "\nPlease create a complete NPC profile with the following sections:\n"
        prompt += "1. APPEARANCE: Physical description\n"
        prompt += "2. PERSONALITY: Key character traits, virtues, flaws\n"
        prompt += "3. MOTIVATIONS: What drives this character\n"
        prompt += "4. BACKGROUND: Brief history\n"
        prompt += "5. SPEECH PATTERN: How they talk, mannerisms, vocabulary\n"
        prompt += "6. KNOWLEDGE: What special information they possess\n"
        
        # Generate the NPC profile
        npc_profile = await self._generate_llm_response(prompt)
        
        # Parse the profile into structured data
        # This is a simplistic implementation - in reality, you'd want to use
        # more sophisticated parsing or prompt the LLM to return structured data
        npc_data = {
            "name": npc_name,
            "type": npc_type,
            "role": npc_role,
            "profile": npc_profile,
            "knowledge": {},
            "dialogue_history": []
        }
        
        # Extract sections from the profile (simple approach)
        sections = ["APPEARANCE", "PERSONALITY", "MOTIVATIONS", "BACKGROUND", "SPEECH PATTERN", "KNOWLEDGE"]
        current_section = None
        section_content = []
        
        for line in npc_profile.split("\n"):
            for section in sections:
                if section in line.upper():
                    if current_section and section_content:
                        npc_data[current_section.lower()] = "\n".join(section_content)
                        section_content = []
                    current_section = section
                    break
            else:
                if current_section:
                    section_content.append(line)
        
        # Don't forget to add the last section
        if current_section and section_content:
            npc_data[current_section.lower()] = "\n".join(section_content)
        
        # Add any initial traits
        for trait, value in initial_traits.items():
            npc_data[trait] = value
        
        # Store the NPC
        self.npcs[npc_name] = npc_data
        
        logger.info(f"Created new NPC: {npc_name}")
        
        return npc_profile
    
    async def _retrieve_npc_information(self, npc_name: str) -> str:
        """
        Retrieve information about an NPC.
        
        Args:
            npc_name: The name of the NPC.
            
        Returns:
            Information about the NPC, or an error message if the NPC is not found.
        """
        if npc_name in self.npcs:
            npc_data = self.npcs[npc_name]
            
            # Build a formatted information string
            info = f"# Information about {npc_name}\n\n"
            
            # Add basic information
            for key, value in npc_data.items():
                if key not in ["knowledge", "dialogue_history", "profile"]:
                    info += f"## {key.capitalize()}\n{value}\n\n"
            
            # Add the full profile if available
            if "profile" in npc_data:
                info += f"## Profile\n{npc_data['profile']}\n\n"
            
            # Add NPC knowledge
            if "knowledge" in npc_data and npc_data["knowledge"]:
                info += "## Knowledge\n"
                for topic, knowledge in npc_data["knowledge"].items():
                    info += f"- {topic}: {knowledge}\n"
                info += "\n"
            
            # Add relationships
            if npc_name in self.relationships:
                info += "## Relationships\n"
                for other_npc, relation in self.relationships[npc_name].items():
                    info += f"- {other_npc}: {relation['type']} (Strength: {relation['strength']})\n"
                info += "\n"
            
            return info
        else:
            return f"Error: NPC '{npc_name}' not found."
    
    async def _generate_npc_response(self, query: str, context: Dict[str, Any]) -> str:
        """
        Generate a response to a free-form NPC-related query.
        
        Args:
            query: The query text.
            context: Dictionary containing context information.
            
        Returns:
            A response to the query.
        """
        # Construct a prompt with the query and relevant context
        prompt = f"Please respond to this NPC-related query: {query}\n\n"
        
        if "npc_name" in context:
            npc_name = context["npc_name"]
            if npc_name in self.npcs:
                prompt += f"NPC INFORMATION ({npc_name}):\n"
                for key, value in self.npcs[npc_name].items():
                    if key not in ["knowledge", "dialogue_history"]:
                        prompt += f"{key.upper()}: {value}\n"
        
        # If we have additional context, include it
        if context:
            prompt += "\nADDITIONAL CONTEXT:\n"
            for key, value in context.items():
                if key not in ["npc_name", "query_type"]:
                    prompt += f"{key.upper()}: {value}\n"
        
        return await self._generate_llm_response(prompt)
    
    def create_relationship(self, npc1: str, npc2: str, relation_type: str, strength: int = 5) -> bool:
        """
        Create a relationship between two NPCs.
        
        Args:
            npc1: The name of the first NPC.
            npc2: The name of the second NPC.
            relation_type: The type of relationship (e.g., "friend", "enemy", "family").
            strength: The strength of the relationship (1-10).
            
        Returns:
            True if successful, False if either NPC doesn't exist.
        """
        if npc1 not in self.npcs or npc2 not in self.npcs:
            logger.warning(f"Cannot create relationship: one or both NPCs don't exist ({npc1}, {npc2})")
            return False
        
        # Initialize relationship dictionaries if needed
        if npc1 not in self.relationships:
            self.relationships[npc1] = {}
        
        if npc2 not in self.relationships:
            self.relationships[npc2] = {}
        
        # Create bidirectional relationship
        self.relationships[npc1][npc2] = {
            "type": relation_type,
            "strength": strength
        }
        
        # For the reverse relationship, we might want to adjust based on relationship type
        # For simplicity, we'll use the same type and strength here
        self.relationships[npc2][npc1] = {
            "type": relation_type,
            "strength": strength
        }
        
        logger.info(f"Created relationship between {npc1} and {npc2}: {relation_type} (Strength: {strength})")
        return True
    
    def add_npc_knowledge(self, npc_name: str, topic: str, knowledge: str) -> bool:
        """
        Add knowledge to an NPC about a specific topic.
        
        Args:
            npc_name: The name of the NPC.
            topic: The topic of knowledge.
            knowledge: The knowledge content.
            
        Returns:
            True if successful, False if the NPC doesn't exist.
        """
        if npc_name not in self.npcs:
            logger.warning(f"Cannot add knowledge: NPC {npc_name} not found")
            return False
        
        # Initialize knowledge dictionary if needed
        if "knowledge" not in self.npcs[npc_name]:
            self.npcs[npc_name]["knowledge"] = {}
        
        # Add or update knowledge
        self.npcs[npc_name]["knowledge"][topic] = knowledge
        
        logger.info(f"Added knowledge to {npc_name} about {topic}")
        return True
    
    def get_all_npcs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a dictionary of all NPCs.
        
        Returns:
            A dictionary mapping NPC names to their data.
        """
        return self.npcs
    
    def get_npc_relationships(self, npc_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all relationships for a specific NPC.
        
        Args:
            npc_name: The name of the NPC.
            
        Returns:
            A dictionary of relationships, or an empty dict if the NPC doesn't exist or has no relationships.
        """
        return self.relationships.get(npc_name, {})
    
    async def generate_npc_description_with_dna(
        self, 
        npc_name: str, 
        race: str = "human", 
        gender: Optional[str] = None, 
        npc_dna: Optional[NPCPersonalityDNA] = None
    ) -> str:
        """
        Generate a detailed NPC description using DNA technology for consistent personality creation.
        
        Args:
            npc_name: The name of the NPC.
            race: The race of the NPC (human, elf, dwarf, etc).
            gender: Optional gender specification.
            npc_dna: Optional NPCPersonalityDNA object. If not provided, a random one is generated.
            
        Returns:
            A detailed description of the NPC.
        """
        # Create or use provided DNA
        if not npc_dna:
            npc_dna = NPCPersonalityDNA()
        
        # Get the personality traits from the DNA
        personality_traits = npc_dna.traits
        
        # Use the advanced personality decoder to create a rich prompt
        decoder = NPCPersonalityDecoder()
        additional_context = f"This character is a {race}"
        if gender:
            additional_context += f" {gender}"
        additional_context += f" named {npc_name}."
        
        # Decode the DNA with context
        detailed_prompt = decoder.decode_personality(npc_dna.dna_string, additional_context)
        
        # Save the prompt for reference
        decoder.save_npc_description(f"{npc_name}_prompt", detailed_prompt)
        
        # Generate the description using the LLM
        description = await self._generate_llm_response(detailed_prompt)
        
        # Store the NPC in our system with their DNA info
        if npc_name not in self.npcs:
            self.npcs[npc_name] = {}
        
        self.npcs[npc_name].update({
            "name": npc_name,
            "race": race,
            "gender": gender or "unknown",
            "description": description,
            "dna": npc_dna.dna_string,
            "dna_traits": personality_traits,
            "prompt": detailed_prompt
        })
        
        # Add knowledge base for this NPC
        if "knowledge" not in self.npcs[npc_name]:
            self.npcs[npc_name]["knowledge"] = {}
        
        logger.info(f"Generated DNA-based NPC with advanced decoder: {npc_name}")
        return description
    
    def save_npc_dna(self, npc_name: str, directory: Union[str, Path]) -> bool:
        """
        Save an NPC's DNA to a file.
        
        Args:
            npc_name: The name of the NPC.
            directory: Directory to save the DNA file in.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            if npc_name not in self.npcs or "dna" not in self.npcs[npc_name]:
                logger.warning(f"NPC {npc_name} not found or has no DNA")
                return False
            
            # Create DNA object from stored string
            npc_dna = NPCPersonalityDNA(self.npcs[npc_name]["dna"])
            
            # Save to file
            directory = Path(directory)
            directory.mkdir(parents=True, exist_ok=True)
            
            # Create a safe filename
            safe_name = npc_name.replace(" ", "_").lower()
            filepath = directory / f"{safe_name}.dna.json"
            
            result = npc_dna.save(filepath)
            return result
        
        except Exception as e:
            logger.error(f"Error saving NPC DNA: {e}")
            return False
    
    async def load_npc_dna(self, filepath: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Load an NPC's DNA from a file.
        
        Args:
            filepath: Path to the DNA file.
            
        Returns:
            Dictionary with NPC data if successful, None otherwise.
        """
        try:
            # Load DNA from file
            npc_dna = NPCPersonalityDNA.load(filepath)
            if not npc_dna:
                return None
            
            # Get filename to extract NPC name
            filepath = Path(filepath)
            npc_name = filepath.stem.replace(".dna", "").replace("_", " ").title()
            
            # Load or create NPC data
            if npc_name not in self.npcs:
                self.npcs[npc_name] = {}
            
            # Update with DNA info
            self.npcs[npc_name].update({
                "name": npc_name,
                "dna": npc_dna.dna_string,
                "dna_traits": npc_dna.traits,
            })
            
            logger.info(f"Loaded DNA for NPC: {npc_name}")
            return self.npcs[npc_name]
        
        except Exception as e:
            logger.error(f"Error loading NPC DNA: {e}")
            return None
    
    async def generate_npcs_for_location(self, location_name: str, count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate NPCs that would typically be found in a specific location.
        
        Args:
            location_name: The name of the location to generate NPCs for.
            count: The number of NPCs to generate.
            
        Returns:
            A list of NPC data dictionaries.
        """
        logger.info(f"Generating {count} NPCs for location: {location_name}")
        
        # Ask the LLM what kinds of NPCs would be appropriate for this location
        prompt = f"What types of characters would typically be found in a location called '{location_name}'? " \
                f"For each character, provide a name, race, and gender. Provide {count} characters."
                
        response = await self._generate_llm_response(prompt)
        
        # Parse LLM response to extract NPC suggestions
        # Since the response format may vary, we'll extract what we can
        npcs = []
        
        # Simple parsing of response to extract potential NPCs
        lines = response.split('\n')
        
        # Extract name, race, and gender information
        for line in lines:
            if not line.strip():
                continue
                
            # Look for character info
            if ':' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    details = parts[1].strip()
                    
                    # Extract race and gender
                    race = "human"  # default
                    gender = None
                    
                    if "dwarf" in details.lower():
                        race = "dwarf"
                    elif "elf" in details.lower():
                        race = "elf"
                    elif "gnome" in details.lower():
                        race = "gnome"
                    elif "halfling" in details.lower():
                        race = "halfling"
                    elif "orc" in details.lower():
                        race = "orc"
                    
                    if "male" in details.lower():
                        gender = "male"
                    elif "female" in details.lower():
                        gender = "female"
                    
                    # Generate NPC DNA and description
                    npc_dna = NPCPersonalityDNA()
                    description = await self.generate_npc_description_with_dna(name, race, gender, npc_dna)
                    
                    # Add relationship to the location
                    self.create_relationship(name, "location", location_name, "frequents", 0.8)
                    
                    npcs.append(self.npcs[name])
                    
                    # Limit to the requested count
                    if len(npcs) >= count:
                        break
        
        logger.info(f"Generated {len(npcs)} NPCs for location: {location_name}")
        return npcs
    
    async def merge_personality_with_dna(self, npc_name: str, personality_text: str) -> Optional[str]:
        """
        Merge a text description of a personality with an NPC's DNA.
        
        Args:
            npc_name: The name of the NPC.
            personality_text: Text description of personality traits to incorporate.
            
        Returns:
            Updated NPC description if successful, None otherwise.
        """
        if npc_name not in self.npcs:
            logger.warning(f"NPC {npc_name} not found")
            return None
            
        npc_data = self.npcs[npc_name]
        
        # If the NPC has DNA, use it as a base
        if "dna" in npc_data:
            npc_dna = NPCPersonalityDNA(npc_data["dna"])
            dna_prompt = npc_dna.to_prompt()
            
            # Build a prompt to merge the personality descriptions
            prompt = f"Merge these two personality descriptions for {npc_name}:\n\n"
            prompt += f"ORIGINAL DNA PERSONALITY:\n{dna_prompt}\n\n"
            prompt += f"NEW PERSONALITY INFORMATION:\n{personality_text}\n\n"
            prompt += "Create a comprehensive, coherent description that incorporates all compatible aspects "
            prompt += "of both descriptions, resolving any contradictions in a realistic way. "
            prompt += "The result should feel like a single, unified character."
            
            # Generate the merged description
            merged_description = await self._generate_llm_response(prompt)
            
            # Update the NPC data with the merged description
            npc_data["description"] = merged_description
            
            return merged_description
        else:
            # If there's no DNA, just use the personality text
            npc_data["description"] = personality_text
            return personality_text
    
    async def evolve_npc_personality(self, npc_name: str, events: List[str], intensity: float = 0.2) -> Dict[str, Any]:
        """
        Evolve an NPC's personality based on events they've experienced.
        
        Args:
            npc_name: The name of the NPC.
            events: List of significant events the NPC has experienced.
            intensity: How strongly the events affect personality (0.0-1.0).
            
        Returns:
            Dictionary with information about the personality evolution.
        """
        if npc_name not in self.npcs:
            logger.warning(f"NPC {npc_name} not found")
            return {"error": f"NPC {npc_name} not found"}
            
        npc_data = self.npcs[npc_name]
        
        # If the NPC has DNA, use it for evolution
        if "dna" in npc_data:
            # Create DNA object from stored string
            original_dna = NPCPersonalityDNA(npc_data["dna"])
            
            # Build a prompt to determine which traits should change
            prompt = f"The character {npc_name} has experienced these events:\n"
            for event in events:
                prompt += f"- {event}\n"
            
            prompt += f"\nTheir current personality is:\n{original_dna.to_prompt()}\n\n"
            prompt += "Based on these events, which personality traits would most likely change? "
            prompt += "List up to 3 traits that would change the most and explain how each would change "
            prompt += "(become stronger or weaker, shift in a different direction)."
            
            # Generate the trait changes analysis
            changes_analysis = await self._generate_llm_response(prompt)
            
            # Apply changes by creating a targeted mutation
            # Starting with a simple mutation for now
            evolved_dna = original_dna.mutate(intensity)
            
            # Generate new description
            race = npc_data.get("race", "human")
            gender = npc_data.get("gender", None)
            
            evolved_description = await self.generate_npc_description_with_dna(
                npc_name, race, gender, evolved_dna
            )
            
            # Track the evolution
            evolution_data = {
                "name": npc_name,
                "original_dna": original_dna.dna_string,
                "evolved_dna": evolved_dna.dna_string,
                "events": events,
                "changes_analysis": changes_analysis,
                "original_description": npc_data.get("description", ""),
                "evolved_description": evolved_description
            }
            
            # Update the NPC with evolved data
            npc_data.update({
                "dna": evolved_dna.dna_string,
                "dna_traits": evolved_dna.traits,
                "description": evolved_description,
                "evolution_history": npc_data.get("evolution_history", []) + [evolution_data]
            })
            
            return evolution_data
        else:
            return {"error": f"NPC {npc_name} does not have DNA information"}
