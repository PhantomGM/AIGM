"""
Test script for the World DNA Decoder

This script demonstrates how to use the WorldDNADecoder class to interpret
advanced DNA strings and generate rich world descriptions.
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dna_generator import WorldDNA, WorldDNAGenerator
from core.dna_decoder import WorldDNADecoder

async def test_basic_decoding():
    """Test basic DNA decoding without additional context."""
    print("\n=== Testing Basic DNA Decoding ===\n")
    
    # Create DNA generator and generate advanced DNA
    generator = WorldDNAGenerator()
    dna_string = generator.generate_dna()
    
    print(f"Generated DNA: {dna_string}\n")
    
    # Create decoder and decode DNA
    decoder = WorldDNADecoder()
    formatted_dna = decoder.format_dna_for_decoding(dna_string)
    
    print("=== Formatted DNA ===")
    print(f"Version: {formatted_dna['version']}")
    print("\nTraits:")
    for trait, data in formatted_dna['traits'].items():
        print(f"  {trait}: prevalence={data['prevalence']}, intensity={data['intensity']}")
    
    print("\nThresholds Met:")
    for threshold in formatted_dna['thresholds']:
        print(f"  {threshold}")
    
    print("\nEvolution Patterns:")
    for trait, evo_data in formatted_dna['evolution'].items():
        print(f"  {trait}: {evo_data['pattern']}")
        if 'time_periods' in evo_data:
            for period, value in evo_data['time_periods'].items():
                print(f"    {period}: {value}")
    
    # Save the decoder prompt
    prompt = decoder.decode_dna(dna_string)
    save_path = decoder.save_world_description("test_world_prompt", prompt)
    
    print(f"\nDecoder prompt saved to: {save_path}")
    print("(This prompt would be sent to an LLM in a production environment)")

async def test_decoding_with_context():
    """Test DNA decoding with additional context."""
    print("\n=== Testing DNA Decoding with Context ===\n")
    
    # Create DNA generator with specific biases
    generator = WorldDNAGenerator()
    bias = {
        "technology": (8, 4),  # High technology prevalence and intensity
        "magic": (7, 5),       # High magic prevalence and very high intensity
        "conflict": (7, 4)     # High conflict prevalence and intensity
    }
    dna_string = generator.generate_dna(bias)
    
    print(f"Generated DNA with bias: {dna_string}\n")
    
    # Create decoder and decode DNA with context
    decoder = WorldDNADecoder()
    additional_context = """
We want a steampunk world with magical elements where technology and magic are in conflict.
The world should have the following elements:
1. A central kingdom with advanced steam technology
2. Outlying regions with strong magical traditions
3. Rising tensions between technologists and magic users
4. Recent discoveries of ancient artifacts that blend magic and technology
"""
    
    prompt = decoder.decode_dna(dna_string, additional_context)
    save_path = decoder.save_world_description("steampunk_world_prompt", prompt)
    
    print(f"Additional context provided: {additional_context}\n")
    print(f"Decoder prompt with context saved to: {save_path}")
    print("(This prompt would be sent to an LLM in a production environment)")

async def test_full_workflow():
    """Test the full workflow from DNA generation to decoding."""
    print("\n=== Testing Full DNA Generation and Decoding Workflow ===\n")
    
    # Step 1: Generate advanced DNA
    generator = WorldDNAGenerator()
    dna_string = generator.generate_dna()
    
    # Step 2: Create a compatible world using simplified DNA
    world_dna = WorldDNA.from_advanced_dna(dna_string)
    
    # Step 3: Decode the advanced DNA
    decoder = WorldDNADecoder()
    prompt = decoder.decode_dna(dna_string)
    
    # Step 4: Save outputs
    world_name = "Example World"
    save_path = decoder.save_world_description(f"{world_name}_prompt", prompt)
    
    print(f"Generated DNA: {dna_string}")
    print(f"Simplified DNA: {world_dna.dna_string}")
    print(f"World DNA Traits: {world_dna.traits}")
    print(f"\nDecoder prompt saved to: {save_path}")
    print("(In a production environment, this prompt would be sent to an LLM to generate a complete world description)")

async def main():
    """Run all tests."""
    print("=== World DNA Decoder Test ===\n")
    
    # Make sure storage directory exists
    Path("storage/world_descriptions").mkdir(parents=True, exist_ok=True)
    
    # Run tests
    await test_basic_decoding()
    await test_decoding_with_context()
    await test_full_workflow()
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    asyncio.run(main())
