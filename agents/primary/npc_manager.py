"""
NPC Manager Agent Implementation

This module implements the NPC Manager Agent, which is responsible for creating and controlling
non-player characters with consistent personalities and motivations. It generates appropriate
dialogue, tracks NPC knowledge and relationships, and determines NPC actions.
"""

import logging
import random
from typing import Dict, Any, Optional, List, Union

from ..base_agent import BaseAgent

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
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
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
            return self._generate_npc_dialogue(npc_name, player_input, situation, current_location)
        elif query_type == "npc_action":
            return self._determine_npc_action(npc_name, situation, current_location)
        elif query_type == "npc_creation":
            npc_type = context.get("npc_type", "")
            npc_role = context.get("npc_role", "")
            initial_traits = context.get("initial_traits", {})
            return self._create_npc(npc_name, npc_type, npc_role, initial_traits)
        elif query_type == "npc_information":
            return self._retrieve_npc_information(npc_name)
        else:
            # Default to processing as a free-form query
            return self._generate_npc_response(query, context)
    
    def _generate_npc_dialogue(self, npc_name: str, player_input: str, situation: str, location: str) -> str:
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
            self._create_npc(npc_name, "", "", {})
        
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
        dialogue = self._generate_llm_response(prompt)
        
        # Update dialogue history
        if "dialogue_history" not in npc_data:
            npc_data["dialogue_history"] = []
        npc_data["dialogue_history"].append({
            "player": player_input,
            "npc": dialogue
        })
        
        return dialogue
    
    def _determine_npc_action(self, npc_name: str, situation: str, location: str) -> str:
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
            self._create_npc(npc_name, "", "", {})
        
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
        return self._generate_llm_response(prompt)
    
    def _create_npc(self, npc_name: str, npc_type: str, npc_role: str, initial_traits: Dict[str, Any]) -> str:
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
        npc_profile = self._generate_llm_response(prompt)
        
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
    
    def _retrieve_npc_information(self, npc_name: str) -> str:
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
    
    def _generate_npc_response(self, query: str, context: Dict[str, Any]) -> str:
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
        
        return self._generate_llm_response(prompt)
    
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
            logger.warning(f"Cannot add knowledge: NPC {npc_name} doesn't exist")
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
