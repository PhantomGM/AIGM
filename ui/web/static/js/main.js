/**
 * AI Game Master - Main JavaScript
 * This file handles client-side functionality for the AI Game Master web UI
 */

// DOM elements
const chatMessages = document.getElementById('chat-messages');
const playerInput = document.getElementById('player-input');
const sendBtn = document.getElementById('send-input-btn');
const characterSelect = document.getElementById('character-select');
const characterForm = document.getElementById('character-form');
const addCharacterBtn = document.getElementById('add-character-btn');
const randomCharacterBtn = document.getElementById('random-character-btn');
const characterModal = document.getElementById('character-modal');
const saveGameBtn = document.getElementById('save-game-btn');
const loadGameBtn = document.getElementById('load-game-btn');
const saveNotesBtn = document.getElementById('save-notes-btn');
const gameNotes = document.getElementById('game-notes');
const diceResult = document.getElementById('dice-result');
const diceButtons = document.querySelectorAll('.dice-button');
const rollCustomDiceBtn = document.getElementById('roll-custom-dice');
const customDiceInput = document.getElementById('custom-dice-input');
const tabButtons = document.querySelectorAll('.tab-button');

// Character profile elements
const characterListEl = document.getElementById('character-list');
const characterProfileModal = document.getElementById('character-profile-modal');
const profileCharName = document.getElementById('profile-char-name');
const profileCharRace = document.getElementById('profile-char-race');
const profileCharClass = document.getElementById('profile-char-class');
const profileCharLevel = document.getElementById('profile-char-level');
const profileCharBackground = document.getElementById('profile-char-background');
const speakAsCharacterBtn = document.getElementById('speak-as-character-btn');
const editCharacterBtn = document.getElementById('edit-character-btn');
const profileAttrStr = document.getElementById('profile-attr-str');
const profileAttrDex = document.getElementById('profile-attr-dex');
const profileAttrCon = document.getElementById('profile-attr-con');
const profileAttrInt = document.getElementById('profile-attr-int');
const profileAttrWis = document.getElementById('profile-attr-wis');
const profileAttrCha = document.getElementById('profile-attr-cha');
const profileAttrStrMod = document.getElementById('profile-attr-str-mod');
const profileAttrDexMod = document.getElementById('profile-attr-dex-mod');
const profileAttrConMod = document.getElementById('profile-attr-con-mod');
const profileAttrIntMod = document.getElementById('profile-attr-int-mod');
const profileAttrWisMod = document.getElementById('profile-attr-wis-mod');
const profileAttrChaMod = document.getElementById('profile-attr-cha-mod');

// Game state elements
const currentLocationEl = document.getElementById('current-location');
const gameTimeEl = document.getElementById('game-time');
const environmentDescriptionEl = document.getElementById('environment-description');
const npcListEl = document.getElementById('npc-list');
const eventLogEl = document.getElementById('event-log');
const gameModeIndicator = document.getElementById('game-mode');
const loadingOverlay = document.getElementById('loading-overlay');

// Global variables
let playerName = "Player"; // Default player name
let sessionId = generateSessionId();

// Global variables to store character data
let characterData = {};
let currentProfileCharacterId = null;

// Initialize the application
function init() {
    // Load saved notes from localStorage
    const savedNotes = localStorage.getItem('gameNotes');
    if (savedNotes) {
        gameNotes.value = savedNotes;
    }
    
    // Connect to WebSocket
    connectWebSocket();
    
    // Initialize event listeners
    initializeEventListeners();
}

// Generate a unique session ID
function generateSessionId() {
    return 'session_' + Math.random().toString(36).substring(2, 10);
}

// Connect to the WebSocket server
function connectWebSocket() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
    
    console.log(`Connecting to WebSocket at ${wsUrl}`);
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = () => {
        console.log('WebSocket connection established');
        
        // Send player information to identify this client
        socket.send(JSON.stringify({
            type: 'join',
            player_name: playerName,
            session_id: sessionId
        }));
    };
    
    socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
    };
    
    socket.onclose = () => {
        console.log('WebSocket connection closed');
        // Attempt to reconnect after delay
        setTimeout(connectWebSocket, 2000);
    };
    
    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

