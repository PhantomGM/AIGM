"""
LLM Interface Tool

This module provides a standardized interface for interacting with language models.
It supports different LLM providers and includes functionality for prompt management,
output parsing, and response handling.
"""

import logging
import os
import json
import time
from typing import Dict, List, Any, Optional, Union, Callable
import importlib.util

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMInterface:
    """
    Interface for working with Language Learning Models.
    
    This class provides a standardized way to interact with different LLM providers
    and includes functionality for prompt management, output parsing, and response handling.
    """
    
    def __init__(self, provider: str = "openai", model: str = None, api_key: str = None):
        """
        Initialize the LLM interface.
        
        Args:
            provider: The LLM provider (e.g., "openai", "anthropic", "huggingface").
            model: The specific model to use. If None, will use a default for the provider.
            api_key: API key for the provider. If None, will try to get from environment.
        """
        self.provider = provider.lower()
        
        # Set default models based on provider
        self.default_models = {
            "openai": "gpt-4-turbo-preview",
            "anthropic": "claude-2",
            "huggingface": "meta-llama/Llama-2-70b-chat-hf",
            "local": "llama.cpp"
        }
        
        # Use provided model or default for provider
        self.model = model or self.default_models.get(self.provider, "gpt-4-turbo-preview")
        
        # Get API key from provided value or environment variable
        self.api_key = api_key or os.environ.get(f"{self.provider.upper()}_API_KEY")
        
        # Initialize the client based on the provider
        self.client = self._initialize_client()
        
        # Cache for storing results to avoid duplicate calls
        self.cache = {}
        
        # Prompt templates store
        self.prompt_templates = {}
        
        # Rate limiting settings
        self.rate_limit_delay = 0.1  # seconds between calls, default value
        self.last_call_time = 0
        
        logger.info(f"Initialized LLM interface with provider: {provider}, model: {self.model}")
    
    def _initialize_client(self) -> Any:
        """
        Initialize the appropriate client based on the provider.
        
        Returns:
            The initialized client object.
        """
        try:
            if self.provider == "openai":
                # Check if openai is installed
                if importlib.util.find_spec("openai") is None:
                    logger.error("OpenAI package not installed. Please install with: pip install openai")
                    return None
                
                import openai
                openai.api_key = self.api_key
                return openai.Client(api_key=self.api_key)
            
            elif self.provider == "anthropic":
                # Check if anthropic is installed
                if importlib.util.find_spec("anthropic") is None:
                    logger.error("Anthropic package not installed. Please install with: pip install anthropic")
                    return None
                
                import anthropic
                return anthropic.Anthropic(api_key=self.api_key)
            
            elif self.provider == "huggingface":
                # Check if transformers is installed
                if importlib.util.find_spec("transformers") is None:
                    logger.error("Transformers package not installed. Please install with: pip install transformers")
                    return None
                
                from transformers import pipeline
                return pipeline("text-generation", model=self.model)
            
            elif self.provider == "local":
                # This is a placeholder for a local model integration
                # You would integrate with llama.cpp or another library here
                logger.warning("Local provider support is limited. Using mock implementation.")
                return None
            
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                return None
                
        except Exception as e:
            logger.error(f"Error initializing client for provider {self.provider}: {e}")
            return None
    
    def generate_response(self, prompt: str, system_message: str = None, 
                          temperature: float = 0.7, max_tokens: int = 1024, 
                          cache_key: str = None, user_id: str = None) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM.
            system_message: Optional system message for models that support it.
            temperature: Controls randomness (0-1).
            max_tokens: Maximum tokens to generate.
            cache_key: If provided, will cache the result with this key.
            user_id: Optional user identifier for API calls.
            
        Returns:
            The generated response text.
        """
        # Check cache if a cache_key is provided
        if cache_key and cache_key in self.cache:
            logger.info(f"Using cached response for key: {cache_key}")
            return self.cache[cache_key]
        
        # Implement rate limiting
        self._apply_rate_limit()
        
        try:
            response_text = ""
            
            if self.provider == "openai":
                messages = []
                
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    user=user_id
                )
                
                response_text = response.choices[0].message.content
            
            elif self.provider == "anthropic":
                if system_message:
                    full_prompt = f"{system_message}\n\nHuman: {prompt}\n\nAssistant:"
                else:
                    full_prompt = f"Human: {prompt}\n\nAssistant:"
                
                response = self.client.completions.create(
                    prompt=full_prompt,
                    model=self.model,
                    max_tokens_to_sample=max_tokens,
                    temperature=temperature
                )
                
                response_text = response.completion
            
            elif self.provider == "huggingface":
                # For Hugging Face, we'll just use the prompt directly
                # You may want to adapt this for specific models
                if system_message:
                    full_prompt = f"{system_message}\n\n{prompt}"
                else:
                    full_prompt = prompt
                
                response = self.client(
                    full_prompt, 
                    max_length=len(full_prompt.split()) + max_tokens,
                    temperature=temperature,
                    do_sample=True
                )
                
                # Extract the generated text beyond the prompt
                response_text = response[0]["generated_text"]
                
                # Remove the input prompt from the response
                if response_text.startswith(full_prompt):
                    response_text = response_text[len(full_prompt):].strip()
            
            elif self.provider == "local":
                # Mock implementation for local provider
                logger.warning("Using mock implementation for local provider")
                response_text = f"This is a mock response for the prompt: {prompt[:30]}..."
            
            # Cache the result if a cache_key is provided
            if cache_key:
                self.cache[cache_key] = response_text
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
    def _apply_rate_limit(self) -> None:
        """
        Apply rate limiting to avoid hitting API rate limits.
        """
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_call_time = time.time()
    
    def load_prompt_template(self, template_path: str) -> None:
        """
        Load prompt templates from a JSON file.
        
        Args:
            template_path: Path to the JSON file containing prompt templates.
        """
        try:
            with open(template_path, 'r') as f:
                templates = json.load(f)
                
            self.prompt_templates.update(templates)
            logger.info(f"Loaded {len(templates)} prompt templates from {template_path}")
        
        except Exception as e:
            logger.error(f"Error loading prompt templates from {template_path}: {e}")
    
    def get_prompt_from_template(self, template_name: str, variables: Dict[str, str] = None) -> str:
        """
        Get a prompt using a named template and fill in variables.
        
        Args:
            template_name: The name of the template to use.
            variables: Dictionary of variables to fill in the template.
            
        Returns:
            The filled template, or an error message if the template is not found.
        """
        if template_name not in self.prompt_templates:
            logger.warning(f"Template '{template_name}' not found")
            return f"ERROR: Prompt template '{template_name}' not found"
        
        template = self.prompt_templates[template_name]
        
        if variables:
            # Replace variables in the template
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                template = template.replace(placeholder, str(value))
        
        return template
    
    def clear_cache(self) -> None:
        """
        Clear the response cache.
        """
        self.cache = {}
        logger.info("Cleared response cache")
    
    def set_rate_limit_delay(self, delay_seconds: float) -> None:
        """
        Set the rate limiting delay between API calls.
        
        Args:
            delay_seconds: Delay in seconds between API calls.
        """
        self.rate_limit_delay = max(0.0, delay_seconds)  # Ensure non-negative
        logger.info(f"Set rate limit delay to {self.rate_limit_delay} seconds")
    
    def batch_generate(self, prompts: List[str], system_message: str = None, 
                      temperature: float = 0.7, max_tokens: int = 1024) -> List[str]:
        """
        Generate responses for multiple prompts in batch.
        
        Args:
            prompts: List of prompts to process.
            system_message: Optional system message for models that support it.
            temperature: Controls randomness (0-1).
            max_tokens: Maximum tokens to generate.
            
        Returns:
            List of generated responses.
        """
        responses = []
        
        for prompt in prompts:
            response = self.generate_response(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens
            )
            responses.append(response)
        
        return responses
    
    def summarize_text(self, text: str, max_length: int = 100) -> str:
        """
        Summarize a text using the LLM.
        
        Args:
            text: The text to summarize.
            max_length: Approximate maximum length of the summary in words.
            
        Returns:
            The summarized text.
        """
        prompt = f"Please summarize the following text in about {max_length} words or less:\n\n{text}"
        
        return self.generate_response(
            prompt=prompt,
            system_message="You are a helpful assistant that summarizes text accurately and concisely.",
            temperature=0.3,  # Lower temperature for more deterministic results
            max_tokens=max_length * 6  # Rough estimate of tokens needed
        )
    
    def extract_structured_data(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from text according to a schema.
        
        Args:
            text: The text to extract data from.
            schema: A dictionary defining the expected structure.
            
        Returns:
            A dictionary containing the extracted data.
        """
        # Convert schema to a string representation
        schema_str = json.dumps(schema, indent=2)
        
        prompt = f"""
Extract structured data from the following text according to the schema below.
Respond ONLY with valid JSON that matches the schema.

SCHEMA:
{schema_str}

TEXT:
{text}

EXTRACTED JSON:
"""
        
        response = self.generate_response(
            prompt=prompt,
            system_message="You are a data extraction assistant. Extract structured data from text and return only valid JSON that matches the given schema.",
            temperature=0.1,  # Very low temperature for more deterministic results
            max_tokens=1000
        )
        
        # Try to parse the response as JSON
        try:
            # First try to find JSON in the response if it's not a pure JSON response
            if not response.strip().startswith('{') and not response.strip().startswith('['):
                import re
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
                if json_match:
                    response = json_match.group(1)
                else:
                    # Try to find anything that looks like JSON
                    json_match = re.search(r'({[\s\S]*})', response)
                    if json_match:
                        response = json_match.group(1)
            
            extracted_data = json.loads(response.strip())
            return extracted_data
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extracted data as JSON: {e}")
            logger.error(f"Raw response: {response}")
            return {"error": "Failed to extract structured data", "raw_response": response}
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of a text using the LLM.
        
        Args:
            text: The text to analyze.
            
        Returns:
            A dictionary with sentiment analysis results.
        """
        prompt = f"""
Perform sentiment analysis on the following text. Rate the sentiment on a scale from -1.0 (very negative) to 1.0 (very positive),
where 0.0 is neutral. Also identify the primary emotion (e.g., joy, anger, sadness, fear, surprise, disgust, trust, anticipation)
and provide a brief explanation for your analysis.

TEXT:
{text}

Respond in JSON format with the following keys:
- sentiment_score: A float from -1.0 to 1.0
- primary_emotion: A string naming the primary emotion
- explanation: A brief explanation of your analysis
"""
        
        response = self.generate_response(
            prompt=prompt,
            system_message="You are a sentiment analysis expert. Analyze text and return only valid JSON with the sentiment analysis results.",
            temperature=0.3,
            max_tokens=500
        )
        
        try:
            import re
            json_match = re.search(r'({[\s\S]*})', response)
            if json_match:
                response = json_match.group(1)
            
            sentiment_data = json.loads(response)
            return sentiment_data
        
        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Failed to parse sentiment analysis as JSON: {e}")
            return {
                "sentiment_score": 0.0,
                "primary_emotion": "unknown",
                "explanation": "Failed to analyze sentiment properly",
                "raw_response": response
            }
