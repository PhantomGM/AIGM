"""
Controller Agent Implementation

This module implements the Controller Agent, which serves as the central hub and orchestrator
for the entire AI Game Master system. It processes player inputs, determines which specialized 
agents to consult, synthesizes responses into coherent narration, and maintains the overall game state.
"""

import logging
from typing import Dict, List, Optional, Any, Union

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ControllerAgent:
    """
    The Controller Agent is the central orchestrator for the AI Game Master system.
    
    It processes player inputs, routes queries to specialized agents, synthesizes their
    responses, and maintains the overall game state and conversation flow.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Controller Agent.
        
        Args:
            config: Optional configuration dictionary for the agent.
        """
        self.config = config or {}
        self.specialized_agents = {}
        self.game_state = {}
        self.context_history = []
        self.current_mode = "standard_gameplay"  # Other modes: "history_creation", "world_building"
        logger.info("Controller Agent initialized")
    
    def register_agent(self, agent_type: str, agent_instance: Any) -> None:
        """
        Register a specialized agent with the controller.
        
        Args:
            agent_type: The type/role of the agent (e.g., "rules_reference", "npc_manager").
            agent_instance: The agent instance to register.
        """
        self.specialized_agents[agent_type] = agent_instance
        logger.info(f"Registered {agent_type} agent")
    
    def process_input(self, user_input: str) -> str:
        """
        Process player input and generate a response.
        
        This is the main entry point for handling player interactions.
        
        Args:
            user_input: The text input from the player.
            
        Returns:
            A string response to be presented to the player.
        """
        logger.info(f"Processing user input: {user_input[:50]}...")
        
        # 1. Analyze input to determine its primary intention
        input_type = self._classify_input(user_input)
        
        # 2. Determine which agents to consult
        agents_to_consult = self._determine_relevant_agents(input_type, user_input)
        
        # 3. Gather responses from relevant agents
        agent_responses = self._gather_agent_responses(agents_to_consult, user_input)
        
        # 4. Synthesize a coherent response
        final_response = self._synthesize_response(agent_responses, input_type)
        
        # 5. Update game state and context history
        self._update_game_state(user_input, final_response)
        
        return final_response
    
    def _classify_input(self, user_input: str) -> str:
        """
        Classify the type of player input.
        
        Args:
            user_input: The text input from the player.
            
        Returns:
            A string indicating the input type (e.g., "action", "question", "dialogue").
        """
        # TODO: Implement more sophisticated input classification
        if "?" in user_input:
            return "question"
        elif user_input.startswith('"') or user_input.startswith('"'):
            return "dialogue"
        else:
            return "action"
    
    def _determine_relevant_agents(self, input_type: str, user_input: str) -> List[str]:
        """
        Determine which specialized agents should be consulted for this input.
        
        Args:
            input_type: The classified type of the user input.
            user_input: The text input from the player.
            
        Returns:
            A list of agent types to consult.
        """
        # Basic mapping of input types to relevant agents
        # In a more sophisticated implementation, this would analyze the content
        # of the input more deeply to determine relevant agents
        if input_type == "question":
            return ["rules_reference", "lore_manager", "memory_keeper"]
        elif input_type == "dialogue":
            return ["npc_manager", "memory_keeper", "narrative_designer"]
        elif input_type == "action":
            return ["world_builder", "rules_reference", "narrative_designer"]
        else:
            return ["narrative_designer"]  # Default fallback
    
    def _gather_agent_responses(self, agent_types: List[str], user_input: str) -> Dict[str, str]:
        """
        Gather responses from the specified agents.
        
        Args:
            agent_types: List of agent types to consult.
            user_input: The text input from the player.
            
        Returns:
            A dictionary mapping agent types to their responses.
        """
        responses = {}
        
        for agent_type in agent_types:
            if agent_type in self.specialized_agents:
                try:
                    # This would call the agent's process_query method in a real implementation
                    # For now, we'll return placeholder responses
                    responses[agent_type] = f"[{agent_type}] Placeholder response"
                except Exception as e:
                    logger.error(f"Error getting response from {agent_type} agent: {e}")
                    responses[agent_type] = f"[{agent_type}] Error: {str(e)}"
            else:
                logger.warning(f"Agent {agent_type} not registered")
        
        return responses
    
    def _synthesize_response(self, agent_responses: Dict[str, str], input_type: str) -> str:
        """
        Synthesize a coherent response from individual agent responses.
        
        Args:
            agent_responses: Dictionary of responses from specialized agents.
            input_type: The classified type of the user input.
            
        Returns:
            A synthesized response to present to the player.
        """
        # TODO: Implement more sophisticated response synthesis
        # This would integrate the various agent responses into a cohesive narrative
        
        # For now, just concatenate the responses with some basic formatting
        if not agent_responses:
            return "I'm not sure how to respond to that."
        
        # In a real implementation, this would use an LLM to synthesize the responses
        # into natural language appropriate for the game context
        combined_response = "\n".join(agent_responses.values())
        return combined_response
    
    def _update_game_state(self, user_input: str, system_response: str) -> None:
        """
        Update the game state based on the interaction.
        
        Args:
            user_input: The text input from the player.
            system_response: The response generated by the system.
        """
        # Add the interaction to the context history
        self.context_history.append({
            "user_input": user_input,
            "system_response": system_response,
            "timestamp": None  # Would use a proper timestamp in real implementation
        })
        
        # Keep context history to a manageable size
        if len(self.context_history) > 50:  # Arbitrary limit for now
            self.context_history = self.context_history[-50:]
    
    def change_mode(self, new_mode: str) -> None:
        """
        Change the operational mode of the controller.
        
        Args:
            new_mode: The new mode to switch to (e.g., "standard_gameplay", "history_creation").
        """
        if new_mode not in ["standard_gameplay", "history_creation", "world_building"]:
            logger.warning(f"Unknown mode: {new_mode}, staying in {self.current_mode}")
            return
        
        logger.info(f"Changing mode from {self.current_mode} to {new_mode}")
        self.current_mode = new_mode
