"""
Test script for NPC generation with the advanced personality decoder.

This script demonstrates how to use the NPCManagerAgent to generate
NPCs with consistent personalities using the advanced DNA decoder.
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.primary.npc_manager import NPCManagerAgent
from core.dna_generator import NPCPersonalityDNA

async def test_basic_npc_generation():
    """Test basic NPC generation with the agent."""
    print("\n=== Testing Basic NPC Generation ===\n")
    
    # Create NPC manager agent
    npc_manager = NPCManagerAgent()
    
    # Generate a simple NPC with random DNA
    npc_name = "Gareth Ironforge"
    race = "dwarf"
    gender = "male"
    
    # This will use a random DNA and the advanced decoder
    description = await npc_manager.generate_npc_description_with_dna(npc_name, race, gender)
    
    print(f"Generated NPC: {npc_name}")
    print(f"Description: {description}")
    print("\nStored NPC data:")
    print(json.dumps(npc_manager.npcs[npc_name], indent=2, default=str))

async def test_custom_dna_npc_generation():
    """Test NPC generation with custom DNA."""
    print("\n=== Testing NPC Generation with Custom DNA ===\n")
    
    # Create NPC manager agent
    npc_manager = NPCManagerAgent()
    
    # Create a specific NPC personality DNA
    custom_dna = "(3/8) 2B5,8R1,3L4,2F5,9S2,8P3,3D4,7G1,2Y3,9E4,4N2,8K3,3Z5,2O1,4C3,5R2,8A4,3D5,2A1,9I3 - H2,C9,K3,G8,L2,J3,M1,F2,E2,B3,U9,S2,I2,R7,T3,A8,D2,V9,Y4,X7"
    npc_dna = NPCPersonalityDNA(custom_dna)
    
    # Generate NPC with our custom DNA
    npc_name = "Elaria Nightshade"
    race = "elf"
    gender = "female"
    
    # This will use our custom DNA and the advanced decoder
    description = await npc_manager.generate_npc_description_with_dna(npc_name, race, gender, npc_dna)
    
    print(f"Generated NPC with custom DNA: {npc_name}")
    print(f"Custom DNA: {custom_dna}")
    print(f"Description: {description}")

async def test_location_npcs():
    """Test generating multiple NPCs for a location."""
    print("\n=== Testing Location NPCs ===\n")
    
    # Create NPC manager agent
    npc_manager = NPCManagerAgent()
    
    # Generate NPCs for a location
    location_name = "The Rusty Tankard Tavern"
    npcs = await npc_manager.generate_npcs_for_location(location_name, count=3)
    
    print(f"Generated {len(npcs)} NPCs for {location_name}:")
    for i, npc in enumerate(npcs, 1):
        print(f"\n{i}. {npc['name']} ({npc['race']} {npc['gender']})")
        print(f"   {npc['description'][:200]}...")

async def main():
    """Run all tests."""
    print("=== NPC Generation with Advanced Decoder Test ===\n")
    
    # Make sure storage directories exist
    Path("storage/npc_descriptions").mkdir(parents=True, exist_ok=True)
    
    # Run tests
    await test_basic_npc_generation()
    await test_custom_dna_npc_generation()
    await test_location_npcs()
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    asyncio.run(main())
