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
- **DNA-based Generation**: Genetic approach to world and NPC creation for consistency and depth
- **Advanced World DNA Generation**: Enhanced system for simulating complex world creation and evolution

## DNA-based World and Character Generation

The AI Game Master features an innovative DNA-based generation system for creating consistent, detailed worlds and NPCs with distinctive personalities.

### World DNA

World DNA encodes fundamental traits of a game world, including:

- Physical characteristics (climate, terrain, magic level)
- Cultural aspects (technology level, dominant species)
- Political structures
- History and conflicts

DNA strings are encoded and decoded to create consistent world descriptions that can be:
- Randomly generated
- Mutated to create variations
- Combined through crossover to blend different world concepts

### Advanced World DNA Generation

The system now includes an enhanced World DNA generation system that simulates more sophisticated world creation and evolution. Key features include:

- **Complex Trait Representation**: Each trait now has both prevalence (1-9) and intensity (1-5) values
- **Critical Thresholds**: Traits can reach critical thresholds, triggering significant world events
- **Chain Reactions**: When thresholds are met, chain reactions can modify other traits automatically
- **Time Evolution**: Traits can evolve over time according to different patterns (accelerating, declining, unstable, stabilizing)
- **DNA Visualization**: Includes tools for visualizing trait evolution and relationships

This enhanced system produces worlds with more dynamic histories and futures, allowing for rich storytelling across different time periods.

#### Example of Advanced DNA Structure

```
V1.6 TRAITS{climate:83;terrain:54;resources:72;hazards:41;society:65;technology:93;religion:43;trade:61;government:71;conflict:84;diplomacy:82;stability:22;intensity:95;prevalence:94;schools:73;artifacts:84} THRESH{high_magic;advanced} EVO{technology:ACCELERATING[93,93,95,97];intensity:ACCELERATING[95,95,96,97];prevalence:ACCELERATING[94,94,96,98]}
```

Breaking down this structure:
- **V1.6**: Version identifier
- **TRAITS{...}**: List of traits with prevalence and intensity values (e.g., "technology:93" = prevalence 9, intensity 3)
- **THRESH{...}**: Critical thresholds that have been met
- **EVO{...}**: Evolution patterns for key traits, showing values over four time periods (PAST, PRESENT, NEAR FUTURE, FAR FUTURE)

#### Using the Advanced DNA System

You can generate worlds with the advanced DNA system through:

1. **API Endpoints**: 
   - `POST /api/world_dna/generate_advanced`: Generate a new world with advanced DNA
   - `POST /api/world_dna/evolve`: Evolve a world forward in time
   - `GET /api/world_dna/advanced/{world_name}`: Get the advanced DNA for an existing world

2. **Utility Scripts**:
   - `tests/test_advanced_dna.py`: Test various features of the advanced DNA system
   - `utils/dna_visualizer.py`: Visualize trait evolution and relationships

3. **Code Integration**:
   ```python
   from core.dna_generator import WorldDNAGenerator, WorldDNA

   # Generate advanced DNA
   generator = WorldDNAGenerator()
   advanced_dna = generator.generate_dna()

   # Convert to classic format for compatibility
   world_dna = WorldDNA.from_advanced_dna(advanced_dna)
   ```

The new system is fully backward compatible with the existing WorldDNA class.

### World DNA Decoder

The system includes a sophisticated DNA decoder that translates complex DNA strings into rich, coherent setting descriptions suitable for campaigns and storytelling. The decoder interprets:

- **Primary Scales & Genre**: Technology level, magic prevalence, and authority structures
- **Environmental, Societal, Conflict, and Historical Data**: Major geography, cultural norms, conflicts, and history
- **Regional Breakdowns**: Distinct traits, features, and challenges of different regions
- **Critical Thresholds & Chain Reactions**: Tipping points and how events cascade across the world
- **Evolution & Trends**: How traits change over time and what patterns emerge
- **Story Elements & Campaign Hooks**: Game-ready ideas tied to the world's unique aspects

#### Using the DNA Decoder

The DNA decoder can be accessed through:

1. **API Endpoints**:
   - `GET /api/dna/decode?dna_string={dna_string}`: Basic decoding of DNA structure
   - `POST /api/dna/decode_with_context`: Advanced decoding with additional context for richer interpretations

2. **Programmatic Usage**:
   ```python
   from core.dna_decoder import WorldDNADecoder
   
   decoder = WorldDNADecoder()
   prompt = decoder.decode_dna(advanced_dna, "Additional context here")
   ```

The decoder generates a structured prompt that can be sent to an LLM for final interpretation, producing a complete world description with:

- World Overview
- Regional Breakdown
- Critical Situations
- Evolution & Trends
- Current State
- Future Trajectories
- Story Elements / Campaign Hooks

