"""
Web Server API for AI Game Master

This module implements a FastAPI web server that provides a REST API for interacting with
the AI Game Master system. It handles player input, game state updates, and provides endpoints
for web UI integration.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from starlette.websockets import WebSocketState

from pydantic import BaseModel

# Import Game Master components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.controller import ControllerAgent
from core.game_state import GameState

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Game Master API", description="API for interacting with the AI Game Master system")

# Path to static files and templates
STATIC_DIR = Path(__file__).parent.parent / "ui" / "web" / "static"
TEMPLATES_DIR = Path(__file__).parent.parent / "ui" / "web" / "templates"

# Mount static files directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Initialize game master components
controller = ControllerAgent()
game_state = GameState()

# Add some dummy data for testing
game_state.update_location("Forest Clearing")
game_state.environment["weather"] = "clear skies"
game_state.environment["time_of_day"] = "morning"
game_state.environment["temperature"] = "warm"
game_state.add_event("game_start", {"session_number": game_state.session_number})

# Connected WebSocket clients for real-time updates
connected_clients = []

# Pydantic models for API requests and responses
class PlayerInput(BaseModel):
    message: str
    player_name: str
    character_id: Optional[str] = None
    session_id: Optional[str] = None

class GameMasterResponse(BaseModel):
    response: str
    game_state: Dict[str, Any]
    events: List[Dict[str, Any]] = []

class CharacterData(BaseModel):
    name: str
    race: str
    class_name: str
    level: int
    attributes: Dict[str, int]
    additional_info: Optional[Dict[str, Any]] = None

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main UI page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/input", response_model=GameMasterResponse)
async def process_input(player_input: PlayerInput):
    """
    Process player input and generate a response from the Game Master.
    
    Args:
        player_input: The player's input message and metadata.
        
    Returns:
        GameMasterResponse: The Game Master's response and updated game state.
    """
    try:
        # Log the incoming message
        logger.info(f"Received input from {player_input.player_name}: {player_input.message}")
        
        # Process the input through the controller
        response = controller.process_query(player_input.message, {
            "player_name": player_input.player_name,
            "character_id": player_input.character_id,
            "game_state": game_state.to_context_dict()
        })
        
        # Get the updated game state
        state_dict = game_state.to_context_dict()
        
        # Get recent events
        events = game_state.get_recent_events(count=5)
        
        # Notify all connected WebSocket clients about the update
        await notify_clients({
            "type": "game_update",
            "response": response,
            "game_state": state_dict,
            "events": events
        })
        
        return GameMasterResponse(
            response=response,
            game_state=state_dict,
            events=events
        )
    
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing input: {str(e)}")

@app.get("/api/game_state", response_model=Dict[str, Any])
async def get_game_state():
    """
    Get the current game state.
    
    Returns:
        Dict: The current game state.
    """
    return game_state.to_context_dict()

@app.get("/api/npcs", response_model=List[str])
async def get_active_npcs():
    """
    Get a list of active NPCs in the current scene.
    
    Returns:
        List[str]: Names of active NPCs.
    """
    return list(game_state.active_npcs)

@app.post("/api/character/add")
async def add_character(character: CharacterData):
    """
    Add a new player character to the game.
    
    Args:
        character: The character data.
        
    Returns:
        Dict: Confirmation message and character ID.
    """
    # Generate a character ID based on name
    character_id = f"char_{character.name.lower().replace(' ', '_')}"
    
    # Add the character to the game state
    game_state.add_active_character(character_id, character.dict())
    
    return {"message": f"Character {character.name} added successfully", "character_id": character_id}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication with the UI.
    
    Args:
        websocket: The WebSocket connection.
    """
    client_id = None
    
    try:
        await websocket.accept()
        connected_clients.append(websocket)
        
        # Log connection
        logger.info(f"New WebSocket connection established: {id(websocket)}")
        
        # Send initial game state to the client
        await websocket.send_json({
            "type": "game_update",
            "game_state": game_state.to_context_dict(),
            "events": game_state.get_recent_events(count=5)
        })
        
        while True:
            # Receive message from WebSocket
            data = await websocket.receive_text()
            
            # Process the message as JSON
            message = json.loads(data)
            message_type = message.get("type", "")
            
            logger.info(f"Received WebSocket message of type '{message_type}'")
            
            # Handle join messages to identify the client
            if message_type == "join":
                client_id = message.get("session_id", str(id(websocket)))
                player_name = message.get("player_name", "Player")
                logger.info(f"Client identified: {player_name} ({client_id})")
                
                # Welcome message
                await websocket.send_json({
                    "type": "system_message",
                    "message": f"Welcome, {player_name}! You are now connected to the game."
                })
                
                # Notify other clients about the new player
                await notify_clients({
                    "type": "system_message",
                    "message": f"{player_name} has joined the game."
                }, exclude=websocket)
                
            # Process player input messages
            elif message_type == "player_input":
                # Process player input through the controller
                try:
                    # Extract player input data
                    player_message = message.get("message", "")
                    player_name = message.get("player_name", "Player")
                    character_id = message.get("character_id")
                    
                    logger.info(f"Processing input from {player_name}: {player_message}")
                    
                    # Add player message to chat for other clients
                    await notify_clients({
                        "type": "player_message",
                        "player_name": player_name,
                        "message": player_message,
                        "character_id": character_id
                    })
                    
                    # In a real implementation, this would call the AI system
                    # For now, we'll just echo the message back with some additional text
                    response = f"Game Master: I acknowledge your message, '{player_message}'. " + \
                              f"The adventure continues in {game_state.current_location}."
                    
                    # Add a sample event for testing
                    game_state.add_event("player_action", {
                        "player": player_name,
                        "action": player_message[:50],  # Truncate long messages
                        "character_id": character_id
                    })
                    
                    # Send response back to this client
                    await websocket.send_json({
                        "type": "gm_response",
                        "response": response,
                        "game_state": game_state.to_context_dict(),
                        "events": game_state.get_recent_events(count=5)
                    })
                    
                    # Notify other clients about the update
                    await notify_clients({
                        "type": "game_update",
                        "game_state": game_state.to_context_dict(),
                        "events": game_state.get_recent_events(count=5),
                        "response": response
                    }, exclude=websocket)
                    
                except Exception as e:
                    logger.error(f"Error processing player input: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error processing your input: {str(e)}"
                    })
            
            # Handle character generation
            elif message_type == "generate_character":
                try:
                    # Log the character generation request
                    logger.info(f"Character generation requested by {client_id}")
                    
                    # In a real implementation, you would have more logic here
                    # For now, we'll just acknowledge the request
                    await websocket.send_json({
                        "type": "system_message",
                        "message": "Character generation request received. The random character has been generated and applied to the form."
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing character generation: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error generating character: {str(e)}"
                    })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {client_id or id(websocket)}")
        # Remove client on disconnect
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        
        # Notify other clients about the disconnect
        if client_id:
            await notify_clients({
                "type": "system_message",
                "message": f"A player has left the game."
            })
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        # Try to send an error message before closing
        try:
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
        
        # Remove client on error
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def notify_clients(message: Dict[str, Any], exclude: WebSocket = None):
    """
    Send a message to all connected WebSocket clients.
    
    Args:
        message: The message to send.
        exclude: Optional WebSocket client to exclude from the notification.
    """
    for client in connected_clients:
        if client != exclude:
            try:
                await client.send_json(message)
            except Exception as e:
                logger.error(f"Error notifying client: {e}")

