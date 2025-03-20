# AI Game Master System

A sophisticated multi-agent AI system designed to provide a complete tabletop role-playing game (TTRPG) experience. This system combines advanced language models, specialized agents, intelligent tools, and social features to create an experience that rivals or exceeds human game mastering.

## Features

- **Multi-Agent Architecture**: A hierarchical structure with specialized AI components handling different aspects of game management
- **Controller Agent**: Central orchestrator that processes player inputs, determines which specialized agents to consult, and synthesizes responses
- **Specialized Agents**: Including Rules Reference, Memory Keeper, World Builder, NPC Manager, Narrative Designer, and more
- **Rich World Generation**: Proprietary World DNA and NPC Personality DNA frameworks to ensure consistency and depth
- **History Generation**: Sophisticated world and history generation capabilities with integrated historical development
- **Comprehensive Knowledge Base**: Structured repository for NPCs, locations, items, factions, lore, quests, and player notes with search capabilities
- **Session Summaries**: Automatic generation of detailed session summaries to help players and GMs track campaign progress
- **Multimodal Interaction**: Support for text-to-speech, speech-to-text, and image generation to enhance the gaming experience
- **Cross-Platform Design**: Deployable across desktop, web, and mobile platforms
- **Social Features**: User profiles, game discovery, and community building tools

## Getting Started

### Prerequisites

- Python 3.10+
- OpenAI API key or other LLM access

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your environment variables:
   ```
   cp .env.example .env
   ```
   Then edit `.env` with your API keys and configuration.

4. Run the application:
   ```
   python -m core.app
   ```

## API Endpoints

The system provides comprehensive API endpoints for interacting with the game state:

### Knowledge Base API

- `GET /api/knowledge`: Retrieve knowledge base entries by category and/or key
- `POST /api/knowledge`: Add or update a knowledge base entry
- `DELETE /api/knowledge/{category}/{key}`: Remove a knowledge base entry
- `GET /api/knowledge/search`: Search the knowledge base with custom queries

### Session Management

- `GET /api/sessions`: Get all available session summaries
- `POST /api/generate_summary`: Generate a new session summary
- `GET /api/sessions/{id}`: Get a specific session summary

### Game Systems

- `GET /api/systems`: List all available game systems
- `GET /api/system/{id}/rules`: Get rules for a specific game system
- `POST /api/change_system`: Change the active game system

### Multimodal Settings

- `POST /api/multimodal_settings`: Update settings for text-to-speech, speech-to-text, and image generation

## Project Structure

The project is organized into the following main directories:

- `core/`: Core system functionality
- `agents/`: All agent implementations
- `models/`: Data models and schemas
- `storage/`: Database and persistence layer
- `api/`: API endpoints for web/mobile clients
- `ui/`: User interfaces (web, desktop)
- `tools/`: Shared tools used by agents
- `tests/`: Test suite

## License

This project is licensed under the MIT License - see the LICENSE file for details.
