"""
DNA Generation System Tester

This script demonstrates the DNA-based generation features for worlds and NPCs.
It tests the creation, mutation, crossover, and saving/loading of DNA.
"""

import os
import sys
import random
import asyncio
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from core.dna_generator import WorldDNA, NPCPersonalityDNA
from agents.primary.world_builder import WorldBuilderAgent
from agents.primary.npc_manager import NPCManagerAgent

async def test_world_dna():
    """Test world DNA generation functionality."""
    print("\n===== TESTING WORLD DNA =====")
    
    # Initialize world builder agent
    world_builder = WorldBuilderAgent()
    
    # Generate a random world DNA
    random_dna = WorldDNA()
    print(f"Random World DNA: {random_dna.dna_string[:20]}...")
    print("Traits:")
    for trait, value in random_dna.traits.items():
        print(f"  {trait}: {value}")
    
    # Generate a world with this DNA
    world_info = await world_builder.generate_world_with_dna("Mysteria", random_dna.dna_string)
    print(f"\nGenerated World: Mysteria")
    print(f"Description: {world_info.get('description', '')[:200]}...")
    
    # Mutate the DNA
    mutated_dna = random_dna.mutate(0.3)
    print(f"\nMutated DNA: {mutated_dna.dna_string[:20]}...")
    print("Changed traits:")
    for trait in random_dna.traits:
        if random_dna.traits[trait] != mutated_dna.traits[trait]:
            print(f"  {trait}: {random_dna.traits[trait]} -> {mutated_dna.traits[trait]}")
    
    # Create another random DNA for crossover
    another_dna = WorldDNA()
    print(f"\nSecond Random DNA: {another_dna.dna_string[:20]}...")
    
    # Perform crossover
    child_dna = random_dna.crossover(another_dna)
    print(f"Crossover DNA: {child_dna.dna_string[:20]}...")
    
    # Save and load DNA
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    dna_path = test_dir / "test_world.dna.json"
    child_dna.save(dna_path)
    print(f"\nSaved DNA to {dna_path}")
    
    loaded_dna = WorldDNA.load(dna_path)
    if loaded_dna:
        print(f"Successfully loaded DNA: {loaded_dna.dna_string[:20]}...")
        assert loaded_dna.dna_string == child_dna.dna_string, "Loaded DNA doesn't match saved DNA"
    
    return child_dna

async def test_npc_dna():
    """Test NPC personality DNA generation functionality."""
    print("\n===== TESTING NPC DNA =====")
    
    # Initialize NPC manager agent
    npc_manager = NPCManagerAgent()
    
    # Generate a random NPC DNA
    random_npc_dna = NPCPersonalityDNA()
    print(f"Random NPC DNA: {random_npc_dna.dna_string[:20]}...")
    print("Key Traits:")
    key_traits = ["extraversion", "morality", "primary_motivation", "intelligence", "major_flaw"]
    for trait in key_traits:
        print(f"  {trait}: {random_npc_dna.traits[trait]}")
    
    # Generate a name based on personality
    npc_name = random_npc_dna.generate_name("elf")
    print(f"\nGenerated Name for Elf: {npc_name}")
    
    # Generate NPC description with DNA
    description = await npc_manager.generate_npc_description_with_dna(
        npc_name, "elf", "female", random_npc_dna
    )
    print(f"Description: {description[:200]}...")
    
    # Mutate the DNA
    mutated_npc_dna = random_npc_dna.mutate(0.2)
    print(f"\nMutated NPC DNA: {mutated_npc_dna.dna_string[:20]}...")
    print("Changed traits:")
    for trait in key_traits:
        if random_npc_dna.traits[trait] != mutated_npc_dna.traits[trait]:
            print(f"  {trait}: {random_npc_dna.traits[trait]} -> {mutated_npc_dna.traits[trait]}")
    
    # Create another random DNA for crossover
    second_npc_dna = NPCPersonalityDNA()
    second_name = second_npc_dna.generate_name("dwarf")
    print(f"\nSecond NPC: {second_name}")
    print(f"Second DNA: {second_npc_dna.dna_string[:20]}...")
    
    # Perform crossover
    child_npc_dna = random_npc_dna.crossover(second_npc_dna)
    child_name = child_npc_dna.generate_name("half-elf")
    print(f"Child NPC: {child_name}")
    print(f"Child DNA: {child_npc_dna.dna_string[:20]}...")
    print("Inherited traits:")
    for trait in key_traits:
        parent = "First" if child_npc_dna.traits[trait] == random_npc_dna.traits[trait] else "Second"
        print(f"  {trait}: {child_npc_dna.traits[trait]} (from {parent})")
    
    # Save and load DNA
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    npc_dna_path = test_dir / f"{child_name.lower()}.dna.json"
    child_npc_dna.save(npc_dna_path)
    print(f"\nSaved NPC DNA to {npc_dna_path}")
    
    loaded_npc_dna = NPCPersonalityDNA.load(npc_dna_path)
    if loaded_npc_dna:
        print(f"Successfully loaded NPC DNA: {loaded_npc_dna.dna_string[:20]}...")
        assert loaded_npc_dna.dna_string == child_npc_dna.dna_string, "Loaded DNA doesn't match saved DNA"
    
    # Test personality evolution
    events = [
        "Witnessed the destruction of their hometown",
        "Lost a loved one in a tragic accident",
        "Discovered a powerful magical artifact"
    ]
    
    evolution_data = await npc_manager.evolve_npc_personality(child_name, events, 0.3)
    print(f"\nEvolved personality based on significant life events:")
    print(f"Analysis: {evolution_data.get('changes_analysis', '')[:200]}...")
    
    return child_npc_dna

async def main():
    """Run the DNA generation system tests."""
    print("DNA GENERATION SYSTEM TESTER")
    print("============================")
    
    # Test world DNA
    world_dna = await test_world_dna()
    
    # Test NPC DNA 
    npc_dna = await test_npc_dna()
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
