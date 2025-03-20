"""
DNA Decoder Module

This module implements advanced decoding capabilities for the World DNA system,
transforming complex DNA strings into rich world descriptions and narratives.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from .dna_generator import WorldDNA, WorldDNAGenerator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorldDNADecoder:
    """
    Class for decoding world DNA into rich descriptions using the Enhanced World Creation DNA System.
    Utilizes LLM-based interpretation through a specialized prompt framework.
    """
    
    # The decoder prompt that guides the LLM in interpreting DNA strings
    DECODER_PROMPT = """
You are the "World Decoding AI." You receive a "World DNA Code" in the Enhanced World Creation DNA System vX.X format (including ENV{}, SOC{}, CON{}, HIS{}, REG{}, CRIT{}, CHAIN{}, EVO{}, TREND{}, etc.). Your goal: **Decode** this DNA, along with any provided context, into a rich, coherent setting or campaign pitch. This decoding is done only once to establish the starting world state. 

Please follow the structure and guidelines below:

--------------------------------------------------------------------------------
# DECODING INSTRUCTIONS

1. **Primary Scales & Genre**
   - Interpret the core numeric scales (T, M, A) or any additional ones (TM, MA, TA) to outline:
     - **Technology Level**  
     - **Magic Prevalence**  
     - **Authority Structures**  
   - Identify or confirm any listed **genres** (e.g., "fantasy-medieval," "steampunk," "post-apocalyptic," etc.), highlighting key elements that shape the tone and style of the world.

2. **ENV / SOC / CON / HIS Blocks** (Environmental, Societal, Conflict, Historical Data)
   - Summarize each domain **briefly**:
     - **Environment (ENV):** Major geography, climate, resources, or anomalies.
     - **Society (SOC):** Cultural norms, power structures, daily life aspects.
     - **Conflicts (CON):** Current or longstanding disputes, warfare, ideological clashes.
     - **History (HIS):** Key historical events, legacies, myths shaping the present.
   - If any data is clearly **contradictory** (e.g., "arid desert" + "massive rainfall"), reinterpret or highlight the tension as part of the setting ("an ongoing magical climate anomaly," etc.).

3. **REG (Regional Breakdown)**
   - List each region (N, S, E, W, C, or otherwise named) alongside its distinct **traits**.
   - Include a **short** bullet list or paragraph describing:
     - **Regional Features** (environment, resources, local culture)
     - **Local Challenges** (conflicts, resource shortages, magical phenomena)
     - **Relationship to Global Norm** (is it different from the rest of the world? more advanced/less advanced?)

4. **CRIT (Critical Thresholds) & CHAIN (Chain Reactions)**
   - Identify any major tipping points (e.g., resource shortages, social unrest, ecological disasters).
   - Outline **chain reactions**: "If X happens in Region A, it triggers Y in Region B," etc.
   - Keep it **concise**—just enough to show how events might cascade.

5. **EVO (Dynamic Evolution)**
   - Show how certain traits or phenomena (environmental, societal, etc.) **change over time**.
   - If data includes **PAST, PRESENT, NEAR, FAR**, summarize each briefly:
     - **Past:** Key developments that shaped today
     - **Present:** The current state or crisis
     - **Near Future:** Potential changes or escalating tensions
     - **Far Future:** Long-term consequences or utopian/dystopian projections
   - Incorporate any patterns: "ACCELERATING," "DECLINING," "UNSTABLE," or "STABILIZING."

6. **TREND (Rising or Falling Elements)**
   - Mention key traits labeled as **RISING** or **FALLING**. 
   - Explain how these trends impact the broader world or specific regions (e.g., "Magic is rising in the West, spurring conflict with the tech-savvy East").

7. **Current State & Conflicts**
   - Combine the data from ENV, SOC, CON, HIS, REG, CRIT, CHAIN, EVO, TREND into a **short** overview of the **world's present condition**:
     - **Environmental Strains** or boons
     - **Societal and Political Tensions**
     - **Active Wars or Diplomatic Crises**
     - **Historical influences still echoing** 
   - Emphasize any **immediate hooks** for storytelling.

8. **Future Trajectories**
   - Based on chain reactions, critical thresholds, and evolution patterns, outline a few **likely scenarios**:
     - **Optimistic path** (if conflicts are resolved or resources managed)
     - **Pessimistic path** (if tensions escalate or disasters strike)
   - Include how **rising/falling** traits might shape these paths.

9. **Story Elements / Campaign Hooks**
   - Provide a succinct **campaign pitch** or **story seeds** that tie directly to:
     - **Regional challenges**
     - **Critical thresholds** or **chain reactions**
     - **Any high-level conflicts** (religious, magical, technological)
   - These should be **game-ready** ideas that highlight the setting's unique aspects.

