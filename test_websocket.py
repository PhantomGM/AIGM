"""
Test WebSocket client for the AI Game Master WebSocket endpoint.
"""

import asyncio
import websockets
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """Test connecting to the WebSocket and sending/receiving messages."""
    
    try:
        # Connect to the WebSocket server
        uri = "ws://127.0.0.1:8000/ws"
        logger.info(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            logger.info("Connection established!")
            
            # Receive the initial game state
            response = await websocket.recv()
            logger.info(f"Received initial game state")
            
            # Send a join message
            join_message = {
                "type": "join",
                "player_name": "TestPlayer",
                "session_id": "test_session_123"
            }
            await websocket.send(json.dumps(join_message))
            logger.info(f"Sent join message: {join_message}")
            
            # Receive the welcome message
            response = await websocket.recv()
            logger.info(f"Received welcome message")
            
            # Test random character generation
            character_gen_message = {
                "type": "generate_character"
            }
            await websocket.send(json.dumps(character_gen_message))
            logger.info(f"Sent character generation request")
            
            # Receive response for character generation
            response = await websocket.recv()
            logger.info(f"Received character generation response")
            
            # Send a test player input
            input_message = {
                "type": "player_input",
                "player_name": "TestPlayer",
                "message": "Hello, Game Master!",
                "character_id": "test_character_1"
            }
            
            await websocket.send(json.dumps(input_message))
            logger.info(f"Sent player input: {input_message}")
            
            # Receive the GM response
            response = await websocket.recv()
            logger.info(f"Received GM response")
            
            # Wait a moment to ensure all messages are processed
            await asyncio.sleep(2)
            
            logger.info("WebSocket test completed successfully!")
            
    except Exception as e:
        logger.error(f"Error in WebSocket test: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())