### NPC Personality DNA

NPC Personality DNA models character traits based on:

- **Lawful/Neutral/Chaotic (LNC) Scale**: Structured, paired traits with 'prevalence' values (1-9) and 'intensity' values (1-5)
- **Good/Neutral/Evil (GNE) Scale**: Moral/ethical values with associated scores (1-9)
- Example pairs: Bold vs. Cautious, Rational vs. Emotional, Loyal vs. Independent
- Example values: Honor, Cunning, Knowledge, Loyalty, Justice

The DNA format for NPCs looks like this:
`(7/3) 5B4,2R1,8L3,4F5,7S2,3P1...`

Where:
- `(7/3)` is the LNC/GNE average alignment
- Each trait entry has a format: `{lnc_score}{trait_code}{intensity}` (e.g., `5B4` = prevalence 5, trait 'Bold', intensity 4)
- GNE traits have format: `{trait_code}{gne_score}` (e.g., `H7` = trait 'Honor', score 7)

### NPC Personality Decoder

The system includes an enhanced and comprehensive decoder for NPC personality DNA that translates trait codes into rich character profiles suitable for roleplaying. The decoder interprets:

- **Overall Alignment**: Interprets the LNC/GNE average values into a character's general alignment tendencies
- **Core Character Traits**: Detailed interpretation of trait codes, scores, and intensities into personality characteristics
- **Moral/Ethical Values**: Analysis of the character's values, beliefs, and ethical tendencies
- **Behavioral Patterns**: How the character typically behaves in various situations and under different circumstances
- **Voice & Expression**: Suggestions for how the character might speak, common phrases, and non-verbal communication
- **Background Implications**: Potential backstory elements that align with the personality traits
- **Development Potential**: Possible character arcs and evolution based on their current traits

#### Using the NPC Personality Decoder

The NPC personality decoder can be accessed through:

1. **API Endpoints**:
   - `GET /api/dna/npc/decode?dna_string={dna_string}`: Basic decoding of NPC personality structure
   - `POST /api/dna/npc/decode_with_context`: Advanced decoding with additional context for richer character profiles

2. **Programmatic Usage**:
   ```python
   from core.npc_decoder import NPCPersonalityDecoder
   
   decoder = NPCPersonalityDecoder()
   prompt = decoder.decode_personality(personality_dna, "Additional character context here")
   ```

The decoder generates a structured prompt with the following sections:

- **Personality Overview**: A holistic view of the character's personality and alignment
- **Defining Traits**: The most prominent characteristics that define the NPC
- **Contradictions & Complexity**: Internal conflicts and nuances that make the character realistic
- **Behavioral Patterns**:
  - Under Pressure: How they act in crisis or stress
  - With Authority: How they respond to leadership or power figures  
  - With Subordinates: How they treat those with less power
  - Core Values: Deep-seated beliefs that drive decision-making
- **Voice & Expression**: Speech patterns, common phrases, and physical mannerisms
- **Background Implications**: What their personality suggests about their past
- **Development Potential**: How the character might grow or change over time

This structured output can be sent to a language model to produce exceptionally detailed and consistent NPC characterizations.

#### Example Output

The system produces rich NPC profiles like this abbreviated example:

```
# NPC CHARACTER PROFILE: DR. ELIAS THORNWOOD

## Personality Overview
A balanced healer combining traditional and magical techniques with mechanical devices...

## Behavioral Patterns
- Under Pressure: Becomes hyperfocused and exceptionally calm (E2)
- With Authority: Shows appropriate respect but advocates firmly for patient needs (T9)
- With Subordinates: Treats apprentices with patience and kindness (P1)
- Core Values: Values the alleviation of suffering and patient dignity above all

## Voice & Expression
Speaks in measured, precise tones with a warm timbre... Common phrases include "Let's examine this systematically"...
```

### Using DNA Generation

The DNA system features:

- API endpoints for generating and manipulating world and NPC DNA
- Ability to save and load DNA for reuse
- Mutation and crossover mechanics for creating variations
- Comprehensive testing framework for validating DNA generation and interpretation
- Natural language prompts derived from DNA for LLM-based generation
- Personality evolution based on character experiences

This technology creates more believable, consistent game worlds and characters that maintain their integrity throughout the campaign.

### Testing the System

The AI Game Master includes extensive testing capabilities:

1. **DNA Generation Tests**:
   ```
   python -m tests.test_dna_generator
   ```

2. **DNA Decoding Tests**:
   ```
   python -m tests.test_dna_decoder
   ```

3. **NPC Personality Tests**:
   ```
   python -m tests.test_npc_decoder
   ```

The NPC decoder tests validate:
- Basic personality trait interpretation
- Contextual decoding with additional background information
- Integration with LLM responses for complete character profiles

### Getting Started

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
