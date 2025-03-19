"""
Rules Reference Agent Implementation

This module implements the Rules Reference Agent, which serves as the authority on game mechanics
and rule systems within the AI Game Master framework. It interprets game rules accurately for
various supported systems, determines appropriate checks, saves, DCs, and mechanical outcomes.
"""

import logging
from typing import Dict, Any, Optional, List, Union

from ..base_agent import BaseAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RulesReferenceAgent(BaseAgent):
    """
    The Rules Reference Agent is the authority on game mechanics and rule systems.
    
    It provides accurate rules interpretations and mechanical outcomes for various
    tabletop RPG systems (D&D 5e, Pathfinder, etc.).
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Rules Reference Agent.
        
        Args:
            config: Optional configuration dictionary for the agent.
        """
        super().__init__("Rules Reference", config)
        self.supported_systems = self.config.get("supported_systems", ["dnd5e"])
        self.current_system = self.config.get("default_system", "dnd5e")
        self.house_rules = self.config.get("house_rules", {})
        
        # Dictionary to store rule precedents (previous rulings)
        self.rule_precedents = {}
        
        logger.info(f"Rules Reference Agent initialized with systems: {self.supported_systems}")
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a rules-related query and generate a response.
        
        Args:
            query: The query text from the Controller Agent.
            context: Optional dictionary containing relevant context information.
            
        Returns:
            A string response with the rules interpretation.
        """
        context = context or {}
        
        # Check if we should change the game system
        if "system" in context and context["system"] in self.supported_systems:
            self.current_system = context["system"]
        
        # Extract relevant information from the context
        character_info = context.get("character_info", {})
        situation = context.get("situation", "")
        action_type = context.get("action_type", "")
        
        # Construct the prompt for the LLM
        prompt = self._construct_rules_prompt(query, character_info, situation, action_type)
        
        # Generate the response
        response = self._generate_llm_response(prompt)
        
        # Store this ruling as a precedent if appropriate
        if context.get("store_precedent", False):
            self._store_rule_precedent(query, response)
        
        return response
    
    def _construct_rules_prompt(self, query: str, character_info: Dict, situation: str, action_type: str) -> str:
        """
        Construct a prompt for the LLM to interpret rules.
        
        Args:
            query: The rules query.
            character_info: Information about relevant characters.
            situation: Description of the current situation.
            action_type: The type of action being taken.
            
        Returns:
            A formatted prompt for the LLM.
        """
        # Start with the base system prompt
        prompt_parts = [self.system_prompt]
        
        # Add context information
        prompt_parts.append(f"CURRENT GAME SYSTEM: {self.current_system}")
        
        if situation:
            prompt_parts.append(f"CURRENT SITUATION: {situation}")
        
        if character_info:
            prompt_parts.append("CHARACTER INFORMATION:")
            for char_name, char_data in character_info.items():
                prompt_parts.append(f"- {char_name}: {char_data}")
        
        if action_type:
            prompt_parts.append(f"ACTION TYPE: {action_type}")
        
        # Add any relevant house rules
        if self.house_rules and self.current_system in self.house_rules:
            prompt_parts.append("HOUSE RULES:")
            for rule_name, rule_desc in self.house_rules[self.current_system].items():
                prompt_parts.append(f"- {rule_name}: {rule_desc}")
        
        # Add any relevant precedents
        relevant_precedents = self._find_relevant_precedents(query)
        if relevant_precedents:
            prompt_parts.append("RELEVANT PRECEDENTS:")
            for q, r in relevant_precedents:
                prompt_parts.append(f"Q: {q}")
                prompt_parts.append(f"A: {r}")
                prompt_parts.append("---")
        
        # Add the query itself
        prompt_parts.append(f"QUERY: {query}")
        prompt_parts.append("Please provide a comprehensive rules interpretation for this query.")
        
        return "\n\n".join(prompt_parts)
    
    def _store_rule_precedent(self, query: str, response: str) -> None:
        """
        Store a rule precedent for future reference.
        
        Args:
            query: The rules query.
            response: The ruling provided.
        """
        # In a real implementation, this would likely store to a database
        key = f"{self.current_system}:{query.lower().strip()}"
        self.rule_precedents[key] = response
        logger.info(f"Stored rule precedent for '{query[:30]}...'")
    
    def _find_relevant_precedents(self, query: str, max_results: int = 3) -> List[tuple]:
        """
        Find relevant precedents for a given query.
        
        Args:
            query: The rules query.
            max_results: Maximum number of precedents to return.
            
        Returns:
            A list of (query, response) tuples.
        """
        # In a real implementation, this would use semantic search or similar
        # For now, we'll just do a simple substring match
        query_lower = query.lower().strip()
        system_prefix = f"{self.current_system}:"
        
        relevant = []
        for key, response in self.rule_precedents.items():
            if key.startswith(system_prefix) and any(term in key for term in query_lower.split()):
                # Extract the original query by removing system prefix
                original_query = key[len(system_prefix):]
                relevant.append((original_query, response))
        
        return relevant[:max_results]
    
    def add_house_rule(self, system: str, rule_name: str, rule_description: str) -> None:
        """
        Add a house rule for a specific game system.
        
        Args:
            system: The game system (e.g., "dnd5e").
            rule_name: A name for the house rule.
            rule_description: Description of the house rule.
        """
        if system not in self.house_rules:
            self.house_rules[system] = {}
        
        self.house_rules[system][rule_name] = rule_description
        logger.info(f"Added house rule '{rule_name}' for system {system}")
    
    def get_supported_systems(self) -> List[str]:
        """Get the list of supported game systems."""
        return self.supported_systems
    
    def set_current_system(self, system: str) -> bool:
        """
        Set the current game system.
        
        Args:
            system: The game system to set as current.
            
        Returns:
            True if successful, False if the system is not supported.
        """
        if system in self.supported_systems:
            self.current_system = system
            logger.info(f"Set current system to {system}")
            return True
        else:
            logger.warning(f"Attempted to set unsupported system: {system}")
            return False
