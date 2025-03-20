"""
NPC Personality DNA Decoder Module

This module provides functionality to decode NPC personality DNA strings 
into structured prompts for character descriptions and behavior profiles.
"""

import os
import re
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NPCPersonalityDecoder:
    """
    A decoder for NPC personality DNA that translates structured DNA strings
    into rich character descriptions.
    """
    
    def __init__(self):
        """Initialize the NPC Personality Decoder."""
        logger.info("Initializing NPC Personality Decoder")
        self.storage_dir = Path("storage/npc_descriptions")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Updated trait descriptions based on the detailed prompt
        self.lnc_trait_descriptions = {
            # Paired traits with their full descriptions
            "B": "Brave, willing to face danger",
            "C": "Cautious, avoids unnecessary risks",
            "R": "Reserved, controlled in expression",
            "O": "Outspoken, expresses opinions freely",
            "L": "Loyal, values commitments",
            "T": "Independent, values freedom",
            "F": "Confident, sure of abilities",
            "I": "Insecure, doubts capabilities",
            "S": "Stoic, hides emotions",
            "X": "Expressive, shows feelings openly",
            "P": "Patient, willing to wait",
            "M": "Impulsive, acts on sudden urges",
            "D": "Methodical, follows procedures",
            "U": "Unpredictable, embraces spontaneity",
            "G": "Generous, shares resources",
            "H": "Protective, conserves resources",
            "Y": "Suspicious, distrusts others",
            "W": "Trusting, believes in others",
            "E": "Serious, focused on situations",
            "A": "Playful, finds humor in life",
            "N": "Introverted, prefers solitude",
            "V": "Extroverted, seeks social interaction",
            "K": "Competitive, strives to excel",
            "Q": "Harmonious, values cooperation",
            "Z": "Curious, seeks knowledge",
            "J": "Judgmental, quick to form opinions"
        }
        
        self.gne_trait_descriptions = {
            # Updated GNE values based on the prompt
            "H": "Honest", 
            "C": "Compassionate",
            "K": "Kind",
            "G": "Generous",
            "L": "Loyal",
            "J": "Just",
            "M": "Merciful",
            "F": "Forgiving",
            "E": "Empathetic",
            "B": "Benevolent",
            "U": "Humble",
            "S": "Selfless",
            "I": "Integrity",
            "R": "Responsible",
            "T": "Tolerant",
            "A": "Fair",
            "D": "Devoted",
            "V": "Charitable",
            "Y": "Accountable",
            "X": "Virtuous"
        }
        
        # LNC and GNE alignment descriptions
        self.lnc_alignment = {
            1: "Highly Chaotic - Rejects established norms, embraces unpredictability",
            2: "Very Chaotic - Strong preference for freedom and spontaneity",
            3: "Chaotic - Values freedom and adaptability",
            4: "Somewhat Chaotic - Prefers flexibility with some respect for rules",
            5: "Neutral - Balance between structure and adaptability",
            6: "Somewhat Lawful - Generally respects rules with some flexibility",
            7: "Lawful - Values rules and structure",
            8: "Very Lawful - Strong preference for order and established systems",
            9: "Highly Lawful - Rigid adherence to rules, structure, and tradition"
        }
        
        self.gne_alignment = {
            1: "Highly Evil - Malicious, cruel, willing to harm others for personal gain",
            2: "Very Evil - Prioritizes self-interest over others' wellbeing",
            3: "Evil - Generally selfish and inconsiderate",
            4: "Somewhat Evil - Often self-interested with occasional consideration",
            5: "Neutral - Balanced between altruism and self-interest",
            6: "Somewhat Good - Often considerate with occasional self-interest",
            7: "Good - Generally kind and helpful",
            8: "Very Good - Prioritizes others' wellbeing over self-interest",
            9: "Highly Good - Selfless, altruistic, devoted to helping others"
        }
        
        # Intensity descriptions
        self.intensity_descriptions = {
            1: "Subtle - Barely noticeable, emerges in specific situations",
            2: "Moderate - Present but not dominant",
            3: "Strong - Clearly evident in behavior",
            4: "Defining - A core aspect of personality",
            5: "Overwhelming - Dominates behavior in most situations"
        }
    
    def format_personality_dna(self, dna_string: str) -> Dict[str, Any]:
        """
        Parse and format an NPC personality DNA string into a structured dictionary.
        
        Args:
            dna_string: The NPC personality DNA string to format.
            
        Returns:
            A dictionary containing the parsed DNA components.
        """
        result = {
            "lnc_average": 5,
            "gne_average": 5,
            "lnc_traits": [],
            "gne_traits": []
        }
        
        # Extract alignment averages
        alignment_match = re.search(r'\((\d)/(\d)\)', dna_string)
        if alignment_match:
            result["lnc_average"] = int(alignment_match.group(1))
            result["gne_average"] = int(alignment_match.group(2))
        
        # Split into LNC and GNE sections
        parts = dna_string.split(" - ")
        if len(parts) >= 2:
            # Extract LNC traits
            lnc_section = parts[0].split(") ")[1] if ")" in parts[0] else parts[0]
            lnc_traits = lnc_section.split(",")
            
            for trait in lnc_traits:
                if len(trait) >= 3 and trait[0].isdigit() and trait[2].isdigit():
                    lnc_score = int(trait[0])
                    trait_code = trait[1]
                    intensity = int(trait[2])
                    
                    trait_info = {
                        "code": trait_code,
                        "lnc_score": lnc_score,
                        "intensity": intensity,
                        "description": self.lnc_trait_descriptions.get(trait_code, "Unknown trait"),
                        "intensity_desc": self.intensity_descriptions.get(intensity, "Normal")
                    }
                    result["lnc_traits"].append(trait_info)
            
            # Extract GNE traits
            gne_traits = parts[1].split(",")
            
            for trait in gne_traits:
                if len(trait) >= 2 and trait[0].isalpha() and trait[1].isdigit():
                    trait_code = trait[0]
                    gne_score = int(trait[1])
                    
                    # Determine strength categorization
                    if gne_score >= 7:
                        strength_desc = "Very Strong (present in most situations)"
                    elif gne_score >= 5:
                        strength_desc = "Strong (regularly exhibited)"
                    elif gne_score >= 3:
                        strength_desc = "Moderate (occasionally present)"
                    else:
                        strength_desc = "Minimal (rarely exhibited or opposite trait may dominate)"
                        
                    trait_info = {
                        "code": trait_code,
                        "gne_score": gne_score,
                        "description": self.gne_trait_descriptions.get(trait_code, "Unknown trait"),
                        "strength_desc": strength_desc
                    }
                    result["gne_traits"].append(trait_info)
        
        return result
    
    def decode_personality(self, dna_string: str, additional_context: str = "") -> str:
        """
        Decode an NPC personality DNA string into a rich character prompt.
        
        Args:
            dna_string: The NPC personality DNA string to decode.
            additional_context: Optional additional context about the character.
            
        Returns:
            A structured prompt for LLM interpretation of the character.
        """
        # Format the DNA for analysis
        formatted_dna = self.format_personality_dna(dna_string)
        
        # Build the structured prompt
        prompt = f"""
# NPC PERSONALITY PROFILE GENERATION

## DNA ANALYSIS
You are interpreting an NPC's Personality DNA to create a rich character profile. The DNA contains the following elements:

**Overall Alignment**: {self.lnc_alignment.get(formatted_dna["lnc_average"], "Neutral")} / {self.gne_alignment.get(formatted_dna["gne_average"], "Neutral")}

**Core Character Traits:**
"""
        
        # Add LNC traits with more detailed interpretation
        for trait in formatted_dna["lnc_traits"]:
            intensity_desc = self.intensity_descriptions.get(trait["intensity"], "Moderate")
            prompt += f"- {intensity_desc.split(' - ')[0]} ({trait['intensity']}/5) - {trait['description']}\n"
        
        prompt += "\n**Moral/Ethical Values:**\n"
        
        # Add GNE traits with more contextual interpretations
        for trait in formatted_dna["gne_traits"]:
            if trait["gne_score"] >= 7:
                strength = "Very Strong"
                context = "present in most situations, a defining characteristic"
            elif trait["gne_score"] >= 5:
                strength = "Strong"
                context = "regularly exhibited, a notable characteristic"
            elif trait["gne_score"] >= 3:
                strength = "Moderate"
                context = "occasionally present, situationally expressed"
            else:
                strength = "Minimal"
                context = "rarely exhibited or may display the opposite"
                
            prompt += f"- {strength} ({trait['gne_score']}/9) - {trait['description']} ({context})\n"
        
        # Add additional context and framework for comprehensive character profile
        prompt += f"""
## ADDITIONAL CONTEXT
{additional_context}

## CHARACTER PROFILE FRAMEWORK
Based on the DNA analysis and additional context, please generate a rich character profile with the following sections:

1. **Personality Overview**: A 2-3 sentence summary of this character's core personality, highlighting their dominant traits and general approach to life.

2. **Defining Traits**: The 3-5 most important traits that define this character's behavior and decisions, including how these traits manifest in everyday situations.

3. **Contradictions & Complexity**: What internal conflicts or seemingly contradictory aspects exist? How do these tensions create depth and nuance in the character?

4. **Behavioral Patterns**:
   - How they typically react under pressure or in crisis situations
   - Their attitude toward authority figures and those with power over them
   - How they treat subordinates or those they have influence over
   - Their core values and what they cherish most in life

5. **Voice & Expression**: 
   - Speech pattern (formal/casual, verbose/terse, etc.)
   - Distinctive phrases or verbal tics they might use
   - How their emotional state affects their communication style
   - Non-verbal communication tendencies

6. **Background Implications**: What past experiences might have shaped this personality? Create plausible backstory elements that would explain their current traits.

7. **Development Potential**: 
   - How might this character evolve over time?
   - What events might trigger personal growth or change?
   - Which traits might soften or intensify through different experiences?

Remember to incorporate the steampunk setting with magical elements in your character interpretation. Focus on creating a psychologically believable character that feels unique and distinct.
"""
        
        return prompt
    
    def save_npc_description(self, npc_name: str, description: str) -> str:
        """
        Save an NPC description to disk.
        
        Args:
            npc_name: The name of the NPC for the filename.
            description: The description/prompt to save.
            
        Returns:
            The path where the description was saved.
        """
        # Create a safe filename
        safe_name = re.sub(r'[^\w\-_]', '_', npc_name)
        file_path = self.storage_dir / f"{safe_name}_description.md"
        
        # Save the description
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(description)
        
        logger.info(f"Saved NPC description to {file_path}")
        return str(file_path)
    
    def load_npc_description(self, npc_name: str) -> Optional[str]:
        """
        Load an NPC description from disk.
        
        Args:
            npc_name: The name of the NPC to load.
            
        Returns:
            The description string if found, None otherwise.
        """
        safe_name = re.sub(r'[^\w\-_]', '_', npc_name)
        file_path = self.storage_dir / f"{safe_name}_description.md"
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        return None
