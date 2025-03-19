"""
Web Server Launcher for AI Game Master

This script launches the FastAPI web server for the AI Game Master system.
It provides a convenient way to start the server with the correct configuration.
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Make sure the necessary directories exist
def ensure_directories_exist():
    """Ensure that all required directories exist."""
    dirs = [
        Path("saves"),
    ]
    
    for directory in dirs:
        if not directory.exists():
            directory.mkdir(parents=True)
            logger.info(f"Created directory: {directory}")

def main():
    """Main function to run the web server."""
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Add the current directory to sys.path if it's not already there
    if script_dir not in sys.path:
        sys.path.append(script_dir)
    
    # Create necessary directories
    ensure_directories_exist()
    
    # Configuration
    host = "127.0.0.1"  # Use localhost for development
    port = 8000  # Default port for the API
    
    print(f"""
+--------------------------------------------+
|                                            |
|         AI GAME MASTER WEB SERVER          |
|                                            |
+--------------------------------------------+

Server starting at http://{host}:{port}

* Open your web browser and navigate to the above URL
* Press Ctrl+C in this terminal to stop the server
""")
    
    # Run the server
    uvicorn.run("api.web_server:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()