// Handle incoming WebSocket messages
function handleWebSocketMessage(message) {
    const messageType = message.type;
    
    switch (messageType) {
        case 'game_update':
            // Update the game state
            if (message.game_state) {
                updateGameState(message.game_state);
            }
            
            // Handle any included response from the GM
            if (message.response) {
                addGMMessage(message.response);
            }
            
            // Update event log if events are included
            if (message.events && message.events.length > 0) {
                updateEventLog(message.events);
            }
            break;
            
        case 'player_message':
            // Display message from another player
            addPlayerMessage(message.message, message.player_name, message.character_id);
            break;
            
        case 'system_message':
            // Display system notification
            addSystemMessage(message.message);
            break;
            
        case 'error':
            // Display error message
            addSystemMessage(message.message, true);
            break;
            
        case 'character_generated':
            // Handle random character generation response
            handleRandomCharacterResponse(message.character);
            break;
            
        default:
            console.log('Unknown message type:', messageType);
    }
}

// Initialize event listeners
function initializeEventListeners() {
    // Player input form submission
    sendBtn.addEventListener('click', () => {
        sendPlayerMessage();
    });
    
    playerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendPlayerMessage();
        }
    });
    
    // Character creation button
    addCharacterBtn.addEventListener('click', () => {
        characterModal.style.display = 'block';
    });
    
    // Modal close button
    document.querySelectorAll('.close-modal').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Form submission
    characterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        createCharacter();
    });
    
    // Random character generation
    randomCharacterBtn.addEventListener('click', generateRandomCharacter);
    
    // Save and load game
    saveGameBtn.addEventListener('click', saveGame);
    loadGameBtn.addEventListener('click', loadGame);
    
    // Save notes
    saveNotesBtn.addEventListener('click', saveNotes);
    
    // Dice buttons
    diceButtons.forEach(button => {
        button.addEventListener('click', () => {
            const diceType = button.dataset.dice;
            showDiceRoll(diceType);
        });
    });
    
    // Custom dice roll
    rollCustomDiceBtn.addEventListener('click', rollCustomDice);
    
    // Tab buttons
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
    
    // Character profile modal close button
    document.querySelectorAll('.close-modal').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Speak as selected character
    speakAsCharacterBtn.addEventListener('click', () => {
        if (currentProfileCharacterId) {
            characterSelect.value = currentProfileCharacterId;
            characterProfileModal.style.display = 'none';
            playerInput.focus();
        }
    });
    
    // Edit character (to be implemented)
    editCharacterBtn.addEventListener('click', () => {
        // This will be implemented in a future update
        addSystemMessage("Character editing will be available in a future update.");
        characterProfileModal.style.display = 'none';
    });
    
    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === characterModal) {
            characterModal.style.display = 'none';
        } else if (e.target === characterProfileModal) {
            characterProfileModal.style.display = 'none';
        }
    });
}

// Send a player message through WebSocket
function sendPlayerMessage() {
    const message = playerInput.value.trim();
    if (!message) return;
    
    // Get the selected character (if any)
    const characterId = characterSelect.value || null;
    
    // Display the message in the chat
    const speakerName = characterId ? characterSelect.options[characterSelect.selectedIndex].text : playerName;
    addPlayerMessage(message, speakerName, characterId);
    
    // Send via WebSocket
    socket.send(JSON.stringify({
        type: 'player_input',
        message: message,
        player_name: playerName,
        character_id: characterId,
        session_id: sessionId
    }));
    
    // Clear the input field
    playerInput.value = '';
}

// Add a player message to the chat
function addPlayerMessage(message, speakerName = 'Player', characterId = null) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message player-message';
    
    messageElement.innerHTML = `
        <div class="message-content">
            <p><strong>${speakerName}:</strong> ${message}</p>
        </div>
        <div class="message-timestamp">${formatTimestamp()}</div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

// Add a GM message to the chat
function addGMMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message gm-message';
    
    // Replace Markdown-style formatting with HTML
    const formattedMessage = formatMarkdown(message);
    
    messageElement.innerHTML = `
        <div class="message-content">
            <p>${formattedMessage}</p>
        </div>
        <div class="message-timestamp">${formatTimestamp()}</div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

