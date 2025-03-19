# AI Game Master System

A sophisticated multi-agent AI system designed to provide a complete tabletop role-playing game (TTRPG) experience. This system combines advanced language models, specialized agents, intelligent tools, and social features to create an experience that rivals or exceeds human game mastering.

## Features

- **Multi-Agent Architecture**: A hierarchical structure with specialized AI components handling different aspects of game management
- **Controller Agent**: Central orchestrator that processes player inputs, determines which specialized agents to consult, and synthesizes responses
- **Specialized Agents**: Including Rules Reference, Memory Keeper, World Builder, NPC Manager, Narrative Designer, and more
- **Rich World Generation**: Proprietary World DNA and NPC Personality DNA frameworks to ensure consistency and depth
- **History Generation**: Sophisticated world and history generation capabilities with integrated historical development
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
