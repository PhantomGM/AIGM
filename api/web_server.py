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

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import game state manager
from core.game_state import GameState
from core.system_manager import SystemManager

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