@app.get("/api/characters", response_model=Dict[str, Any])
async def get_characters():
    """
    Get all active player characters.
    
    Returns:
        Dict: Character IDs mapped to character data.
    """
    return game_state.active_characters

@app.get("/api/save_game")
async def save_game(file_path: Optional[str] = None):
    """
    Save the current game state to a file.
    
    Args:
        file_path: Optional path to save the game state.
        
    Returns:
        Dict: Confirmation message and save path.
    """
    if not file_path:
        file_path = f"saves/game_{game_state.game_id}.json"
    
    # Ensure the saves directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save the game state
    success = game_state.save_to_file(file_path)
    
    if success:
        return {"message": "Game saved successfully", "path": file_path}
    else:
        raise HTTPException(status_code=500, detail="Failed to save game")

@app.get("/api/load_game")
async def load_game(file_path: str):
    """
    Load a game state from a file.
    
    Args:
        file_path: Path to the saved game file.
        
    Returns:
        Dict: Confirmation message and loaded game ID.
    """
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Save file not found: {file_path}")
    
    # Load the game state
    global game_state
    game_state = GameState.load_from_file(file_path)
    
    # Notify all connected clients about the update
    await notify_clients({
        "type": "game_loaded",
        "game_state": game_state.to_context_dict(),
        "events": game_state.get_recent_events(count=5)
    })
    
    return {"message": "Game loaded successfully", "game_id": game_state.game_id}

if __name__ == "__main__":
    # Run the FastAPI app with uvicorn
    uvicorn.run("api.web_server:app", host="0.0.0.0", port=8000, reload=True)