--------------------------------------------------------------------------------
# OUTPUT FORMAT

Please structure the final text with clear headings:

1. **World Overview**  
2. **Regional Breakdown**  
3. **Critical Situations** (Thresholds, Chain Reactions)  
4. **Evolution & Trends**  
5. **Current State**  
6. **Future Trajectories**  
7. **Story Elements / Campaign Hooks**

You may merge smaller sections if it flows naturally (e.g., "Critical Situations" + "Evolution" can be combined), but ensure **all** the content is addressed in some form.

--------------------------------------------------------------------------------
# FINAL INSTRUCTIONS

- Keep each heading **concise** (1–2 short paragraphs or bullet lists).  
- If data is **contradictory**, re-interpret or highlight it as an **interesting tension** in the setting.  
- Provide **just enough detail** to make the world playable or narratively rich, but do not write overly long text walls.  
- Incorporate any **additional context** the user provides (e.g., "We want a steampunk vibe," "We have a reanimator plague in the North," etc.) in each relevant section.  
- After presenting the final 7 headings, **stop**. Do not include extra commentary or disclaimers; output only the world's final profile.
"""

    def __init__(self):
        """Initialize the DNA decoder."""
        logger.info("Initializing DNA Decoder")
        
        # Ensure storage directories exist
        Path("storage/world_descriptions").mkdir(parents=True, exist_ok=True)
    
    def format_dna_for_decoding(self, advanced_dna: str) -> Dict[str, Any]:
        """
        Format an advanced DNA string into sections for easier parsing by the decoder.
        
        Args:
            advanced_dna: The advanced DNA string to format
            
        Returns:
            Dictionary with organized DNA sections
        """
        result = {
            "version": "1.0",
            "traits": {},
            "thresholds": [],
            "evolution": {},
            "regions": {},
            "chain_reactions": []
        }
        
        # Extract version
        if advanced_dna.startswith("V"):
            version_part = advanced_dna.split(" ")[0]
            result["version"] = version_part[1:]
        
        # Extract traits section
        if "TRAITS{" in advanced_dna:
            traits_section = advanced_dna.split("TRAITS{")[1].split("}")[0]
            for trait_part in traits_section.split(";"):
                if ":" in trait_part:
                    name, value = trait_part.split(":")
                    # Parse prevalence and intensity
                    if len(value) >= 2 and value[0].isdigit() and value[1].isdigit():
                        prevalence = int(value[0])
                        intensity = int(value[1])
                        result["traits"][name] = {
                            "prevalence": prevalence,
                            "intensity": intensity,
                            "raw": value
                        }
                    else:
                        result["traits"][name] = {
                            "prevalence": 5,
                            "intensity": 5,
                            "raw": value
                        }
        
        # Extract thresholds
        if "THRESH{" in advanced_dna:
            thresh_part = advanced_dna.split("THRESH{")[1].split("}")[0]
            result["thresholds"] = thresh_part.split(";")
        
        # Extract evolution patterns
        if "EVO{" in advanced_dna:
            evo_part = advanced_dna.split("EVO{")[1].split("}")[0]
            for evo_item in evo_part.split(";"):
                if ":" in evo_item and "[" in evo_item and "]" in evo_item:
                    trait, pattern_values = evo_item.split(":", 1)
                    pattern = pattern_values.split("[")[0]
                    values_str = pattern_values.split("[")[1].split("]")[0]
                    values = values_str.split(",")
                    
                    # Map values to time periods
                    time_periods = {}
                    if len(values) >= 1:
                        time_periods["PAST"] = values[0]
                    if len(values) >= 2:
                        time_periods["PRESENT"] = values[1]
                    if len(values) >= 3:
                        time_periods["NEAR"] = values[2]
                    if len(values) >= 4:
                        time_periods["FAR"] = values[3]
                    
                    result["evolution"][trait] = {
                        "pattern": pattern,
                        "values": values,
                        "time_periods": time_periods
                    }
        
        # Extract regional information (if present)
        if "REG{" in advanced_dna:
            reg_part = advanced_dna.split("REG{")[1].split("}")[0]
            for region in reg_part.split(";"):
                if ":" in region:
                    region_name, traits = region.split(":", 1)
                    region_traits = {}
                    for trait in traits.split(","):
                        if "=" in trait:
                            trait_name, value = trait.split("=")
                            region_traits[trait_name] = value
                    result["regions"][region_name] = region_traits
        
        # Extract chain reactions (if present)
        if "CHAIN{" in advanced_dna:
            chain_part = advanced_dna.split("CHAIN{")[1].split("}")[0]
            for chain in chain_part.split(";"):
                if "->" in chain:
                    trigger, effect = chain.split("->")
                    result["chain_reactions"].append({
                        "trigger": trigger,
                        "effect": effect
                    })
        
        return result
    
    def generate_extended_prompt(self, dna_data: Dict[str, Any], additional_context: str = "") -> str:
        """
        Generate the prompt for the LLM to interpret the DNA.
        
        Args:
            dna_data: Formatted DNA data
            additional_context: Any additional context to include
            
        Returns:
            Complete prompt for the LLM
        """
        # Start with the base prompt
        prompt = self.DECODER_PROMPT
        
        # Add DNA data sections
        dna_description = f"World DNA Version: {dna_data['version']}\n\n"
        
        # Add traits section
        if dna_data['traits']:
            dna_description += "TRAITS {\n"
            for trait, data in dna_data['traits'].items():
                dna_description += f"  {trait}: prevalence={data['prevalence']}, intensity={data['intensity']}\n"
            dna_description += "}\n\n"
        
        # Add thresholds section
        if dna_data['thresholds']:
            dna_description += "THRESHOLDS {\n"
            for threshold in dna_data['thresholds']:
                dna_description += f"  {threshold}\n"
            dna_description += "}\n\n"
        
        # Add evolution section
        if dna_data['evolution']:
            dna_description += "EVOLUTION {\n"
            for trait, evo_data in dna_data['evolution'].items():
                time_periods = evo_data.get('time_periods', {})
                dna_description += f"  {trait}: {evo_data['pattern']}\n"
                if time_periods:
                    dna_description += "    Time Periods:\n"
                    for period, value in time_periods.items():
                        dna_description += f"      {period}: {value}\n"
            dna_description += "}\n\n"
        
        # Add regions section
        if dna_data['regions']:
            dna_description += "REGIONS {\n"
            for region, traits in dna_data['regions'].items():
                dna_description += f"  {region}:\n"
                for trait, value in traits.items():
                    dna_description += f"    {trait}={value}\n"
            dna_description += "}\n\n"
        
        # Add chain reactions section
        if dna_data['chain_reactions']:
            dna_description += "CHAIN REACTIONS {\n"
            for chain in dna_data['chain_reactions']:
                dna_description += f"  {chain['trigger']} -> {chain['effect']}\n"
            dna_description += "}\n\n"
        
        # Add additional context if provided
        if additional_context:
            dna_description += f"ADDITIONAL CONTEXT:\n{additional_context}\n\n"
        
        # Combine into final prompt
        full_prompt = f"{prompt}\n\nHere is the World DNA to decode:\n\n{dna_description}"
        
        return full_prompt
    
    def decode_dna(self, dna_string: str, additional_context: str = "") -> str:
        """
        Decode an advanced DNA string into a rich world description.
        
        This method parses the DNA, formats it, and generates a prompt for a language model
        to interpret the DNA as a rich world setting. For this implementation, we'll just
        return the formatted prompt, which can then be sent to an LLM API.
        
        Args:
            dna_string: Advanced DNA string to decode
            additional_context: Optional additional context to include
            
        Returns:
            Formatted prompt for LLM interpretation
        """
        formatted_dna = self.format_dna_for_decoding(dna_string)
        prompt = self.generate_extended_prompt(formatted_dna, additional_context)
        
        # In a real implementation, this would be sent to an LLM API
        # For now, we'll just return the prompt
        return prompt
    
    def save_world_description(self, world_name: str, description: str) -> str:
        """
        Save a decoded world description to storage.
        
        Args:
            world_name: Name of the world
            description: The decoded description
            
        Returns:
            Path to the saved file
        """
        storage_dir = Path("storage/world_descriptions")
        file_path = storage_dir / f"{world_name.lower().replace(' ', '_')}_description.md"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(description)
        
        return str(file_path)
    
    def load_world_description(self, world_name: str) -> Optional[str]:
        """
        Load a decoded world description from storage.
        
        Args:
            world_name: Name of the world
            
        Returns:
            The world description or None if not found
        """
        file_path = Path(f"storage/world_descriptions/{world_name.lower().replace(' ', '_')}_description.md")
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

# Example usage:
# decoder = WorldDNADecoder()
# advanced_dna = "V1.6 TRAITS{climate:93;terrain:85;resources:62;hazards:33;technology:63;religion:75} THRESH{high_magic;unstable} EVO{terrain:ACCELERATING[85,95,95,95];religion:ACCELERATING[75,95,95,95]}"
# prompt = decoder.decode_dna(advanced_dna, "We want a steampunk vibe with magical elements")