// Add a system message to the chat (for notifications)
function addSystemMessage(message, isError = false) {
    const messageElement = document.createElement('div');
    messageElement.className = isError ? 'message system-message error' : 'message system-message';
    
    messageElement.innerHTML = `
        <div class="message-content">
            <p>${message}</p>
        </div>
        <div class="message-timestamp">${formatTimestamp()}</div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

// Format timestamp for messages
function formatTimestamp() {
    const now = new Date();
    return now.toLocaleTimeString();
}

// Format markdown-style text to HTML
function formatMarkdown(text) {
    // Bold: **text** -> <strong>text</strong>
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic: *text* -> <em>text</em>
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Add paragraph breaks
    text = text.replace(/\n\n/g, '</p><p>');
    
    return text;
}

// Scroll chat to bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Update the game state with new data
function updateGameState(stateData) {
    // Update location
    if (stateData.current_location) {
        currentLocationEl.textContent = stateData.current_location;
    } else {
        currentLocationEl.textContent = 'Unknown';
    }
    
    // Update game time
    if (stateData.game_time) {
        if (typeof stateData.game_time === 'string') {
            gameTimeEl.textContent = stateData.game_time;
        } else {
            const time = stateData.game_time;
            gameTimeEl.textContent = `Day ${time.day}, ${time.hour}:${time.minute < 10 ? '0' + time.minute : time.minute}`;
        }
    } else {
        gameTimeEl.textContent = 'Day 1, 8:00';
    }
    
    // Update environment description
    if (stateData.environment) {
        const env = stateData.environment;
        environmentDescriptionEl.textContent = `${env.time_of_day}, ${env.weather}, ${env.temperature}`;
    } else {
        environmentDescriptionEl.textContent = 'Normal conditions';
    }
    
    // Update game mode
    if (stateData.game_mode) {
        gameModeIndicator.textContent = `${capitalizeFirstLetter(stateData.game_mode)} Mode`;
    }
    
    // Update character list
    if (stateData.active_characters) {
        updateCharacterList(stateData.active_characters);
    }
    
    // Update NPC list
    if (stateData.active_npcs) {
        updateNPCList(stateData.active_npcs);
    }
}

// Update the character list
function updateCharacterList(characters) {
    // Clear current list
    characterListEl.innerHTML = '';
    
    // Clear character select dropdown (keep only the "Speak as Player" option)
    while (characterSelect.options.length > 1) {
        characterSelect.remove(1);
    }
    
    if (Object.keys(characters).length === 0) {
        characterListEl.innerHTML = '<li>No characters yet</li>';
        return;
    }
    
    // Store character data globally
    characterData = characters;
    
    // Add each character to the list and dropdown
    for (const [id, character] of Object.entries(characters)) {
        // Add to sidebar list
        const li = document.createElement('li');
        li.textContent = `${character.name} (${character.race} ${character.class_name} ${character.level})`;
        li.dataset.characterId = id;
        li.addEventListener('click', () => openCharacterProfile(id));
        characterListEl.appendChild(li);
        
        // Add to dropdown
        const option = document.createElement('option');
        option.value = id;
        option.textContent = character.name;
        characterSelect.appendChild(option);
    }
}

// Update the NPC list
function updateNPCList(npcs) {
    // Clear current list
    npcListEl.innerHTML = '';
    
    if (npcs.length === 0) {
        npcListEl.innerHTML = '<li>No NPCs in the scene</li>';
        return;
    }
    
    // Add each NPC to the list
    for (const npc of npcs) {
        const li = document.createElement('li');
        li.textContent = npc;
        npcListEl.appendChild(li);
    }
}

// Update the event log
function updateEventLog(events) {
    if (!events || events.length === 0) return;
    
    // Clear current log
    eventLogEl.innerHTML = '';
    
    // Add each event to the log
    for (const event of events) {
        const eventEl = document.createElement('p');
        
        // Format the event display based on its type
        switch (event.type) {
            case 'location_change':
                eventEl.textContent = `Location changed to ${event.data.new_location}`;
                break;
                
            case 'player_action':
                eventEl.textContent = `${event.data.player}: "${event.data.action}"`;
                break;
                
            case 'game_start':
                eventEl.textContent = `Game session ${event.data.session_number} started`;
                break;
                
            default:
                eventEl.textContent = `${capitalizeFirstLetter(event.type)} event at ${formatGameTime(event.game_time)}`;
        }
        
        eventLogEl.appendChild(eventEl);
    }
    
    // Scroll to the bottom of the log
    eventLogEl.scrollTop = eventLogEl.scrollHeight;
}

// Format game time for display
function formatGameTime(time) {
    if (!time) return 'unknown time';
    return `Day ${time.day}, ${time.hour}:${time.minute < 10 ? '0' + time.minute : time.minute}`;
}

// Create a new character from the form
function createCharacter() {
    // Get form values
    const name = document.getElementById('char-name').value;
    const race = document.getElementById('char-race').value;
    const className = document.getElementById('char-class').value;
    const level = parseInt(document.getElementById('char-level').value);
    const background = document.getElementById('char-background').value;
    
    // Get attributes
    const attributes = {
        strength: parseInt(document.getElementById('attr-str').value),
        dexterity: parseInt(document.getElementById('attr-dex').value),
        constitution: parseInt(document.getElementById('attr-con').value),
        intelligence: parseInt(document.getElementById('attr-int').value),
        wisdom: parseInt(document.getElementById('attr-wis').value),
        charisma: parseInt(document.getElementById('attr-cha').value),
    };
    
    // Create character data
    const characterData = {
        name: name,
        race: race,
        class_name: className,
        level: level,
        attributes: attributes,
        additional_info: {
            background: background
        }
    };
    
    // Show loading indicator
    showLoading();
    
    // Send to API
    fetch('/api/character/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(characterData)
    })
    .then(response => response.json())
    .then(data => {
        // Hide modal
        characterModal.style.display = 'none';
        
        // Reset form
        characterForm.reset();
        
        // Show success message
        addSystemMessage(`Character ${name} added successfully!`);
        
        // Refresh character list
        fetchGameState();
        
        // Hide loading indicator
        hideLoading();
    })
    .catch(error => {
        console.error('Error creating character:', error);
        addSystemMessage('Failed to create character.', true);
        hideLoading();
    });
}

// Save the current game
function saveGame() {
    // Show loading indicator
    showLoading();
    
    // Generate a file name based on date
    const date = new Date();
    const fileName = `game_save_${date.toISOString().split('T')[0]}.json`;
    
    // Send save request
    fetch(`/api/save_game?file_path=saves/${fileName}`)
    .then(response => response.json())
    .then(data => {
        addSystemMessage(`Game saved as ${fileName}`);
        hideLoading();
    })
    .catch(error => {
        console.error('Error saving game:', error);
        addSystemMessage('Failed to save game.', true);
        hideLoading();
    });
}

// Load a saved game
function loadGame() {
    // TODO: Implement file selection
    // For now, just load the most recent save (or a hardcoded one)
    showLoading();
    
    fetch(`/api/load_game?file_path=saves/game_save_latest.json`)
    .then(response => response.json())
    .then(data => {
        addSystemMessage('Game loaded successfully!');
        // Update the UI with the loaded game state
        updateGameState(data);
        hideLoading();
    })
    .catch(error => {
        console.error('Error loading game:', error);
        addSystemMessage('Failed to load game.', true);
        hideLoading();
    });
}

// Save notes to localStorage
function saveNotes() {
    const notes = gameNotes.value;
    localStorage.setItem('gameNotes', notes);
    addSystemMessage('Notes saved!');
}

// Fetch the current game state
function fetchGameState() {
    fetch('/api/game_state')
    .then(response => response.json())
    .then(data => {
        updateGameState(data);
    })
    .catch(error => {
        console.error('Error fetching game state:', error);
    });
}

// Show a dice roll result
function showDiceRoll(diceType) {
    // Parse the dice type (e.g., "d20" -> sides: 20)
    const sides = parseInt(diceType.substring(1));
    
    // Roll the dice
    const result = Math.floor(Math.random() * sides) + 1;
    
    // Display the result
    diceResult.innerHTML = `<span class="dice-roll">${diceType}: <strong>${result}</strong></span>`;
    
    // Send the dice roll to the chat
    addSystemMessage(`Rolled ${diceType}: ${result}`);
}

// Roll custom dice expression (e.g., "2d6+3")
function rollCustomDice() {
    const diceExpression = customDiceInput.value.trim();
    if (!diceExpression) return;
    
    // Simple expression parser (just handles NdM+K format)
    const regex = /(\d+)d(\d+)(?:([+-])(\d+))?/i;
    const match = diceExpression.match(regex);
    
    if (!match) {
        diceResult.innerHTML = '<span class="error">Invalid format. Use "NdM+K" (e.g., "2d6+3").</span>';
        return;
    }
    
    const count = parseInt(match[1]);
    const sides = parseInt(match[2]);
    const hasModifier = match[3] !== undefined;
    const modifierSign = match[3] || '+';
    const modifierValue = hasModifier ? parseInt(match[4]) : 0;
    
    if (count > 100) {
        diceResult.innerHTML = '<span class="error">Too many dice (max 100).</span>';
        return;
    }
    
    // Roll the dice
    let rolls = [];
    let total = 0;
    
    for (let i = 0; i < count; i++) {
        const roll = Math.floor(Math.random() * sides) + 1;
        rolls.push(roll);
        total += roll;
    }
    
    // Apply modifier
    if (hasModifier) {
        if (modifierSign === '+') {
            total += modifierValue;
        } else {
            total -= modifierValue;
        }
    }
    
    // Display the result
    const modifierText = hasModifier ? ` ${modifierSign} ${modifierValue}` : '';
    diceResult.innerHTML = `
        <span class="dice-roll">
            ${diceExpression}: <strong>${total}</strong><br>
            <small>[${rolls.join(', ')}]${modifierText}</small>
        </span>
    `;
    
    // Send the dice roll to the chat
    addSystemMessage(`Rolled ${diceExpression}: ${total} [${rolls.join(', ')}]${modifierText}`);
}

// Switch between tabs in the reference section
function switchTab(tabName) {
    // Hide all tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Deactivate all tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Activate the selected tab
    document.getElementById(`${tabName}-content`).classList.add('active');
    document.querySelector(`.tab-button[data-tab="${tabName}"]`).classList.add('active');
}

// Show loading indicator
function showLoading() {
    loadingOverlay.style.display = 'flex';
}

// Hide loading indicator
function hideLoading() {
    loadingOverlay.style.display = 'none';
}

// Generate a random character via WebSocket
function generateRandomCharacter() {
    // Send request to server via WebSocket
    socket.send(JSON.stringify({
        type: 'generate_character'
    }));
    
    addSystemMessage("Generating random character...");
}

// Handle random character response from server
function handleRandomCharacterResponse(character) {
    // Populate the form with the generated character
    document.getElementById('char-name').value = character.name;
    document.getElementById('char-race').value = character.race;
    document.getElementById('char-class').value = character.class_name;
    document.getElementById('char-level').value = character.level;
    document.getElementById('attr-str').value = character.attributes.strength;
    document.getElementById('attr-dex').value = character.attributes.dexterity;
    document.getElementById('attr-con').value = character.attributes.constitution;
    document.getElementById('attr-int').value = character.attributes.intelligence;
    document.getElementById('attr-wis').value = character.attributes.wisdom;
    document.getElementById('attr-cha').value = character.attributes.charisma;
    document.getElementById('char-background').value = character.additional_info.background;
    
    // Display success message
    const characterName = character.name;
    const race = character.race;
    const className = character.class_name;
    const level = character.level;
    
    addSystemMessage(`Random character generated: ${characterName} (${race} ${className}, level ${level})`);
}

// Calculate ability score modifier
function calculateModifier(score) {
    return Math.floor((score - 10) / 2);
}

// Format modifier as string with sign
function formatModifier(modifier) {
    return modifier >= 0 ? `+${modifier}` : `${modifier}`;
}

// Open character profile modal
function openCharacterProfile(characterId) {
    const character = characterData[characterId];
    if (!character) return;
    
    currentProfileCharacterId = characterId;
    
    // Set character basic info
    profileCharName.textContent = character.name;
    profileCharRace.textContent = capitalizeFirstLetter(character.race);
    profileCharClass.textContent = capitalizeFirstLetter(character.class_name);
    profileCharLevel.textContent = character.level;
    
    // Set character attributes and modifiers
    profileAttrStr.textContent = character.attributes.strength;
    profileAttrDex.textContent = character.attributes.dexterity;
    profileAttrCon.textContent = character.attributes.constitution;
    profileAttrInt.textContent = character.attributes.intelligence;
    profileAttrWis.textContent = character.attributes.wisdom;
    profileAttrCha.textContent = character.attributes.charisma;
    
    // Calculate and set modifiers
    profileAttrStrMod.textContent = formatModifier(calculateModifier(character.attributes.strength));
    profileAttrDexMod.textContent = formatModifier(calculateModifier(character.attributes.dexterity));
    profileAttrConMod.textContent = formatModifier(calculateModifier(character.attributes.constitution));
    profileAttrIntMod.textContent = formatModifier(calculateModifier(character.attributes.intelligence));
    profileAttrWisMod.textContent = formatModifier(calculateModifier(character.attributes.wisdom));
    profileAttrChaMod.textContent = formatModifier(calculateModifier(character.attributes.charisma));
    
    // Set background
    if (character.additional_info && character.additional_info.background) {
        profileCharBackground.textContent = character.additional_info.background;
    } else {
        profileCharBackground.textContent = "No background information available.";
    }
    
    // Show the modal
    characterProfileModal.style.display = 'block';
}

// Utility function to capitalize the first letter of a string
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', init);
