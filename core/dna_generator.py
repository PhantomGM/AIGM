"""
DNA Generator for World and NPC Creation

This module implements DNA-based generation systems for creating consistent and rich
worlds and NPCs. It provides tools for encoding world traits and NPC personalities
into DNA strings and then decoding them for use in game generation.
"""

import random
import logging
import json
from typing import Dict, Any, List, Tuple, Optional, Union
from pathlib import Path
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorldDNAGenerator:
    """
    An advanced DNA generator for world creation with evolving traits.
    
    This generator creates complex DNA with prevalence and intensity values for each trait,
    tracks critical thresholds and chain reactions, and models trait evolution over time.
    """
    def __init__(self):
        # Version tracking
        self.version = "1.6"
        
        # Define base traits and categories
        self.trait_categories = {
            "PHYSICAL": ["climate", "terrain", "resources", "hazards"],
            "CULTURAL": ["society", "technology", "religion", "trade"],
            "POLITICAL": ["government", "conflict", "diplomacy", "stability"],
            "MAGICAL": ["intensity", "prevalence", "schools", "artifacts"]
        }
        
        # Critical thresholds for trait interactions
        self.critical_thresholds = {
            "high_magic": {"magical.intensity": 4, "magical.prevalence": 7},
            "unstable": {"political.conflict": 4, "political.stability": 2},
            "advanced": {"cultural.technology": 7, "cultural.society": 6}
        }
        
        # Chain reaction definitions
        self.chain_reactions = {
            "magical_crisis": {
                "trigger": "high_magic",
                "effects": {
                    "political.stability": -2,
                    "cultural.society": 1,
                    "magical.artifacts": 2
                }
            },
            "societal_collapse": {
                "trigger": "unstable",
                "effects": {
                    "cultural.trade": -2,
                    "political.government": -1,
                    "cultural.society": -2
                }
            }
        }
        
        # Time periods for evolution
        self.time_periods = ["PAST", "PRESENT", "NEAR", "FAR"]
        
        # Evolution patterns
        self.evolution_patterns = {
            "ACCELERATING": {
                "description": "Rapid increase in prevalence/intensity",
                "prevalence_mod": 2,
                "intensity_mod": 1
            },
            "DECLINING": {
                "description": "Gradual decrease in prevalence/intensity",
                "prevalence_mod": -1,
                "intensity_mod": -1
            },
            "UNSTABLE": {
                "description": "Fluctuating prevalence/intensity",
                "prevalence_mod": 0,
                "intensity_mod": 2
            },
            "STABILIZING": {
                "description": "Moving toward equilibrium",
                "prevalence_mod": 0,
                "intensity_mod": -1
            }
        }

    def generate_base_traits(self) -> Dict[str, Tuple[int, int]]:
        """Generate base traits with prevalence (1-9) and intensity (1-5)."""
        traits = {}
        for category, category_traits in self.trait_categories.items():
            for trait in category_traits:
                # Generate prevalence (1-9) and intensity (1-5)
                prevalence = random.randint(1, 9)
                intensity = random.randint(1, 5)
                trait_key = f"{category.lower()}.{trait}"
                traits[trait_key] = (prevalence, intensity)
        return traits

    def check_thresholds(self, traits: Dict[str, Tuple[int, int]]) -> set:
        """Check which critical thresholds are met."""
        met_thresholds = set()
        
        for threshold_name, conditions in self.critical_thresholds.items():
            all_conditions_met = True
            for trait, min_value in conditions.items():
                if trait not in traits or traits[trait][0] < min_value:
                    all_conditions_met = False
                    break
            if all_conditions_met:
                met_thresholds.add(threshold_name)
        
        return met_thresholds

    def apply_chain_reactions(self, 
                            traits: Dict[str, Tuple[int, int]], 
                            met_thresholds: set) -> Dict[str, Tuple[int, int]]:
        """Apply chain reactions based on met thresholds."""
        modified_traits = traits.copy()
        
        for reaction_name, reaction_data in self.chain_reactions.items():
            if reaction_data["trigger"] in met_thresholds:
                for trait, modifier in reaction_data["effects"].items():
                    if trait in modified_traits:
                        prev, intens = modified_traits[trait]
                        # Apply modifier to intensity
                        new_intens = max(1, min(5, intens + modifier))
                        modified_traits[trait] = (prev, new_intens)
        
        return modified_traits

    def identify_trends(self, traits: Dict[str, Tuple[int, int]]) -> Dict[str, List[str]]:
        """Identify rising and falling trends based on trait values."""
        trends = {
            "RISING": [],
            "FALLING": []
        }
        
        # Define thresholds for trend identification
        HIGH_THRESHOLD = 7
        LOW_THRESHOLD = 3
        
        for trait, (prev, intens) in traits.items():
            if prev >= HIGH_THRESHOLD and intens >= 4:
                trends["RISING"].append(trait)
            elif prev <= LOW_THRESHOLD and intens <= 2:
                trends["FALLING"].append(trait)
        
        return trends

    def calculate_evolution(self, trait_value: Tuple[int, int], 
                          pattern: str, time_steps: int) -> List[Tuple[int, int]]:
        """Calculate trait values across time periods based on evolution pattern."""
        current_prev, current_int = trait_value
        pattern_data = self.evolution_patterns[pattern]
        evolution = [(current_prev, current_int)]
        
        for _ in range(time_steps):
            # Calculate new values based on pattern
            new_prev = max(1, min(9, current_prev + 
                                pattern_data["prevalence_mod"]))
            new_int = max(1, min(5, current_int + 
                               pattern_data["intensity_mod"]))
            
            if pattern == "UNSTABLE":
                # Add random fluctuation for unstable pattern
                new_prev = max(1, min(9, new_prev + random.randint(-1, 1)))
                new_int = max(1, min(5, new_int + random.randint(-1, 1)))
            
            evolution.append((new_prev, new_int))
            current_prev, current_int = new_prev, new_int
            
        return evolution

    def identify_evolution_patterns(self, 
                                  all_traits: Dict[str, tuple],
                                  trends: Dict[str, List[str]]) -> Dict[str, str]:
        """Identify evolution patterns for significant traits."""
        patterns = {}
        
        for trait, (prev, intens) in all_traits.items():
            # High value traits tend to accelerate
            if prev >= 7 and intens >= 4:
                patterns[trait] = "ACCELERATING"
            # Low value traits tend to decline
            elif prev <= 3 and intens <= 2:
                patterns[trait] = "DECLINING"
            # Moderate traits with high intensity are unstable
            elif 4 <= prev <= 6 and intens >= 4:
                patterns[trait] = "UNSTABLE"
            # Moderate traits with low intensity stabilize
            elif 4 <= prev <= 6 and intens <= 2:
                patterns[trait] = "STABILIZING"
        
        # Consider trends in pattern assignment
        for rising in trends["RISING"]:
            if rising in patterns and patterns[rising] != "ACCELERATING":
                patterns[rising] = "ACCELERATING"
        for falling in trends["FALLING"]:
            if falling in patterns and patterns[falling] != "DECLINING":
                patterns[falling] = "DECLINING"
        
        return patterns

    def generate_dna(self, bias: Optional[Dict] = None) -> str:
        """Generate a complete World DNA string with all components."""
        dna_parts = []
        
        # Generate version identifier
        dna_parts.append(f"V{self.version}")
        
        # Generate base traits
        all_traits = self.generate_base_traits()
        
        # Apply bias if provided
        if bias:
            for trait, (bias_prev, bias_int) in bias.items():
                if trait in all_traits:
                    prev, intens = all_traits[trait]
                    # Modify values based on bias
                    new_prev = max(1, min(9, prev + bias_prev))
                    new_int = max(1, min(5, intens + bias_int))
                    all_traits[trait] = (new_prev, new_int)
        
        # Check thresholds and apply chain reactions
        met_thresholds = self.check_thresholds(all_traits)
        all_traits = self.apply_chain_reactions(all_traits, met_thresholds)
        
        # Generate trait string
        trait_str = "TRAITS{"
        trait_parts = []
        for trait, (prev, intens) in all_traits.items():
            trait_parts.append(f"{trait.split('.')[1]}:{prev}{intens}")
        trait_str += ";".join(trait_parts) + "}"
        dna_parts.append(trait_str)
        
        # Generate threshold string if any met
        if met_thresholds:
            thresh_str = "THRESH{" + ";".join(met_thresholds) + "}"
            dna_parts.append(thresh_str)
        
        # Identify trends and evolution patterns
        trends = self.identify_trends(all_traits)
        evolution_patterns = self.identify_evolution_patterns(all_traits, trends)
        
        # Calculate significant evolutions
        significant_evolutions = {}
        for trait, pattern in evolution_patterns.items():
            if pattern in ["ACCELERATING", "DECLINING"]:  # Focus on major changes
                evolution = self.calculate_evolution(
                    all_traits[trait], pattern, len(self.time_periods)-1
                )
                significant_evolutions[trait] = evolution
        
        # Add evolution to DNA string
        if significant_evolutions:
            evo_str = "EVO{"
            evo_parts = []
            for trait, evolution in significant_evolutions.items():
                # Format: trait:pattern[past,present,near,far]
                evo_values = [f"{prev}{intens}" for prev, intens in evolution]
                evo_parts.append(
                    f"{trait.split('.')[1]}:{evolution_patterns[trait]}"
                    f"[{','.join(evo_values)}]"
                )
            evo_str += ";".join(evo_parts) + "}"
            dna_parts.append(evo_str)
        
        return " ".join(dna_parts)
    
    def to_simple_traits(self, advanced_dna: str) -> Dict[str, str]:
        """
        Convert an advanced DNA string to a simplified traits dictionary
        for compatibility with the original WorldDNA class.
        
        Args:
            advanced_dna: Advanced DNA string generated by WorldDNAGenerator
            
        Returns:
            Dictionary of simplified traits compatible with WorldDNA
        """
        # Parse advanced DNA
        trait_section = ""
        if "TRAITS{" in advanced_dna:
            trait_section = advanced_dna.split("TRAITS{")[1].split("}")[0]
        
        if not trait_section:
            return {}
        
        # Extract traits
        traits_dict = {}
        for trait_part in trait_section.split(";"):
            if ":" in trait_part:
                name, value = trait_part.split(":")
                # In advanced DNA, value has prevalence and intensity (e.g., "93")
                # We'll use the name to map to a simplified value
                
                # Only map traits that are compatible with WorldDNA
                if name in ["climate", "terrain", "resources", "hazards", "conflict"]:
                    traits_dict[name] = self._map_to_simplified_value(name, value)
        
        # Ensure all required components from WorldDNA.COMPONENTS are present
        # Add default values for any missing components
        required_components = ["climate", "terrain", "resources", "conflict", "hazards"]
        for component in required_components:
            if component not in traits_dict:
                traits_dict[component] = self._get_default_value(component)
        
        return traits_dict
    
    def _map_to_simplified_value(self, trait_name: str, value: str) -> str:
        """Map advanced trait values to simplified ones."""
        # Extract prevalence from combined value (e.g., "93")
        prevalence = int(value[0]) if len(value) >= 1 and value[0].isdigit() else 5
        intensity = int(value[1]) if len(value) >= 2 and value[1].isdigit() else 3
        
        # Map to WorldDNA component values based on simplified thresholds
        if trait_name == "terrain":
            terrains = ["mountains", "forests", "plains", "desert", "arctic", "coastal", 
                       "islands", "jungle", "swamp", "underground", "mixed"]
            return terrains[prevalence % len(terrains)]
            
        elif trait_name == "climate":
            climates = ["tropical", "arid", "temperate", "cold", "arctic", "varied"]
            return climates[prevalence % len(climates)]
            
        elif trait_name == "resources":
            if prevalence >= 7:
                return "abundant"
            elif prevalence >= 4:
                return "balanced"
            else:
                return "scarce"
                
        elif trait_name == "conflict":
            if prevalence >= 7 and intensity >= 4:
                return "open_war"
            elif prevalence >= 5:
                return "skirmishes"
            elif prevalence >= 3:
                return "cold_war"
            else:
                return "peace"
                
        elif trait_name == "hazards":
            if prevalence >= 7:
                return "deadly"
            elif prevalence >= 4:
                return "dangerous"
            else:
                return "safe"
        
        # For other traits, we'll just return a default value
        return "balanced"
    
    def _get_default_value(self, component: str) -> str:
        """Get a default value for a component."""
        if component == "terrain":
            return "mixed"
        elif component == "climate":
            return "temperate"
        elif component == "resources":
            return "balanced"
        elif component == "conflict":
            return "peace"
        elif component == "hazards":
            return "safe"
        else:
            return "balanced"


