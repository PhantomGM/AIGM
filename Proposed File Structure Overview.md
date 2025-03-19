# Proposed File Structure for AI Game Master System

Let me outline a comprehensive file structure for your AI Game Master system. This structure organizes your project into logical components while supporting the multi-agent architecture you've described.

## Root Directory Structure

```
ai-game-master/
├── .env                      # Environment variables (API keys, configuration)
├── .gitignore                # Git ignore file
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── setup.py                  # Package installation script
├── docker-compose.yml        # Container orchestration for services
├── core/                     # Core system functionality
├── agents/                   # All agent implementations
├── models/                   # Data models and schemas
├── storage/                  # Database and persistence layer
├── api/                      # API endpoints for web/mobile clients
├── ui/                       # User interfaces (web, desktop)
├── mobile/                   # Mobile app specific code
├── tools/                    # Shared tools used by agents
├── tests/                    # Test suite
└── docs/                     # Documentation
```

## Core System Component

The core directory contains the central system functionality:

```
core/
├── __init__.py
├── controller.py             # Controller Agent implementation
├── game_state.py             # Game state management
├── session_manager.py        # Session creation and management
├── agent_coordinator.py      # Coordination between agents
├── context_manager.py        # Context window optimization
├── message_bus.py            # Inter-agent communication
├── user_manager.py           # User authentication and profiles
├── security.py               # Security and privacy controls
└── config.py                 # System configuration
```

## Agent Implementation

The agents directory contains all specialized agents:

```
agents/
├── __init__.py
├── base_agent.py             # Abstract base class for all agents
├── primary/                  # Primary agent implementations
│   ├── __init__.py
│   ├── rules_reference.py    # Rules Reference Agent
│   ├── memory_keeper.py      # Memory Keeper Agent
│   ├── world_builder.py      # World Builder Agent
│   ├── npc_manager.py        # NPC Manager Agent
│   ├── narrative_designer.py # Narrative Designer Agent
│   ├── lore_manager.py       # Lore Manager Agent
│   ├── cultural_dynamics.py  # Cultural Dynamics Agent
│   ├── economic_systems.py   # Economic Systems Agent
│   └── magic_systems.py      # Magic Systems Agent
├── supporting/               # Supporting agent implementations
│   ├── __init__.py
│   ├── campaign_architect.py # Campaign Architect Agent
│   ├── history_integration.py# History Integration Agent
│   ├── safety_management.py  # Safety Management Agent
│   └── meta_gaming.py        # Meta-Gaming Simulation Agent
└── prompts/                  # Agent-specific prompts
    ├── __init__.py
    ├── rules_reference/      # Prompts for Rules Reference Agent
    ├── world_builder/        # Prompts for World Builder Agent
    └── ...                   # Directories for other agents
```

## Data Models

The models directory defines data structures used throughout the system:

```
models/
├── __init__.py
├── game_world.py             # Game world representation
├── character.py              # Character data model
├── npc.py                    # NPC data model with Personality DNA
├── world_dna.py              # World DNA implementation
├── timeline.py               # Timeline and event models
├── relationship.py           # Entity relationship models
├── campaign.py               # Campaign structure models
├── user.py                   # User profile models
└── schemas/                  # JSON schemas for validation
    ├── __init__.py
    ├── world_schema.json     # Schema for world data
    ├── character_schema.json # Schema for character data
    └── ...                   # Other schemas
```

## Storage Layer

The storage directory handles persistence of game data:

```
storage/
├── __init__.py
├── database.py               # Database connection management
├── vector_store.py           # Vector database implementation
├── graph_store.py            # Graph database for relationships
├── repositories/             # Data access layer
│   ├── __init__.py
│   ├── world_repository.py   # World data operations
│   ├── character_repository.py # Character data operations
│   └── ...                   # Other repositories
└── migrations/               # Database migrations
```

## API Layer

The API directory contains endpoints for client applications:

```
api/
├── __init__.py
├── app.py                    # API application entry point
├── middleware/               # API middleware
│   ├── __init__.py
│   ├── authentication.py     # Auth middleware
│   └── rate_limiting.py      # Rate limiting
├── routes/                   # API routes
│   ├── __init__.py
│   ├── game_routes.py        # Game management endpoints
│   ├── world_routes.py       # World management endpoints
│   ├── character_routes.py   # Character management endpoints
│   └── user_routes.py        # User management endpoints
└── websockets/               # WebSocket handlers for real-time communication
    ├── __init__.py
    └── game_session.py       # Game session WebSocket handler
```

## User Interfaces

The UI directory contains web and desktop interfaces:

```
ui/
├── web/                      # Web application
│   ├── public/               # Static files
│   ├── src/                  # Frontend source code
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── state/            # State management
│   │   └── api/              # API client
│   └── package.json          # Frontend dependencies
└── desktop/                  # Desktop application
    ├── src/                  # Electron app source
    ├── assets/               # Desktop app assets
    └── package.json          # Desktop app dependencies
```

## Mobile Applications

The mobile directory contains mobile-specific code:

```
mobile/
├── android/                  # Android-specific code
├── ios/                      # iOS-specific code
├── src/                      # Shared mobile code
│   ├── components/           # Mobile UI components
│   ├── screens/              # Screen components
│   ├── navigation/           # Navigation configuration
│   └── api/                  # Mobile API client
└── package.json              # Mobile dependencies
```

## Shared Tools

The tools directory contains utilities used across the system:

```
tools/
├── __init__.py
├── llm_client.py             # Language model API client
├── prompt_templates.py       # Common prompt templates
├── vector_search.py          # Vector search utilities
├── entity_graph.py           # Entity relationship graph tools
├── dice_roller.py            # Virtual dice rolling
└── content_moderation.py     # Content safety checking
```

## Testing Framework

The tests directory contains the test suite:

```
tests/
├── __init__.py
├── conftest.py               # Test configuration
├── unit/                     # Unit tests
│   ├── __init__.py
│   ├── test_controller.py    # Controller Agent tests
│   ├── test_world_builder.py # World Builder Agent tests
│   └── ...                   # Other unit tests
├── integration/              # Integration tests
│   ├── __init__.py
│   ├── test_agent_communication.py # Tests for agent coordination
│   └── ...                   # Other integration tests
└── fixtures/                 # Test fixtures
    ├── worlds/               # Sample world data
    ├── characters/           # Sample character data
    └── campaigns/            # Sample campaign data
```

## Documentation

The docs directory contains comprehensive documentation:

```
docs/
├── architecture/             # Architecture documentation
│   ├── system_overview.md    # System architecture overview
│   ├── agent_design.md       # Agent design principles
│   └── data_flow.md          # Data flow diagrams
├── api/                      # API documentation
│   ├── endpoints.md          # API endpoint reference
│   └── websockets.md         # WebSocket protocol docs
├── development/              # Development guides
│   ├── getting_started.md    # Developer onboarding
│   ├── adding_agents.md      # Guide to adding new agents
│   └── testing.md            # Testing guidelines
└── user/                     # User documentation
    ├── game_creation.md      # Game creation guide
    ├── character_creation.md # Character creation guide
    └── gameplay.md           # Gameplay instructions
```

This file structure supports your complex multi-agent architecture while organizing code logically. It separates concerns appropriately (core system, agents, models, storage, API, UI) and provides appropriate abstractions for each component. The structure is also set up to support cross-platform deployment with web, desktop, and mobile interfaces all sharing the same backend services.

As you implement this system, you might need to adjust the structure to accommodate specific technologies or patterns you choose, but this provides a solid foundation to build upon. Would you like me to elaborate on any specific part of this structure or discuss implementation details for particular components?