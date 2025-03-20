#!/usr/bin/env python
"""
Test script for the advanced DNA generation and evolution system.

This script demonstrates the functionality of the WorldDNAGenerator class,
including trait generation, evolution patterns, and chain reactions.
"""
import sys
import os
import asyncio
import json
from pathlib import Path

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dna_generator import WorldDNA, WorldDNAGenerator
from agents.primary.world_builder import WorldBuilderAgent


async def test_advanced_dna_generation():
    """Test basic DNA generation with the advanced generator."""
    print("\n=== Testing Basic Advanced DNA Generation ===")
    generator = WorldDNAGenerator()
    dna = generator.generate_dna()
    print(f"Generated DNA: {dna}")
    
    # Parse and display DNA components
    print("\n--- DNA Breakdown ---")
    
    # Version
    if dna.startswith("V"):
        version = dna.split(" ")[0][1:]
        print(f"Version: {version}")
    
    # Traits
    if "TRAITS{" in dna:
        traits_section = dna.split("TRAITS{")[1].split("}")[0]
        print("\nTraits:")
        for trait_part in traits_section.split(";"):
            if ":" in trait_part:
                name, value = trait_part.split(":")
                prevalence = value[0] if len(value) >= 1 else "?"
                intensity = value[1] if len(value) >= 2 else "?"
                print(f"  {name}: Prevalence={prevalence}, Intensity={intensity}")
    
    # Thresholds
    if "THRESH{" in dna:
        thresh_section = dna.split("THRESH{")[1].split("}")[0]
        print("\nThresholds Met:")
        for threshold in thresh_section.split(";"):
            print(f"  {threshold}")
    
    # Evolution
    if "EVO{" in dna:
        evo_section = dna.split("EVO{")[1].split("}")[0]
        print("\nEvolution Patterns:")
        for evo_part in evo_section.split(";"):
            if ":" in evo_part and "[" in evo_part:
                trait, pattern_values = evo_part.split(":", 1)
                pattern = pattern_values.split("[")[0]
                values = pattern_values.split("[")[1].split("]")[0]
                print(f"  {trait}: Pattern={pattern}")
                print(f"    Values (PAST,PRESENT,NEAR,FAR): {values}")


async def test_biased_generation():
    """Test DNA generation with biases applied."""
    print("\n=== Testing Biased DNA Generation ===")
    generator = WorldDNAGenerator()
    
    # Create bias for high magic and technology
    bias = {
        "magical.intensity": (2, 2),  # Add 2 to prevalence and 2 to intensity
        "cultural.technology": (3, 1)  # Add 3 to prevalence and 1 to intensity
    }
    
    dna = generator.generate_dna(bias)
    print(f"Generated DNA with bias: {dna}")
    
    # Check if thresholds are met due to bias
    if "THRESH{" in dna:
        thresh_section = dna.split("THRESH{")[1].split("}")[0]
        print("\nThresholds Met:")
        for threshold in thresh_section.split(";"):
            print(f"  {threshold}")
    else:
        print("\nNo thresholds met despite bias.")


async def test_world_generation_with_advanced_dna():
    """Test generating a world description with the advanced DNA."""
    print("\n=== Testing World Generation with Advanced DNA ===")
    generator = WorldDNAGenerator()
    
    # Generate DNA for a magical world
    bias = {
        "magical.intensity": (3, 2),
        "magical.prevalence": (3, 0),
        "terrain.prevalence": (2, 1)
    }
    
    advanced_dna = generator.generate_dna(bias)
    print(f"Advanced DNA: {advanced_dna}")
    
    # Convert to classic DNA format for compatibility
    world_dna = WorldDNA.from_advanced_dna(advanced_dna)
    print(f"Simplified DNA: {world_dna.dna_string}")
    print(f"Traits: {json.dumps(world_dna.traits, indent=2)}")
    
    # Generate a world description
    world_builder = WorldBuilderAgent()
    world_data = await world_builder.generate_world_with_dna("Arcania", world_dna.dna_string)
    
    print("\nGenerated World:")
    print(f"Name: Arcania")
    print(f"Description: {world_data.get('description', 'No description generated')}")


