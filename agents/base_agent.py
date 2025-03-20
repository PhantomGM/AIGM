"""
Base Agent Implementation

This module defines the BaseAgent class that serves as the foundation for all specialized agents
in the AI Game Master system. It provides common functionality and interfaces that all agents should implement.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents in the AI Game Master system.
    
    All agents should inherit from this class and implement its abstract methods.
    """
    
    def __init__(self, agent_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_name: A unique name for this agent instance.
            config: Optional configuration dictionary for the agent.
        """
        self.agent_name = agent_name
        self.config = config or {}
        self.system_prompt = self.config.get("system_prompt", "")
        logger.info(f"Initialized {agent_name} agent")
    
    @abstractmethod
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a query from the Controller Agent and generate a response.
        
        This is the main method that specialized agents must implement.
        
        Args:
            query: The query text from the Controller Agent.
            context: Optional dictionary containing relevant context information.
            
        Returns:
            A string response to the query.
        """
        pass
    
    def load_system_prompt(self, prompt_file: str) -> None:
        """
        Load the system prompt for this agent from a file.
        
        Args:
            prompt_file: Path to the file containing the system prompt.
        """
        try:
            with open(prompt_file, 'r', encoding='utf-8') as file:
                self.system_prompt = file.read()
            logger.info(f"Loaded system prompt for {self.agent_name} from {prompt_file}")
        except Exception as e:
            logger.error(f"Error loading system prompt from {prompt_file}: {e}")
    
    def set_system_prompt(self, prompt: str) -> None:
        """
        Set the system prompt for this agent directly.
        
        Args:
            prompt: The system prompt text.
        """
        self.system_prompt = prompt
        logger.info(f"Set system prompt for {self.agent_name}")
    
    async def _generate_llm_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response using a language model asynchronously.
        
        Args:
            prompt: The prompt to send to the language model.
            system_prompt: Optional system prompt to override the default.
            
        Returns:
            The generated response from the language model.
        """
        # This is a placeholder implementation. In a real implementation, this would
        # call an actual LLM API like OpenAI, Anthropic, etc.
        logger.info(f"LLM call from {self.agent_name}: {prompt[:50]}...")
        
        # In a real implementation, this would be replaced with actual LLM API calls
        response = f"[LLM Response from {self.agent_name}]: This is a placeholder response for '{prompt[:30]}...'"
        return response
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        Format the context dictionary into a string that can be included in prompts.
        
        Args:
            context: The context dictionary to format.
            
        Returns:
            A formatted string representation of the context.
        """
        formatted = ["CONTEXT:"]
        
        for key, value in context.items():
            if isinstance(value, (list, dict)):
                import json
                value_str = json.dumps(value, indent=2)
            else:
                value_str = str(value)
            
            formatted.append(f"{key.upper()}: {value_str}")
        
        return "\n".join(formatted)
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.agent_name} Agent"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.agent_name}')"
