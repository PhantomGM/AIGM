"""
Web Server Module

This module implements the FastAPI web server for the AI Game Master system,
providing REST API endpoints for player input and game state updates.
"""

import logging
import json
import os
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import random
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks, Body
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import game state manager
from core.game_state import GameState
from core.system_manager import SystemManager
from core.dna_generator import WorldDNA, NPCPersonalityDNA, WorldDNAGenerator
from agents.primary.world_builder import WorldBuilderAgent
from agents.primary.npc_manager import NPCManagerAgent
from core.dna_decoder import WorldDNADecoder
from core.npc_decoder import NPCPersonalityDecoder

app = FastAPI(title="AI Game Master API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up static file serving and templates
templates_path = Path("ui/web/templates")
static_path = Path("ui/web/static")

if templates_path.exists():
    templates = Jinja2Templates(directory=str(templates_path))
else:
    logging.warning(f"Templates directory not found at {templates_path}")
    templates = None

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
else:
    logging.warning(f"Static files directory not found at {static_path}")

# Initialize game state and system manager
game_state = GameState()
system_manager = SystemManager()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Active WebSocket connections
active_connections: List[WebSocket] = []

# Request and response models
class PlayerInput(BaseModel):
    content: str
    character_id: Optional[str] = None

class GameMasterResponse(BaseModel):
    content: str
    tokens: int

class CharacterData(BaseModel):
    name: str
    race: str
    character_class: str = ""
    level: int = 1
    id: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface."""
    if templates:
        return templates.TemplateResponse("index.html", {"request": {}})
    else:
        return HTMLResponse(content="<html><body><h1>AI Game Master</h1><p>Web interface not available.</p></body></html>")

@app.post("/api/input", response_model=GameMasterResponse)
async def process_input(player_input: PlayerInput):
    """
    Process player input and return AI Game Master response.
    
    Args:
        player_input: The player's input message and optional character ID
        
    Returns:
        AI Game Master response with content and token count
    """
    try:
        # Log the input
        logger.info(f"Received player input: {player_input.content}")
        
        # TODO: Process the input through AI agents
        # For now, return a simple response
        response_content = f"You said: {player_input.content}"
        
        # Update all connected clients with the new message
        await broadcast_message("gm_message", {"content": response_content})
        
        return GameMasterResponse(content=response_content, tokens=len(response_content.split()))
    
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/character")
async def add_character(character: CharacterData):
    """
    Add a new character to the game.
    
    Args:
        character: Character data including name, race, class, and level
        
    Returns:
        The character data with assigned ID
    """
    try:
        # Generate ID if not provided
        if not character.id:
            character.id = f"char_{int(time.time())}"
        
        # Create character data for game state
        character_data = {
            "name": character.name,
            "race": character.race,
            "class": character.character_class,
            "level": character.level
        }
        
        # Add to game state
        game_state.add_active_character(character.id, character_data)
        
        # Update all connected clients
        await broadcast_state_update()
        
        return character
    
    except Exception as e:
        logger.error(f"Error adding character: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/state")
async def get_game_state():
    """
    Get the current game state.
    
    Returns:
        Current game state context
    """
    try:
        return game_state.to_context_dict()
    
    except Exception as e:
        logger.error(f"Error retrieving game state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save")
async def save_game(filename: Optional[str] = None):
    """
    Save the current game state to a file.
    
    Args:
        filename: Optional filename to save to
        
    Returns:
        Path to the saved file
    """
    try:
        saved_path = game_state.save_to_file(filename)
        return {"status": "success", "file": saved_path}
    
    except Exception as e:
        logger.error(f"Error saving game: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/load")
async def load_game(filename: str):
    """
    Load a game state from a file.
    
    Args:
        filename: Path to the game state file
        
    Returns:
        Status of the load operation
    """
    try:
        success = game_state.load_from_file(filename)
        
        if success:
            # Update all connected clients
            await broadcast_state_update()
            return {"status": "success"}
        else:
            return {"status": "error", "message": "Failed to load game"}
    
    except Exception as e:
        logger.error(f"Error loading game: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system")
async def change_system(system_id: str):
    """
    Change the active game system.
    
    Args:
        system_id: ID of the game system to switch to
        
    Returns:
        Status of the system change operation
    """
    try:
        success = game_state.change_system(system_id)
        
        if success:
            system = game_state.system
            await broadcast_message("system_change", {
                "success": True,
                "id": system_id,
                "name": system.name,
                "version": system.version
            })
            
            # Update all clients with new state
            await broadcast_state_update()
            
            return {"status": "success", "system": system_id}
        else:
            await broadcast_message("system_change", {
                "success": False,
                "error": f"System '{system_id}' not found"
            })
            return {"status": "error", "message": f"System '{system_id}' not found"}
    
    except Exception as e:
        logger.error(f"Error changing system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rules")
async def get_rules(system_id: Optional[str] = None, rule_id: Optional[str] = None):
    """
    Get rules for the specified game system.
    
    Args:
        system_id: Optional system ID (defaults to active system)
        rule_id: Optional specific rule ID to retrieve
        
    Returns:
        Rules data for the requested system/rule
    """
    try:
        # Use current system if not specified
        if not system_id:
            system_id = game_state.system_id
        
        # Temporarily select system if different from current
        current_system = game_state.system_id
        temp_change = (system_id != current_system)
        
        if temp_change:
            system_manager.select_system(system_id)
            system = system_manager.get_active_system()
        else:
            system = game_state.system
        
        if not system:
            return {"error": f"System '{system_id}' not found"}
        
        # Get specific rule or all rules
        if rule_id:
            rule_data = system.get_rule(rule_id)
            result = {"rule": rule_data} if rule_data else {"error": f"Rule '{rule_id}' not found"}
        else:
            # Load basic rules
            rules_path = Path(f"systems/{system_id}/rules/basic_rules.json")
            if rules_path.exists():
                with open(rules_path, "r", encoding="utf-8") as f:
                    rules_data = json.load(f)
                result = rules_data
            else:
                result = {"name": system.name, "sections": []}
        
        # Restore original system if we temporarily changed it
        if temp_change:
            system_manager.select_system(current_system)
        
        return result
    
    except Exception as e:
        logger.error(f"Error retrieving rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/session_summary")
async def add_session_summary(summary: Dict[str, Any]):
    """
    Add a session summary to the game state.
    
    Args:
        summary: Dictionary with at least "title" and "content" keys
        
    Returns:
        Status of the operation
    """
    try:
        if "title" not in summary or "content" not in summary:
            raise ValueError("Summary must include 'title' and 'content'")
        
        game_state.add_session_summary(summary)
        
        # Update clients with new summaries
        await broadcast_message("session_summaries", {
            "summaries": game_state.get_session_summaries()
        })
        
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Error adding session summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session_summaries")
async def get_session_summaries(count: Optional[int] = None):
    """
    Get session summaries from the game state.
    
    Args:
        count: Optional number of most recent summaries to retrieve
        
    Returns:
        List of session summaries
    """
    try:
        summaries = game_state.get_session_summaries(count)
        return {"summaries": summaries}
    
    except Exception as e:
        logger.error(f"Error retrieving session summaries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge")
async def get_knowledge_base(category: Optional[str] = None, key: Optional[str] = None):
    """
    Get entries from the knowledge base.
    
    Args:
        category: Optional category to filter by
        key: Optional specific key to retrieve from the category
        
    Returns:
        Knowledge base entries matching the criteria
    """
    try:
        # If key is specified, category is required
        if key and not category:
            raise HTTPException(status_code=400, detail="Category is required when querying by key")
        
        # Get specific entry
        if category and key:
            entry = game_state.get_knowledge_entry(category, key)
            if not entry:
                raise HTTPException(status_code=404, detail=f"Entry {key} not found in category {category}")
            return {"category": category, "key": key, "data": entry}
        
        # Get all entries in a category
        if category:
            if category not in game_state.knowledge_base:
                raise HTTPException(status_code=404, detail=f"Category {category} not found")
            return {
                "category": category, 
                "entries": game_state.knowledge_base[category]
            }
        
        # Get summary of all categories
        result = {}
        for cat, entries in game_state.knowledge_base.items():
            result[cat] = {
                "count": len(entries),
                "keys": list(entries.keys())
            }
        
        return {"categories": result}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/knowledge")
async def add_knowledge_entry(category: str, key: str, data: Dict[str, Any]):
    """
    Add or update an entry in the knowledge base.
    
    Args:
        category: The category to add to
        key: The key for the entry
        data: The data to store
        
    Returns:
        Status of the operation
    """
    try:
        # Validate category
        if category not in game_state.knowledge_base:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        # Ensure key is not empty
        if not key:
            raise HTTPException(status_code=400, detail="Key cannot be empty")
        
        # Add the entry
        success = game_state.add_knowledge_entry(category, key, data)
        
        if success:
            # Notify all connected clients about the update
            await broadcast_message("knowledge_update", {
                "category": category,
                "key": key,
                "action": "add_or_update"
            })
            
            return {"status": "success", "category": category, "key": key}
        else:
            raise HTTPException(status_code=500, detail="Failed to add knowledge entry")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding knowledge entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/knowledge/{category}/{key}")
async def delete_knowledge_entry(category: str, key: str):
    """
    Delete an entry from the knowledge base.
    
    Args:
        category: The category containing the entry
        key: The key of the entry to delete
        
    Returns:
        Status of the operation
    """
    try:
        # Validate category
        if category not in game_state.knowledge_base:
            raise HTTPException(status_code=404, detail=f"Category {category} not found")
        
        # Check if entry exists
        if key not in game_state.knowledge_base[category]:
            raise HTTPException(status_code=404, detail=f"Entry {key} not found in category {category}")
        
        # Delete the entry
        del game_state.knowledge_base[category][key]
        
        # Save the knowledge base
        game_state._save_knowledge_base()
        
        # Notify all connected clients about the update
        await broadcast_message("knowledge_update", {
            "category": category,
            "key": key,
            "action": "delete"
        })
        
        return {"status": "success", "message": f"Deleted entry {key} from category {category}"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge/search")
async def search_knowledge_base(query: str, category: Optional[str] = None):
    """
    Search the knowledge base for entries matching the query.
    
    Args:
        query: The search query string
        category: Optional category to limit the search
        
    Returns:
        List of matching entries
    """
    try:
        # Perform the search
        results = game_state.search_knowledge_base(query, category)
        
        return {"query": query, "category": category, "results": results, "count": len(results)}
    
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_summary")
async def generate_session_summary():
    """
    Generate an automatic session summary based on current game state.
    
    Returns:
        The generated summary
    """
    try:
        # Generate the summary
        summary = game_state.generate_session_summary()
        
        # Add it to the game state
        game_state.add_session_summary(summary)
        
        # Notify clients
        await broadcast_message("session_summaries", {
            "summaries": game_state.get_session_summaries()
        })
        
        return {"status": "success", "summary": summary}
    
    except Exception as e:
        logger.error(f"Error generating session summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/multimodal_settings")
async def update_multimodal_settings(settings: Dict[str, bool]):
    """
    Update multimodal interaction settings.
    
    Args:
        settings: Dictionary of settings to update
        
    Returns:
        Updated settings
    """
    try:
        # Update the settings
        game_state.update_multimodal_settings(settings)
        
        # Notify clients
        await broadcast_message("settings_update", {
            "multimodal_settings": game_state.multimodal_settings
        })
        
        return {"status": "success", "settings": game_state.multimodal_settings}
    
    except Exception as e:
        logger.error(f"Error updating multimodal settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dna/world")
async def get_world_dna(world_name: Optional[str] = None):
    """
    Get the DNA of a world, either the current active one or a specific one by name.
    
    Args:
        world_name: Optional name of the world to get DNA for.
        
    Returns:
        The world DNA data.
    """
    try:
        world_builder = system_manager.get_agent("world_builder")
        
        # If world_name provided, try to load that specific DNA
        if world_name:
            success = world_builder.load_world_dna(world_name)
            if not success:
                raise HTTPException(status_code=404, detail=f"World DNA not found for '{world_name}'")
        
        # If no DNA is loaded at this point, generate a new random one
        if not world_builder.world_dna:
            world_builder.world_dna = WorldDNA()
            world_builder.world_traits = world_builder.world_dna.traits
        
        # Return the DNA information
        return {
            "dna_string": world_builder.world_dna.dna_string,
            "traits": world_builder.world_dna.traits,
            "prompt": world_builder.world_dna.to_prompt()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving world DNA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dna/world/generate")
async def generate_world_with_dna(world_name: str, dna_string: Optional[str] = None):
    """
    Generate a new world using DNA technology.
    
    Args:
        world_name: Name of the world to generate.
        dna_string: Optional DNA string. If not provided, a random one is generated.
        
    Returns:
        The generated world information.
    """
    try:
        if not world_name:
            raise HTTPException(status_code=400, detail="World name is required")
        
        # Get the world builder agent
        world_builder = system_manager.get_agent("world_builder")
        
        # Generate the world
        world_info = world_builder.generate_world_with_dna(world_name, dna_string)
        
        # Update game state with new world information
        game_state.world_name = world_name
        game_state.world_description = world_info.get("description", "")
        
        # Add to knowledge base
        game_state.add_knowledge_entry("locations", world_name, {
            "type": "world",
            "description": world_info.get("description", ""),
            "dna": world_info.get("dna", ""),
            "traits": world_builder.world_traits
        })
        
        # Add generated locations to the knowledge base
        for loc_name, loc_data in world_info.get("locations", {}).items():
            game_state.add_knowledge_entry("locations", loc_name, loc_data)
        
        # Notify clients about the new world
        await broadcast_message("world_created", {
            "world_name": world_name,
            "summary": world_info
        })
        
        return world_info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating world with DNA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dna/world/mutate")
async def mutate_world_dna(mutation_rate: float = 0.2):
    """
    Mutate the current world DNA to create variations.
    
    Args:
        mutation_rate: Probability (0-1) of each trait mutating.
        
    Returns:
        Information about the mutation.
    """
    try:
        if mutation_rate < 0 or mutation_rate > 1:
            raise HTTPException(status_code=400, detail="Mutation rate must be between 0 and 1")
        
        # Get the world builder agent
        world_builder = system_manager.get_agent("world_builder")
        
        # Perform mutation
        mutation_info = world_builder.mutate_world_dna(mutation_rate)
        
        # Notify clients
        await broadcast_message("world_dna_updated", {
            "action": "mutate",
            "dna": mutation_info.get("dna", ""),
            "changes": mutation_info.get("changes", [])
        })
        
        return mutation_info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error mutating world DNA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dna/world/crossover")
async def crossover_world_dna(other_dna_string: str):
    """
    Create a new world DNA by combining the current DNA with another.
    
    Args:
        other_dna_string: The other DNA string to combine with.
        
    Returns:
        Information about the new DNA.
    """
    try:
        # Validate DNA string
        if not other_dna_string:
            raise HTTPException(status_code=400, detail="Other DNA string is required")
        
        # Get the world builder agent
        world_builder = system_manager.get_agent("world_builder")
        
        # Perform crossover
        crossover_info = world_builder.crossover_world_dna(other_dna_string)
        
        # Notify clients
        await broadcast_message("world_dna_updated", {
            "action": "crossover",
            "dna": crossover_info.get("dna", ""),
            "traits": crossover_info.get("traits", {})
        })
        
        return crossover_info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing DNA crossover: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dna/world/random")
async def generate_random_world_dna():
    """
    Generate a random world DNA string.
    
    Returns:
        Random DNA information.
    """
    try:
        # Create a new random DNA
        random_dna = WorldDNA()
        
        return {
            "dna_string": random_dna.dna_string,
            "traits": random_dna.traits,
            "prompt": random_dna.to_prompt()
        }
    
    except Exception as e:
        logger.error(f"Error generating random world DNA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dna/npc")
async def get_npc_dna(npc_name: Optional[str] = None):
    """
    Get the DNA of an NPC, either the current active one or a specific one by name.
    
    Args:
        npc_name: Optional name of the NPC to get DNA for.
        
    Returns:
        The NPC personality DNA data.
    """
    try:
        # Get the NPC manager agent
        npc_manager = system_manager.get_agent("npc_manager")
        
        # If a specific NPC is requested, try to load its DNA
        if npc_name:
            # Retrieve the NPC data from the knowledge base
            npc_data = game_state.get_knowledge_entry("npcs", npc_name)
            if not npc_data or "dna" not in npc_data:
                raise HTTPException(status_code=404, detail=f"NPC DNA not found for '{npc_name}'")
            
            # Create DNA from the stored string
            npc_dna = NPCPersonalityDNA(npc_data["dna"])
        else:
            # If no NPC specified, generate a new random DNA
            npc_dna = NPCPersonalityDNA()
        
        # Return the DNA information
        return {
            "name": npc_name,
            "dna_string": npc_dna.dna_string,
            "traits": npc_dna.traits,
            "prompt": npc_dna.to_prompt()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving NPC DNA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dna/npc/generate")
async def generate_npc_with_dna(
    npc_name: str, 
    race: str = "human", 
    gender: Optional[str] = None, 
    dna_string: Optional[str] = None
):
    """
    Generate a new NPC using DNA technology.
    
    Args:
        npc_name: Name of the NPC to generate, or "auto" to auto-generate a name.
        race: Race of the NPC (e.g., human, elf, dwarf).
        gender: Optional gender of the NPC.
        dna_string: Optional DNA string. If not provided, a random one is generated.
        
    Returns:
        The generated NPC information.
    """
    try:
        # Validate inputs
        if not npc_name:
            raise HTTPException(status_code=400, detail="NPC name or 'auto' is required")
        
        # Get the NPC manager agent
        npc_manager = system_manager.get_agent("npc_manager")
        
        # Create DNA object
        if dna_string:
            npc_dna = NPCPersonalityDNA(dna_string)
        else:
            npc_dna = NPCPersonalityDNA()
        
        # Auto-generate name if requested
        auto_generated_name = False
        if npc_name.lower() == "auto":
            npc_name = npc_dna.generate_name(race, gender)
            auto_generated_name = True
        
        # Generate NPC description based on DNA
        npc_description = await npc_manager.generate_npc_description_with_dna(
            npc_name, race, gender, npc_dna
        )
        
        # Create NPC data structure
        npc_data = {
            "name": npc_name,
            "race": race,
            "gender": gender or "unknown",
            "description": npc_description,
            "dna": npc_dna.dna_string,
            "traits": npc_dna.traits,
            "auto_generated_name": auto_generated_name
        }
        
        # Add to knowledge base
        game_state.add_knowledge_entry("npcs", npc_name, npc_data)
        
        # Notify clients
        await broadcast_message("npc_created", {
            "npc_name": npc_name,
            "summary": npc_data
        })
        
        return npc_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating NPC with DNA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dna/npc/mutate")
async def mutate_npc_dna(npc_name: str, mutation_rate: float = 0.2):
    """
    Mutate an existing NPC's DNA to create a variation.
    
    Args:
        npc_name: Name of the NPC to mutate.
        mutation_rate: Probability (0-1) of each trait mutating.
        
    Returns:
        Information about the mutated NPC.
    """
    try:
        # Validate inputs
        if not npc_name:
            raise HTTPException(status_code=400, detail="NPC name is required")
        
        if mutation_rate < 0 or mutation_rate > 1:
            raise HTTPException(status_code=400, detail="Mutation rate must be between 0 and 1")
        
        # Get existing NPC data
        npc_data = game_state.get_knowledge_entry("npcs", npc_name)
        if not npc_data or "dna" not in npc_data:
            raise HTTPException(status_code=404, detail=f"NPC '{npc_name}' not found or has no DNA")
        
        # Get the NPC manager agent
        npc_manager = system_manager.get_agent("npc_manager")
        
        # Create DNA from stored string and mutate it
        original_dna = NPCPersonalityDNA(npc_data["dna"])
        mutated_dna = original_dna.mutate(mutation_rate)
        
        # Generate new description based on mutated DNA
        race = npc_data.get("race", "human")
        gender = npc_data.get("gender", None)
        
        mutated_description = await npc_manager.generate_npc_description_with_dna(
            npc_name, race, gender, mutated_dna
        )
        
        # Create mutation data
        mutation_data = {
            "name": npc_name,
            "race": race,
            "gender": gender,
            "original_dna": original_dna.dna_string,
            "mutated_dna": mutated_dna.dna_string,
            "original_traits": original_dna.traits,
            "mutated_traits": mutated_dna.traits,
            "original_description": npc_data.get("description", ""),
            "mutated_description": mutated_description,
            "changed_traits": [
                trait for trait in mutated_dna.traits 
                if trait in original_dna.traits and mutated_dna.traits[trait] != original_dna.traits[trait]
            ]
        }
        
        # Update knowledge base with the mutated version (optional, can be switched with the original)
        npc_data.update({
            "description": mutated_description,
            "dna": mutated_dna.dna_string,
            "traits": mutated_dna.traits,
            "mutated_from": original_dna.dna_string
        })
        game_state.add_knowledge_entry("npcs", npc_name, npc_data)
        
        # Notify clients
        await broadcast_message("npc_dna_updated", {
            "npc_name": npc_name,
            "action": "mutate",
            "changes": mutation_data["changed_traits"]
        })
        
        return mutation_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error mutating NPC DNA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dna/npc/crossover")
async def crossover_npc_dna(npc1_name: str, npc2_name: str, child_name: Optional[str] = None):
    """
    Create a new NPC by combining the DNA of two existing NPCs.
    
    Args:
        npc1_name: Name of the first parent NPC.
        npc2_name: Name of the second parent NPC.
        child_name: Optional name for the child NPC. If not provided, one will be generated.
        
    Returns:
        Information about the new NPC.
    """
    try:
        # Validate inputs
        if not npc1_name or not npc2_name:
            raise HTTPException(status_code=400, detail="Both parent NPC names are required")
        
        # Get existing NPC data
        npc1_data = game_state.get_knowledge_entry("npcs", npc1_name)
        npc2_data = game_state.get_knowledge_entry("npcs", npc2_name)
        
        if not npc1_data or "dna" not in npc1_data:
            raise HTTPException(status_code=404, detail=f"NPC '{npc1_name}' not found or has no DNA")
        
        if not npc2_data or "dna" not in npc2_data:
            raise HTTPException(status_code=404, detail=f"NPC '{npc2_name}' not found or has no DNA")
        
        # Get the NPC manager agent
        npc_manager = system_manager.get_agent("npc_manager")
        
        # Create DNA objects
        npc1_dna = NPCPersonalityDNA(npc1_data["dna"])
        npc2_dna = NPCPersonalityDNA(npc2_data["dna"])
        
        # Perform crossover
        child_dna = npc1_dna.crossover(npc2_dna)
        
        # Determine race and gender for the child (simple inheritance for this example)
        race = random.choice([npc1_data.get("race", "human"), npc2_data.get("race", "human")])
        gender = random.choice([npc1_data.get("gender", "unknown"), npc2_data.get("gender", "unknown")])
        if gender == "unknown":
            gender = None
        
        # Generate or use provided name
        if not child_name:
            child_name = child_dna.generate_name(race, gender)
        
        # Generate description based on DNA
        child_description = await npc_manager.generate_npc_description_with_dna(
            child_name, race, gender, child_dna
        )
        
        # Create child NPC data
        child_data = {
            "name": child_name,
            "race": race,
            "gender": gender or "unknown",
            "description": child_description,
            "dna": child_dna.dna_string,
            "traits": child_dna.traits,
            "parents": [npc1_name, npc2_name],
            "parent1_dna": npc1_data["dna"],
            "parent2_dna": npc2_data["dna"]
        }
        
        # Add to knowledge base
        game_state.add_knowledge_entry("npcs", child_name, child_data)
        
        # Notify clients
        await broadcast_message("npc_created", {
            "npc_name": child_name,
            "summary": child_data,
            "crossover": {
                "parent1": npc1_name,
                "parent2": npc2_name
            }
        })
        
        return child_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing NPC DNA crossover: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dna/npc/random")
async def generate_random_npc_dna(race: str = "human", gender: Optional[str] = None):
    """
    Generate a random NPC DNA string with optional name.
    
    Args:
        race: Race of the NPC (e.g., human, elf, dwarf).
        gender: Optional gender to influence name generation.
    
    Returns:
        Random NPC DNA information.
    """
    try:
        # Create a new random DNA
        random_dna = NPCPersonalityDNA()
        
        # Generate a name
        name = random_dna.generate_name(race, gender)
        
        return {
            "name": name,
            "race": race,
            "gender": gender or "unknown",
            "dna_string": random_dna.dna_string,
            "traits": random_dna.traits,
            "prompt": random_dna.to_prompt()
        }
    
    except Exception as e:
        logger.error(f"Error generating random NPC DNA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/world_dna/{world_name}")
async def get_world_dna(world_name: str):
    """
    Get the DNA for a specific world.
    
    Args:
        world_name: Name of the world.
        
    Returns:
        The world's DNA string and decoded traits.
    """
    # In a real implementation, you would retrieve this from storage
    storage_path = Path(f"storage/world_dna/{world_name.lower().replace(' ', '_')}_dna.json")
    
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail=f"World DNA for '{world_name}' not found")
    
    try:
        with open(storage_path, 'r') as f:
            data = json.load(f)
        
        return {
            "name": world_name,
            "dna_string": data.get("dna_string", ""),
            "traits": data.get("traits", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving world DNA: {str(e)}")

@app.get("/api/world_dna/advanced/{world_name}")
async def get_advanced_world_dna(world_name: str):
    """
    Get the advanced DNA for a specific world.
    
    Args:
        world_name: Name of the world.
        
    Returns:
        The world's advanced DNA string with evolution patterns and thresholds.
    """
    # In a real implementation, you would retrieve this from storage
    storage_path = Path(f"storage/world_dna/advanced/{world_name.lower().replace(' ', '_')}_advanced_dna.json")
    
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail=f"Advanced World DNA for '{world_name}' not found")
    
    try:
        with open(storage_path, 'r') as f:
            data = json.load(f)
        
        return {
            "name": world_name,
            "dna_string": data.get("dna_string", ""),
            "traits": data.get("traits", {}),
            "evolution": data.get("evolution", {}),
            "thresholds": data.get("thresholds", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving advanced world DNA: {str(e)}")

@app.post("/api/world_dna/generate_advanced")
async def generate_advanced_world_dna(world_info: Dict[str, Any] = Body(...)):
    """
    Generate a new world using the advanced DNA generator.
    
    Args:
        world_info: Dictionary containing:
            - name: Name of the world to generate.
            - bias: Optional dictionary of trait biases.
            
    Returns:
        The generated world's DNA string, traits, and other details.
    """
    world_name = world_info.get("name", "")
    bias = world_info.get("bias", None)
    
    if not world_name:
        raise HTTPException(status_code=400, detail="World name is required")
    
    try:
        # Create a DNA generator and generate DNA
        generator = WorldDNAGenerator()
        dna_string = generator.generate_dna(bias)
        
        # Create a world with this DNA (simplified version for compatibility)
        world_dna = WorldDNA.from_advanced_dna(dna_string)
        
        # Initialize the world builder agent
        world_builder = WorldBuilderAgent()
        
        # Generate the world
        world_data = await world_builder.generate_world_with_dna(world_name, world_dna.dna_string)
        
        # Additional parsing for advanced DNA
        version = "1.0"
        thresholds = []
        evolution = {}
        
        if dna_string:
            # Extract version
            if dna_string.startswith("V"):
                version_part = dna_string.split(" ")[0]
                version = version_part[1:]
            
            # Extract thresholds
            if "THRESH{" in dna_string:
                thresh_part = dna_string.split("THRESH{")[1].split("}")[0]
                thresholds = thresh_part.split(";")
            
            # Extract evolution (simplified for API response)
            if "EVO{" in dna_string:
                evo_part = dna_string.split("EVO{")[1].split("}")[0]
                for evo_item in evo_part.split(";"):
                    if ":" in evo_item and "[" in evo_item and "]" in evo_item:
                        trait, pattern_values = evo_item.split(":", 1)
                        pattern = pattern_values.split("[")[0]
                        values = pattern_values.split("[")[1].split("]")[0]
                        evolution[trait] = {
                            "pattern": pattern,
                            "values": values.split(",")
                        }
        
        # Store advanced DNA for future retrieval
        storage_dir = Path("storage/world_dna/advanced")
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        advanced_data = {
            "name": world_name,
            "dna_string": dna_string,
            "version": version,
            "thresholds": thresholds,
            "evolution": evolution,
            "traits": world_data.get("dna_traits", {})
        }
        
        with open(storage_dir / f"{world_name.lower().replace(' ', '_')}_advanced_dna.json", 'w') as f:
            json.dump(advanced_data, f, indent=2)
        
        # Return the world data with advanced DNA information
        return {
            "name": world_name,
            "description": world_data.get("description", ""),
            "dna_string": dna_string,
            "simplified_dna": world_dna.dna_string,
            "traits": world_data.get("dna_traits", {}),
            "thresholds": thresholds,
            "evolution": evolution,
            "version": version
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advanced world: {str(e)}")

@app.post("/api/world_dna/evolve")
async def evolve_world_dna(evolution_data: Dict[str, Any] = Body(...)):
    """
    Evolve a world's DNA to a future time period.
    
    Args:
        evolution_data: Dictionary containing:
            - world_name: Name of the world to evolve.
            - time_periods: Number of time periods to evolve (default 1).
            - focus_traits: Optional list of traits to focus evolution on.
            
    Returns:
        The evolved world DNA and description.
    """
    world_name = evolution_data.get("world_name", "")
    time_periods = evolution_data.get("time_periods", 1)
    focus_traits = evolution_data.get("focus_traits", [])
    
    if not world_name:
        raise HTTPException(status_code=400, detail="World name is required")
    
    # Check if advanced DNA exists
    storage_path = Path(f"storage/world_dna/advanced/{world_name.lower().replace(' ', '_')}_advanced_dna.json")
    
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail=f"Advanced World DNA for '{world_name}' not found")
    
    try:
        # Load existing advanced DNA
        with open(storage_path, 'r') as f:
            data = json.load(f)
        
        original_dna = data.get("dna_string", "")
        
        # Parse the DNA to extract evolution information
        evolution_info = {}
        if "EVO{" in original_dna:
            evo_part = original_dna.split("EVO{")[1].split("}")[0]
            for evo_item in evo_part.split(";"):
                if ":" in evo_item and "[" in evo_item and "]" in evo_item:
                    trait, pattern_values = evo_item.split(":", 1)
                    pattern = pattern_values.split("[")[0]
                    values = pattern_values.split("[")[1].split("]")[0]
                    evolution_info[trait] = {
                        "pattern": pattern,
                        "values": values.split(",")
                    }
        
        # Extract traits section
        traits_section = ""
        if "TRAITS{" in original_dna:
            traits_section = original_dna.split("TRAITS{")[1].split("}")[0]
        
        # Create a modified traits section with evolved values
        if traits_section:
            traits_parts = traits_section.split(";")
            evolved_traits_parts = []
            
            for trait_part in traits_parts:
                if ":" in trait_part:
                    trait_name, value = trait_part.split(":")
                    
                    # Check if this trait has evolution info
                    if trait_name in evolution_info:
                        # Get the evolved value based on time periods
                        evo_data = evolution_info[trait_name]
                        values = evo_data["values"]
                        
                        # Calculate the index of the evolved value
                        # PAST, PRESENT, NEAR, FAR
                        # Start at PRESENT (index 1) and move forward
                        target_index = 1 + time_periods  # PRESENT + time_periods
                        
                        if target_index < len(values):
                            evolved_value = values[target_index]
                            evolved_traits_parts.append(f"{trait_name}:{evolved_value}")
                        else:
                            # If we're evolving beyond what's defined, use the last value
                            evolved_value = values[-1]
                            evolved_traits_parts.append(f"{trait_name}:{evolved_value}")
                    elif focus_traits and trait_name in focus_traits:
                        # Special handling for focused traits without defined evolution
                        # Implement your own logic here for how these should evolve
                        # For now, we'll just keep them unchanged
                        evolved_traits_parts.append(trait_part)
                    else:
                        # Keep unchanged for non-evolving traits
                        evolved_traits_parts.append(trait_part)
            
            # Create the new traits section
            evolved_traits_section = ";".join(evolved_traits_parts)
            
            # Replace the traits section in the DNA
            evolved_dna = original_dna.replace(f"TRAITS{{{traits_section}}}", f"TRAITS{{{evolved_traits_section}}}")
            
            # Create a world based on the evolved DNA
            world_dna = WorldDNA.from_advanced_dna(evolved_dna)
            
            # Generate a world description
            world_builder = WorldBuilderAgent()
            evolved_world = await world_builder.generate_world_with_dna(f"{world_name} (Evolved)", world_dna.dna_string)
            
            # Return the evolved world
            return {
                "original_name": world_name,
                "evolved_name": f"{world_name} (Evolved)",
                "description": evolved_world.get("description", ""),
                "evolved_dna": evolved_dna,
                "simplified_dna": world_dna.dna_string,
                "traits": evolved_world.get("dna_traits", {}),
                "time_periods": time_periods
            }
        else:
            raise HTTPException(status_code=400, detail="Could not parse traits from DNA")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evolving world: {str(e)}")

@app.get("/api/dna/decode")
async def decode_dna(dna_string: str):
    """
    Decode a DNA string into its traits and other information.
    
    Args:
        dna_string: The DNA string to decode.
        
    Returns:
        Decoded DNA information.
    """
    try:
        # Create a DNA decoder
        decoder = WorldDNADecoder()
        
        # Decode the DNA
        decoded_data = decoder.decode_dna(dna_string)
        
        return decoded_data
    
    except Exception as e:
        logger.error(f"Error decoding DNA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dna/decode_with_context")
async def decode_dna_with_context(request_data: Dict[str, Any] = Body(...)):
    """
    Decode a DNA string with additional context into a rich world description.
    
    Args:
        request_data: Dictionary containing:
            - dna_string: The DNA string to decode
            - world_name: Optional name of the world
            - additional_context: Optional additional context for the decoder
            
    Returns:
        The decoding prompt that can be sent to an LLM.
    """
    dna_string = request_data.get("dna_string", "")
    world_name = request_data.get("world_name", "Unnamed World")
    additional_context = request_data.get("additional_context", "")
    
    if not dna_string:
        raise HTTPException(status_code=400, detail="DNA string is required")
    
    try:
        # Create a DNA decoder
        decoder = WorldDNADecoder()
        
        # Decode the DNA with context
        decoded_prompt = decoder.decode_dna(dna_string, additional_context)
        
        # Save the prompt for future reference
        decoder.save_world_description(world_name + "_prompt", decoded_prompt)
        
        return {
            "world_name": world_name,
            "decoder_prompt": decoded_prompt,
            "dna_string": dna_string,
            "additional_context": additional_context
        }
    
    except Exception as e:
        logger.error(f"Error decoding DNA with context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dna/npc/decode")
async def decode_npc_dna(dna_string: str):
    """
    Decode an NPC personality DNA string into its traits and other information.
    
    Args:
        dna_string: The personality DNA string to decode.
        
    Returns:
        Decoded personality DNA information.
    """
    try:
        # Create an NPC personality decoder
        decoder = NPCPersonalityDecoder()
        
        # Format the DNA
        formatted_dna = decoder.format_personality_dna(dna_string)
        
        return {
            "lnc_average": formatted_dna["lnc_average"],
            "gne_average": formatted_dna["gne_average"],
            "lnc_alignment": decoder.lnc_alignment.get(formatted_dna["lnc_average"]),
            "gne_alignment": decoder.gne_alignment.get(formatted_dna["gne_average"]),
            "lnc_traits": formatted_dna["lnc_traits"],
            "gne_traits": formatted_dna["gne_traits"],
            "dna_string": dna_string
        }
    
    except Exception as e:
        logger.error(f"Error decoding NPC personality DNA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dna/npc/decode_with_context")
async def decode_npc_dna_with_context(request_data: Dict[str, Any] = Body(...)):
    """
    Decode an NPC personality DNA string with additional context into a rich character description.
    
    Args:
        request_data: Dictionary containing:
            - dna_string: The personality DNA string to decode
            - npc_name: Optional name of the NPC
            - additional_context: Optional additional context for the decoder
            
    Returns:
        The decoding prompt that can be sent to an LLM.
    """
    dna_string = request_data.get("dna_string", "")
    npc_name = request_data.get("npc_name", "Unnamed NPC")
    additional_context = request_data.get("additional_context", "")
    
    if not dna_string:
        raise HTTPException(status_code=400, detail="DNA string is required")
    
    try:
        # Create an NPC personality decoder
        decoder = NPCPersonalityDecoder()
        
        # Decode the DNA with context
        decoded_prompt = decoder.decode_personality(dna_string, additional_context)
        
        # Save the prompt for future reference
        decoder.save_npc_description(npc_name + "_prompt", decoded_prompt)
        
        return {
            "npc_name": npc_name,
            "decoder_prompt": decoded_prompt,
            "dna_string": dna_string,
            "additional_context": additional_context
        }
    
    except Exception as e:
        logger.error(f"Error decoding NPC personality DNA with context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication with the client.
    
    Args:
        websocket: The WebSocket connection
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if "type" not in message:
                await websocket.send_json({"error": "Invalid message format"})
                continue
            
            # Process message based on type
            if message["type"] == "user_input":
                # Process player input
                if "content" in message:
                    # Create a player input from the message
                    player_input = PlayerInput(
                        content=message["content"],
                        character_id=message.get("character_id")
                    )
                    
                    # Process the input
                    response = await process_input(player_input)
                else:
                    await websocket.send_json({"error": "Missing content in user_input message"})
            
            elif message["type"] == "get_state":
                # Send current game state to the client
                state = game_state.to_context_dict()
                await websocket.send_json({
                    "type": "state_update",
                    "state": state
                })
            
            elif message["type"] == "add_character":
                # Add a new character
                if "character" in message:
                    char_data = message["character"]
                    character = CharacterData(
                        name=char_data["name"],
                        race=char_data.get("race", "Human"),
                        character_class=char_data.get("class", ""),
                        level=char_data.get("level", 1),
                        id=char_data.get("id")
                    )
                    await add_character(character)
                else:
                    await websocket.send_json({"error": "Missing character data"})
            
            elif message["type"] == "save_game":
                # Save the current game
                result = await save_game()
                await websocket.send_json({
                    "type": "save_result",
                    "result": result
                })
            
            elif message["type"] == "load_game":
                # Load a game - in a real implementation, this would use the provided filename
                # For simplicity, we'll just load the most recent save if available
                saves_dir = Path("saves")
                if saves_dir.exists():
                    save_files = list(saves_dir.glob("*.json"))
                    if save_files:
                        # Sort by modification time, newest first
                        save_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                        result = await load_game(str(save_files[0]))
                        await websocket.send_json({
                            "type": "load_result",
                            "result": result
                        })
                    else:
                        await websocket.send_json({
                            "type": "load_result",
                            "result": {"status": "error", "message": "No save files found"}
                        })
                else:
                    await websocket.send_json({
                        "type": "load_result",
                        "result": {"status": "error", "message": "No saves directory found"}
                    })
            
            elif message["type"] == "change_system":
                # Change the game system
                if "system_id" in message:
                    result = await change_system(message["system_id"])
                    await websocket.send_json({
                        "type": "system_change_result",
                        "result": result
                    })
                else:
                    await websocket.send_json({"error": "Missing system_id in change_system message"})
            
            elif message["type"] == "get_rules":
                # Get rules for a system
                system_id = message.get("system_id", game_state.system_id)
                rule_id = message.get("rule_id")
                rules = await get_rules(system_id, rule_id)
                await websocket.send_json({
                    "type": "rules_data",
                    "rules": rules
                })
            
            elif message["type"] == "search_rules":
                # Search rules (simple implementation)
                if "query" in message and "system_id" in message:
                    system_id = message["system_id"]
                    query = message["query"].lower()
                    
                    # Get all rules for the system
                    rules = await get_rules(system_id)
                    
                    # Simple search implementation
                    # In a real app, this would use more sophisticated search
                    if "sections" in rules:
                        filtered_sections = []
                        
                        for section in rules["sections"]:
                            # Check if query matches section name or content
                            if query in section["name"].lower() or query in section["content"].lower():
                                filtered_sections.append(section)
                                continue
                            
                            # Check subsections
                            matching_subsections = []
                            for subsection in section.get("subsections", []):
                                if query in subsection["name"].lower() or query in subsection["content"].lower():
                                    matching_subsections.append(subsection)
                            
                            # If any subsections match, include the parent section with only matching subsections
                            if matching_subsections:
                                section_copy = section.copy()
                                section_copy["subsections"] = matching_subsections
                                filtered_sections.append(section_copy)
                        
                        # Return filtered results
                        search_results = {
                            "name": rules["name"],
                            "sections": filtered_sections
                        }
                        
                        await websocket.send_json({
                            "type": "rules_data",
                            "rules": search_results
                        })
                    else:
                        await websocket.send_json({
                            "type": "rules_data",
                            "rules": {"name": "Search Results", "sections": []}
                        })
                else:
                    await websocket.send_json({"error": "Missing query or system_id in search_rules message"})
            
            elif message["type"] == "search_knowledge":
                # Search knowledge base
                if "query" in message:
                    query = message["query"]
                    category = message.get("category")
                    results = game_state.search_knowledge_base(query, category)
                    await websocket.send_json({
                        "type": "knowledge_search_results",
                        "query": query,
                        "category": category,
                        "results": results,
                        "count": len(results)
                    })
                else:
                    await websocket.send_json({"error": "Missing query in search_knowledge message"})
            
            elif message["type"] == "add_knowledge_entry":
                # Add a knowledge entry
                if all(k in message for k in ["category", "key", "data"]):
                    category = message["category"]
                    key = message["key"]
                    data = message["data"]
                    
                    if category in game_state.knowledge_base:
                        success = game_state.add_knowledge_entry(category, key, data)
                        
                        if success:
                            await websocket.send_json({
                                "type": "knowledge_update_result",
                                "success": True,
                                "category": category,
                                "key": key
                            })
                            
                            # Notify other clients
                            await broadcast_message("knowledge_update", {
                                "category": category,
                                "key": key,
                                "action": "add_or_update"
                            }, exclude=[websocket])
                        else:
                            await websocket.send_json({
                                "type": "knowledge_update_result",
                                "success": False,
                                "error": "Failed to add knowledge entry"
                            })
                    else:
                        await websocket.send_json({
                            "type": "knowledge_update_result",
                            "success": False,
                            "error": f"Invalid category: {category}"
                        })
                else:
                    await websocket.send_json({"error": "Missing required fields for add_knowledge_entry"})
            
            elif message["type"] == "generate_summary":
                # Generate session summary
                summary = game_state.generate_session_summary()
                game_state.add_session_summary(summary)
                
                await websocket.send_json({
                    "type": "summary_generated",
                    "summary": summary
                })
                
                # Notify other clients
                await broadcast_message("session_summaries", {
                    "summaries": game_state.get_session_summaries()
                }, exclude=[websocket])
            
            elif message["type"] == "update_multimodal_settings":
                # Update multimodal settings
                if "settings" in message:
                    settings = message["settings"]
                    game_state.update_multimodal_settings(settings)
                    
                    await websocket.send_json({
                        "type": "settings_update_result",
                        "success": True,
                        "settings": game_state.multimodal_settings
                    })
                    
                    # Notify other clients
                    await broadcast_message("settings_update", {
                        "multimodal_settings": game_state.multimodal_settings
                    }, exclude=[websocket])
                else:
                    await websocket.send_json({"error": "Missing settings in update_multimodal_settings message"})
    
    except WebSocketDisconnect:
        # Handle client disconnect
        active_connections.remove(websocket)
        logger.info("Client disconnected")
    
    except Exception as e:
        # Handle other exceptions
        logger.error(f"WebSocket error: {e}")
        try:
            active_connections.remove(websocket)
        except ValueError:
            pass

async def broadcast_message(message_type: str, message_data: Dict[str, Any], exclude: List[WebSocket] = None):
    """
    Broadcast a message to all connected clients.
    
    Args:
        message_type: Type of message to send
        message_data: Message data to send
        exclude: Optional list of WebSocket connections to exclude
    """
    message = {"type": message_type, **message_data}
    exclude = exclude or []
    
    for connection in active_connections:
        if connection not in exclude:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")

async def broadcast_state_update():
    """Broadcast the current game state to all connected clients."""
    state = game_state.to_context_dict()
    await broadcast_message("state_update", {"state": state})

@app.on_event("startup")
async def startup_event():
    """Initialize resources when the server starts."""
    logger.info("Starting AI Game Master web server")
    
    # Create necessary directories
    Path("saves").mkdir(exist_ok=True)