class WorldDNA:
    """
    The WorldDNA class generates and interprets DNA strings for world creation.
    
    World DNA encodes fundamental aspects of a setting including geography, climate,
    political systems, technology level, magic prevalence, major conflicts, and cultural aspects.
    """
    
    # World DNA components and their possible values
    COMPONENTS = {
        # Geography and physical environment
        "terrain": ["mountains", "forests", "plains", "desert", "arctic", "coastal", "islands", 
                   "jungle", "swamp", "underground", "mixed"],
        "climate": ["tropical", "arid", "temperate", "cold", "arctic", "varied"],
        "resources": ["abundant", "balanced", "scarce", "depleted", "contested"],
        "hazards": ["safe", "dangerous", "deadly"],
        
        # Society and politics
        "government": ["monarchy", "democracy", "oligarchy", "republic", "theocracy", "anarchy",
                      "feudal", "tribal", "empire", "dictatorship", "federation"],
        "stability": ["stable", "unstable", "recovering", "declining", "fractured", "chaotic"],
        "factions": ["united", "competing", "hostile", "hidden", "numerous", "rare"],
        
        # Technology and magic
        "tech_level": ["primitive", "medieval", "renaissance", "industrial", "modern", 
                      "futuristic", "post-apocalyptic", "varied"],
        "magic": ["abundant", "common", "restricted", "rare", "forgotten", "forbidden", "none"],
        "supernatural": ["integral", "common", "hidden", "rare", "feared", "worshipped", "none"],
        
        # Conflict and danger
        "conflict": ["peace", "cold_war", "skirmishes", "open_war", "recovery", "ancient_grudges"],
        "threats": ["monsters", "invaders", "natural", "political", "supernatural", "internal", "minimal"],
        "danger_level": ["safe", "moderate", "dangerous", "deadly", "apocalyptic"],
        
        # Culture and society
        "culture_type": ["unified", "diverse", "segregated", "hierarchical", "tribal", "cosmopolitan"],
        "values": ["honor", "wealth", "knowledge", "tradition", "progress", "harmony", "power", "faith"],
        "openness": ["xenophobic", "cautious", "diplomatic", "welcoming", "integrated"],
        
        # Distinctive features
        "special_features": ["ancient_ruins", "magical_anomalies", "unique_ecosystems", "lost_technology",
                           "prophecies", "artifacts_of_power", "planar_connections", "divine_presence",
                           "hidden_societies", "mysterious_phenomena", "none"]
    }
    
    def __init__(self, dna_string: Optional[str] = None):
        """
        Initialize a WorldDNA instance.
        
        Args:
            dna_string: Optional DNA string to load. If not provided, a new random DNA will be generated.
        """
        if dna_string:
            self.dna_string = dna_string
            self.traits = self._decode_dna(dna_string)
        else:
            self.traits = self._generate_random_traits()
            self.dna_string = self._encode_dna(self.traits)
        
        logger.info(f"WorldDNA initialized: {self.dna_string[:30]}...")
    
    def _generate_random_traits(self) -> Dict[str, str]:
        """
        Generate random traits for world creation.
        
        Returns:
            Dictionary of traits with random values selected from COMPONENTS.
        """
        traits = {}
        for component, values in self.COMPONENTS.items():
            traits[component] = random.choice(values)
        return traits
    
    def _encode_dna(self, traits: Dict[str, str]) -> str:
        """
        Encode traits into a DNA string.
        
        Args:
            traits: Dictionary of component/value pairs to encode.
            
        Returns:
            DNA string representation.
        """
        components = []
        for component, value in traits.items():
            # Find index of value in the component's possible values
            value_index = self.COMPONENTS[component].index(value)
            # Convert to two-character hex
            hex_val = format(value_index, '02x')
            components.append(hex_val)
        
        # Join all hex values into a single string
        return ''.join(components)
    
    def _decode_dna(self, dna_string: str) -> Dict[str, str]:
        """
        Decode a DNA string into trait components.
        
        Args:
            dna_string: The DNA string to decode.
            
        Returns:
            Dictionary of decoded traits.
        """
        traits = {}
        component_keys = list(self.COMPONENTS.keys())
        
        # Ensure DNA string has correct length
        expected_length = len(component_keys) * 2  # 2 chars per component
        if len(dna_string) != expected_length:
            logger.warning(f"DNA string length mismatch: expected {expected_length}, got {len(dna_string)}")
            # Pad or truncate as needed
            dna_string = dna_string.ljust(expected_length, '0')[:expected_length]
        
        # Extract 2-character chunks
        chunks = [dna_string[i:i+2] for i in range(0, len(dna_string), 2)]
        
        # Convert each chunk to a trait value
        for i, component in enumerate(component_keys):
            if i < len(chunks):
                # Convert hex to index
                try:
                    index = int(chunks[i], 16)
                    # Get value at that index, or the first value if index is out of range
                    possible_values = self.COMPONENTS[component]
                    value = possible_values[index % len(possible_values)]
                    traits[component] = value
                except ValueError:
                    # Fallback if hex conversion fails
                    traits[component] = self.COMPONENTS[component][0]
            else:
                # Fallback for missing chunks
                traits[component] = self.COMPONENTS[component][0]
        
        return traits
    
    def mutate(self, mutation_rate: float = 0.2) -> 'WorldDNA':
        """
        Create a mutation of this DNA with some traits randomly changed.
        
        Args:
            mutation_rate: Probability (0-1) of each trait mutating.
            
        Returns:
            A new WorldDNA instance with mutations.
        """
        mutated_traits = self.traits.copy()
        
        for component in mutated_traits:
            if random.random() < mutation_rate:
                # Choose a different value than the current one
                current = mutated_traits[component]
                options = [v for v in self.COMPONENTS[component] if v != current]
                if options:
                    mutated_traits[component] = random.choice(options)
        
        mutated_dna = self._encode_dna(mutated_traits)
        return WorldDNA(mutated_dna)
    
    def crossover(self, other: 'WorldDNA') -> 'WorldDNA':
        """
        Create a new DNA by combining traits from this DNA and another.
        
        Args:
            other: Another WorldDNA instance to combine with.
            
        Returns:
            A new WorldDNA instance with mixed traits.
        """
        child_traits = {}
        
        for component in self.traits:
            # 50% chance of inheriting from each parent
            if random.random() < 0.5:
                child_traits[component] = self.traits[component]
            else:
                child_traits[component] = other.traits[component]
        
        child_dna = self._encode_dna(child_traits)
        return WorldDNA(child_dna)
    
    def to_prompt(self) -> str:
        """
        Convert DNA traits into a natural language prompt for the World Builder agent.
        
        Returns:
            A detailed textual description of the world.
        """
        # Build a detailed description based on traits
        descriptions = []
        
        # Geography and environment
        geography_desc = f"The world features predominantly {self.traits['terrain']} terrain "
        geography_desc += f"with a {self.traits['climate']} climate. "
        geography_desc += f"Natural resources are {self.traits['resources']}. "
        geography_desc += f"The environment poses {self.traits['hazards']} hazards."
        descriptions.append(geography_desc)
        
        # Society and politics
        society_desc = f"The dominant form of government is {self.traits['government']}, "
        society_desc += f"and the political landscape is {self.traits['stability']}. "
        society_desc += f"Various factions within society are {self.traits['factions']}."
        descriptions.append(society_desc)
        
        # Technology and magic
        tech_magic_desc = f"The civilization has reached a {self.traits['tech_level']} level of technology. "
        tech_magic_desc += f"Magic is {self.traits['magic']} throughout the world. "
        tech_magic_desc += f"Supernatural elements are {self.traits['supernatural']} to everyday life."
        descriptions.append(tech_magic_desc)
        
        # Conflict and danger
        conflict_desc = f"The world exists in a state of {self.traits['conflict']}. "
        conflict_desc += f"The primary threats are {self.traits['threats']}, "
        conflict_desc += f"making most areas {self.traits['danger_level']}."
        descriptions.append(conflict_desc)
        
        # Culture and society
        culture_desc = f"The culture is largely {self.traits['culture_type']}, "
        culture_desc += f"with a strong emphasis on {self.traits['values']}. "
        culture_desc += f"Toward outsiders, the society is generally {self.traits['openness']}."
        descriptions.append(culture_desc)
        
        # Special features
        if self.traits['special_features'] != "none":
            special_desc = f"A distinctive feature of this world is the presence of {self.traits['special_features']}."
            descriptions.append(special_desc)
        
        # Join all descriptions into a coherent prompt
        prompt = "\n\n".join(descriptions)
        
        return prompt
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DNA to a dictionary representation.
        
        Returns:
            A dictionary with DNA string and decoded traits.
        """
        return {
            "dna_string": self.dna_string,
            "traits": self.traits
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldDNA':
        """
        Create a WorldDNA instance from a dictionary.
        
        Args:
            data: Dictionary containing a DNA string.
            
        Returns:
            A new WorldDNA instance.
        """
        dna_string = data.get("dna_string")
        if not dna_string:
            logger.warning("No DNA string provided in dictionary, generating random DNA")
            return cls()
        return cls(dna_string)
    
    def save(self, filepath: Union[str, Path]) -> bool:
        """
        Save the DNA to a JSON file.
        
        Args:
            filepath: Path where the DNA should be saved.
            
        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            data = self.to_dict()
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved WorldDNA to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving WorldDNA: {e}")
            return False
    
    @classmethod
    def load(cls, filepath: Union[str, Path]) -> Optional['WorldDNA']:
        """
        Load a DNA from a JSON file.
        
        Args:
            filepath: Path to the DNA file.
            
        Returns:
            A WorldDNA instance or None if loading failed.
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded WorldDNA from {filepath}")
            return cls.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading WorldDNA: {e}")
            return None
    
    @classmethod
    def from_advanced_dna(cls, advanced_dna: str) -> 'WorldDNA':
        """
        Create a WorldDNA instance from an advanced DNA string generated by WorldDNAGenerator.
        
        Args:
            advanced_dna: Advanced DNA string.
            
        Returns:
            A new WorldDNA instance.
        """
        generator = WorldDNAGenerator()
        simplified_traits = generator.to_simple_traits(advanced_dna)
        
        # Create a new instance with simplified traits
        instance = cls()
        instance.traits = simplified_traits
        instance.dna_string = instance._encode_dna(simplified_traits)
        
        return instance
    
    def generate_advanced_dna(self, bias: Optional[Dict] = None) -> str:
        """
        Generate an advanced DNA string using the WorldDNAGenerator.
        
        Args:
            bias: Optional bias to apply to trait generation.
            
        Returns:
            Advanced DNA string.
        """
        generator = WorldDNAGenerator()
        return generator.generate_dna(bias)


class NPCPersonalityDNA:
    """
    The NPCPersonalityDNA class generates and interprets DNA strings for NPC personality creation.
    
    NPC Personality DNA encodes fundamental personality traits, motivations, flaws, quirks, and other
    characteristics that shape how an NPC behaves and interacts with players.
    """
    
    # NPC Personality DNA components and their possible values
    COMPONENTS = {
        # Core personality traits (Inspired by Big Five personality traits)
        "extraversion": ["highly_extraverted", "moderately_extraverted", "neutral", "moderately_introverted", "highly_introverted"],
        "openness": ["very_open", "somewhat_open", "balanced", "somewhat_traditional", "very_traditional"],
        "conscientiousness": ["highly_conscientious", "somewhat_conscientious", "balanced", "somewhat_careless", "very_careless"],
        "agreeableness": ["very_agreeable", "somewhat_agreeable", "neutral", "somewhat_disagreeable", "very_disagreeable"],
        "neuroticism": ["very_neurotic", "somewhat_neurotic", "emotionally_stable", "resilient", "extremely_resilient"],
        
        # Moral alignment (simplified D&D-style)
        "morality": ["lawful_good", "neutral_good", "chaotic_good", "lawful_neutral", "true_neutral", 
                   "chaotic_neutral", "lawful_evil", "neutral_evil", "chaotic_evil"],
        
        # Motivations and drives
        "primary_motivation": ["power", "wealth", "knowledge", "fame", "revenge", "love", "duty", "freedom", 
                             "survival", "pleasure", "ideology", "curiosity", "faith"],
        "secondary_motivation": ["power", "wealth", "knowledge", "fame", "revenge", "love", "duty", "freedom", 
                               "survival", "pleasure", "ideology", "curiosity", "faith", "none"],
        "ambition_level": ["obsessive", "highly_ambitious", "moderately_ambitious", "content", "unambitious"],
        
        # Social traits
        "social_status": ["outcast", "low", "average", "respected", "elite", "legendary"],
        "loyalty": ["blindly_loyal", "generally_loyal", "conditional", "self_serving", "treacherous"],
        "humor": ["none", "dry", "sarcastic", "silly", "dark", "witty", "self_deprecating"],
        "confidence": ["extremely_insecure", "somewhat_insecure", "average", "confident", "overconfident"],
        
        # Flaws and quirks
        "major_flaw": ["arrogance", "greed", "cowardice", "paranoia", "naivety", "jealousy", "addiction", 
                     "dishonesty", "wrath", "prejudice", "obsession", "stubbornness", "indecisiveness", "none"],
        "minor_quirk": ["talks_to_self", "uses_big_words", "fidgets", "always_hungry", "collects_trinkets", 
                      "afraid_of_something_common", "laughs_inappropriately", "formal_speech", "constant_jokes", 
                      "specific_ritual", "whistles_tunes", "refers_to_self_in_third_person", "none"],
        
        # Speech and communication
        "speech_complexity": ["very_simple", "straightforward", "average", "eloquent", "elaborate"],
        "truthfulness": ["pathological_liar", "deceptive", "avoids_direct_lies", "honest", "brutally_honest"],
        "talkativeness": ["silent", "taciturn", "average", "talkative", "extremely_talkative"],
        
        # Intellect and knowledge
        "intelligence": ["very_low", "below_average", "average", "above_average", "exceptional", "genius"],
        "education": ["none", "rudimentary", "average", "well_educated", "expert", "scholarly"],
        "wisdom": ["foolish", "naive", "average_wisdom", "wise", "sage_like"],
        
        # Relationships
        "default_attitude": ["hostile", "suspicious", "cautious", "neutral", "friendly", "helpful"],
        "attachment_style": ["avoidant", "anxious", "secure", "dismissive", "fearful"],
        
        # Combat and conflict
        "bravery": ["cowardly", "cautious", "average", "brave", "reckless"],
        "combat_style": ["avoids_all_combat", "defensive", "balanced", "aggressive", "berserker", "tactical", "dirty_fighter"],
        
        # Hidden depth
        "secret": ["none", "hidden_identity", "dark_past", "secret_knowledge", "hidden_agenda", "hidden_power", 
                 "forbidden_relationship", "criminal_history", "traumatic_experience", "prophecy", "conspiracy"],
        "depth_trait": ["exactly_as_appears", "more_complex", "facade_hiding_opposite", "troubled_past", "secret_agenda", "none"]
    }
    
    def __init__(self, dna_string: Optional[str] = None):
        """
        Initialize an NPCPersonalityDNA instance.
        
        Args:
            dna_string: Optional DNA string to load. If not provided, a new random DNA will be generated.
        """
        if dna_string:
            self.dna_string = dna_string
            self.traits = self._decode_dna(dna_string)
        else:
            self.traits = self._generate_random_traits()
            self.dna_string = self._encode_dna(self.traits)
        
        logger.info(f"NPCPersonalityDNA initialized: {self.dna_string[:30]}...")
    
    def _generate_random_traits(self) -> Dict[str, str]:
        """
        Generate random traits for NPC personality creation.
        
        Returns:
            Dictionary of traits with random values selected from COMPONENTS.
        """
        traits = {}
        for component, values in self.COMPONENTS.items():
            traits[component] = random.choice(values)
        
        # Ensure secondary motivation isn't the same as primary
        if traits["secondary_motivation"] == traits["primary_motivation"]:
            traits["secondary_motivation"] = "none"
        
        return traits
    
    def _encode_dna(self, traits: Dict[str, str]) -> str:
        """
        Encode traits into a DNA string.
        
        Args:
            traits: Dictionary of component/value pairs to encode.
            
        Returns:
            DNA string representation.
        """
        components = []
        for component, value in traits.items():
            # Find index of value in the component's possible values
            value_index = self.COMPONENTS[component].index(value)
            # Convert to two-character hex
            hex_val = format(value_index, '02x')
            components.append(hex_val)
        
        # Join all hex values into a single string
        return ''.join(components)
    
    def _decode_dna(self, dna_string: str) -> Dict[str, str]:
        """
        Decode a DNA string into trait components.
        
        Args:
            dna_string: The DNA string to decode.
            
        Returns:
            Dictionary of decoded traits.
        """
        traits = {}
        component_keys = list(self.COMPONENTS.keys())
        
        # Ensure DNA string has correct length
        expected_length = len(component_keys) * 2  # 2 chars per component
        if len(dna_string) != expected_length:
            logger.warning(f"DNA string length mismatch: expected {expected_length}, got {len(dna_string)}")
            # Pad or truncate as needed
            dna_string = dna_string.ljust(expected_length, '0')[:expected_length]
        
        # Extract 2-character chunks
        chunks = [dna_string[i:i+2] for i in range(0, len(dna_string), 2)]
        
        # Convert each chunk to a trait value
        for i, component in enumerate(component_keys):
            if i < len(chunks):
                # Convert hex to index
                try:
                    index = int(chunks[i], 16)
                    # Get value at that index, or the first value if index is out of range
                    possible_values = self.COMPONENTS[component]
                    value = possible_values[index % len(possible_values)]
                    traits[component] = value
                except ValueError:
                    # Fallback if hex conversion fails
                    traits[component] = self.COMPONENTS[component][0]
            else:
                # Fallback for missing chunks
                traits[component] = self.COMPONENTS[component][0]
        
        return traits
    
    def mutate(self, mutation_rate: float = 0.2) -> 'NPCPersonalityDNA':
        """
        Create a mutation of this DNA with some traits randomly changed.
        
        Args:
            mutation_rate: Probability (0-1) of each trait mutating.
            
        Returns:
            A new NPCPersonalityDNA instance with mutations.
        """
        mutated_traits = self.traits.copy()
        
        for component in mutated_traits:
            if random.random() < mutation_rate:
                # Choose a different value than the current one
                current = mutated_traits[component]
                options = [v for v in self.COMPONENTS[component] if v != current]
                if options:
                    mutated_traits[component] = random.choice(options)
        
        # Ensure secondary motivation isn't the same as primary
        if mutated_traits["secondary_motivation"] == mutated_traits["primary_motivation"]:
            mutated_traits["secondary_motivation"] = "none"
        
        mutated_dna = self._encode_dna(mutated_traits)
        return NPCPersonalityDNA(mutated_dna)
    
    def crossover(self, other: 'NPCPersonalityDNA') -> 'NPCPersonalityDNA':
        """
        Create a new DNA by combining traits from this DNA and another.
        
        Args:
            other: Another NPCPersonalityDNA instance to combine with.
            
        Returns:
            A new NPCPersonalityDNA instance with mixed traits.
        """
        child_traits = {}
        
        for component in self.traits:
            # 50% chance of inheriting from each parent
            if random.random() < 0.5:
                child_traits[component] = self.traits[component]
            else:
                child_traits[component] = other.traits[component]
        
        # Ensure secondary motivation isn't the same as primary
        if child_traits["secondary_motivation"] == child_traits["primary_motivation"]:
            child_traits["secondary_motivation"] = "none"
        
        child_dna = self._encode_dna(child_traits)
        return NPCPersonalityDNA(child_dna)
    
    def to_prompt(self) -> str:
        """
        Convert DNA traits into a natural language prompt for the NPC Manager agent.
        
        Returns:
            A detailed textual description of the NPC's personality.
        """
        # Build a detailed description based on traits
        descriptions = []
        
        # Core personality
        personality_desc = f"This character is {self.traits['extraversion']}, {self.traits['openness']} to new experiences, "
        personality_desc += f"{self.traits['conscientiousness']} in their approach to tasks, {self.traits['agreeableness']} "
        personality_desc += f"toward others, and {self.traits['neuroticism']} emotionally."
        descriptions.append(personality_desc)
        
        # Moral alignment
        alignment_desc = f"Their moral alignment is {self.traits['morality'].replace('_', ' ')}."
        descriptions.append(alignment_desc)
        
        # Motivations
        motivation_desc = f"They are primarily motivated by {self.traits['primary_motivation']}"
        if self.traits['secondary_motivation'] != "none":
            motivation_desc += f" and secondarily by {self.traits['secondary_motivation']}"
        motivation_desc += f". Their ambition level can be described as {self.traits['ambition_level']}."
        descriptions.append(motivation_desc)
        
        # Social traits
        social_desc = f"They hold {self.traits['social_status']} social status and are {self.traits['loyalty']} "
        social_desc += f"to their allies. They have a {self.traits['humor']} sense of humor and are {self.traits['confidence']} "
        social_desc += f"in their abilities and decisions."
        descriptions.append(social_desc)
        
        # Flaws and quirks
        flaws_desc = ""
        if self.traits['major_flaw'] != "none":
            flaws_desc += f"Their major character flaw is {self.traits['major_flaw']}. "
        if self.traits['minor_quirk'] != "none":
            flaws_desc += f"They have a quirky habit where they {self.traits['minor_quirk'].replace('_', ' ')}."
        if flaws_desc:
            descriptions.append(flaws_desc)
        
        # Speech and communication
        speech_desc = f"Their speech is {self.traits['speech_complexity']} and generally {self.traits['truthfulness']}. "
        speech_desc += f"They tend to be {self.traits['talkativeness']} in conversation."
        descriptions.append(speech_desc)
        
        # Intellect and knowledge
        intellect_desc = f"They possess {self.traits['intelligence']} intelligence with {self.traits['education']} education "
        intellect_desc += f"and {self.traits['wisdom']} wisdom."
        descriptions.append(intellect_desc)
        
        # Relationships and attitude
        relationship_desc = f"Their default attitude toward strangers is {self.traits['default_attitude']}. "
        relationship_desc += f"In relationships, they exhibit a {self.traits['attachment_style']} attachment style."
        descriptions.append(relationship_desc)
        
        # Combat approach
        combat_desc = f"In dangerous situations, they are {self.traits['bravery']} and favor a {self.traits['combat_style']} "
        combat_desc += f"approach to conflict."
        descriptions.append(combat_desc)
        
        # Hidden depth
        depth_desc = ""
        if self.traits['secret'] != "none":
            depth_desc += f"They harbor a secret involving {self.traits['secret'].replace('_', ' ')}. "
        if self.traits['depth_trait'] != "none" and self.traits['depth_trait'] != "exactly_as_appears":
            depth_desc += f"There is more depth to this character - they are {self.traits['depth_trait'].replace('_', ' ')}."
        if depth_desc:
            descriptions.append(depth_desc)
        
        # Join all descriptions into a coherent prompt
        prompt = "\n\n".join(descriptions)
        
        return prompt
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DNA to a dictionary representation.
        
        Returns:
            A dictionary with DNA string and decoded traits.
        """
        return {
            "dna_string": self.dna_string,
            "traits": self.traits
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NPCPersonalityDNA':
        """
        Create an NPCPersonalityDNA instance from a dictionary.
        
        Args:
            data: Dictionary containing a DNA string.
            
        Returns:
            A new NPCPersonalityDNA instance.
        """
        dna_string = data.get("dna_string")
        if not dna_string:
            logger.warning("No DNA string provided in dictionary, generating random DNA")
            return cls()
        return cls(dna_string)
    
    def save(self, filepath: Union[str, Path]) -> bool:
        """
        Save the DNA to a JSON file.
        
        Args:
            filepath: Path where the DNA should be saved.
            
        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            data = self.to_dict()
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved NPCPersonalityDNA to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving NPCPersonalityDNA: {e}")
            return False
    
    @classmethod
    def load(cls, filepath: Union[str, Path]) -> Optional['NPCPersonalityDNA']:
        """
        Load a DNA from a JSON file.
        
        Args:
            filepath: Path to the DNA file.
            
        Returns:
            An NPCPersonalityDNA instance or None if loading failed.
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded NPCPersonalityDNA from {filepath}")
            return cls.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading NPCPersonalityDNA: {e}")
            return None
    
    def generate_name(self, race: str = "human", gender: Optional[str] = None) -> str:
        """
        Generate a name that fits the NPC's personality traits.
        
        Args:
            race: The race of the NPC (e.g., human, elf, dwarf).
            gender: Optional gender to influence name generation.
            
        Returns:
            A generated name.
        """
        # This is a simplified implementation. In a real system, this would use
        # more sophisticated name generation based on race, culture, and personality.
        
        # Example simple implementation:
        prefixes = {
            "human": ["Al", "Ber", "Car", "Dav", "El", "Fre", "Gar", "Han", "Is", "Jor"],
            "elf": ["Aer", "Bael", "Cael", "Dae", "Eld", "Fae", "Gael", "Hae", "Iel", "Jae"],
            "dwarf": ["Bor", "Dur", "Gar", "Gim", "Kil", "Mor", "Nor", "Tho", "Thro", "Val"],
            "orc": ["Drak", "Gorn", "Gruk", "Krag", "Morg", "Nar", "Rak", "Thog", "Urg", "Zog"]
        }
        
        suffixes = {
            "human": ["an", "en", "id", "on", "us", "in", "ar", "or", "er", "el"],
            "elf": ["ion", "ian", "iel", "ien", "il", "is", "ith", "iël", "ias", "ira"],
            "dwarf": ["in", "ur", "or", "ar", "im", "om", "ek", "ak", "il", "ul"],
            "orc": ["ash", "ug", "og", "arg", "org", "ul", "uk", "nak", "gak", "mar"]
        }
        
        # Default to human if race not found
        race = race.lower()
        race_prefixes = prefixes.get(race, prefixes["human"])
        race_suffixes = suffixes.get(race, suffixes["human"])
        
        # Personality influences name choice
        if self.traits["morality"].startswith("evil"):
            # Evil characters get harsher sounding names
            race_prefixes = [p for p in race_prefixes if any(c in p for c in "kgrzx")]
            if not race_prefixes:  # Fallback if filtering removed all options
                race_prefixes = prefixes.get(race, prefixes["human"])
        
        if self.traits["extraversion"] == "highly_extraverted":
            # Extroverted characters get longer names
            suffix = random.choice(race_suffixes) + random.choice(race_suffixes)
        else:
            suffix = random.choice(race_suffixes)
            
        prefix = random.choice(race_prefixes)
        
        name = prefix + suffix
        # Capitalize first letter
        return name[0].upper() + name[1:].lower()