async def test_dna_evolution():
    """Test the evolution of world DNA over time."""
    print("\n=== Testing DNA Evolution Over Time ===")
    generator = WorldDNAGenerator()
    
    # Generate initial DNA
    original_dna = generator.generate_dna()
    
    # Parse evolution patterns
    evolution_info = {}
    if "EVO{" in original_dna:
        evo_section = original_dna.split("EVO{")[1].split("}")[0]
        for evo_part in evo_section.split(";"):
            if ":" in evo_part and "[" in evo_part:
                trait, pattern_values = evo_part.split(":", 1)
                pattern = pattern_values.split("[")[0]
                values_str = pattern_values.split("[")[1].split("]")[0]
                values = values_str.split(",")
                
                evolution_info[trait] = {
                    "pattern": pattern,
                    "values": values
                }
    
    # If we have evolution patterns, simulate evolution
    if evolution_info:
        print("\nOriginal DNA: " + original_dna)
        
        # Extract and print traits section
        original_traits_section = ""
        if "TRAITS{" in original_dna:
            original_traits_section = original_dna.split("TRAITS{")[1].split("}")[0]
            print("\nOriginal Traits:")
            for trait_part in original_traits_section.split(";"):
                if ":" in trait_part:
                    print(f"  {trait_part}")
        
        # Simulate evolution by 1 time period
        print("\nEvolving by 1 time period...")
        
        # Create evolved traits
        evolved_traits_parts = []
        for trait_part in original_traits_section.split(";"):
            if ":" in trait_part:
                trait_name, value = trait_part.split(":")
                
                if trait_name in evolution_info:
                    evo_data = evolution_info[trait_name]
                    values = evo_data["values"]
                    
                    # Move from PRESENT (index 1) to NEAR (index 2)
                    if len(values) > 2:
                        evolved_value = values[2]  # NEAR future
                        evolved_traits_parts.append(f"{trait_name}:{evolved_value}")
                        print(f"  {trait_name}: {value} -> {evolved_value} ({evo_data['pattern']})")
                    else:
                        evolved_traits_parts.append(trait_part)
                else:
                    evolved_traits_parts.append(trait_part)
        
        # Create evolved DNA
        evolved_traits_section = ";".join(evolved_traits_parts)
        evolved_dna = original_dna.replace(
            f"TRAITS{{{original_traits_section}}}", 
            f"TRAITS{{{evolved_traits_section}}}"
        )
        
        print("\nEvolved DNA: " + evolved_dna)
        
        # Generate world descriptions
        world_builder = WorldBuilderAgent()
        
        # Original world
        original_world_dna = WorldDNA.from_advanced_dna(original_dna)
        original_world = await world_builder.generate_world_with_dna(
            "Original World", original_world_dna.dna_string
        )
        
        # Evolved world
        evolved_world_dna = WorldDNA.from_advanced_dna(evolved_dna)
        evolved_world = await world_builder.generate_world_with_dna(
            "Evolved World", evolved_world_dna.dna_string
        )
        
        print("\nOriginal World Description:")
        print(original_world.get("description", "No description generated"))
        
        print("\nEvolved World Description:")
        print(evolved_world.get("description", "No description generated"))
    else:
        print("No evolution patterns found in the generated DNA. Try running the test again.")


async def main():
    """Run all tests sequentially."""
    print("=== Advanced DNA Generation System Test ===")
    
    await test_advanced_dna_generation()
    await test_biased_generation()
    await test_world_generation_with_advanced_dna()
    await test_dna_evolution()
    
    print("\n=== All tests completed ===")


if __name__ == "__main__":
    asyncio.run(main())
