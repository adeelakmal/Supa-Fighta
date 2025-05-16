const WebSocket = require('ws');
const readline = require('readline');

const ws = new WebSocket('ws://localhost:8080');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

let lobbyId = null;
let playerId = null;

ws.on('open', () => {
  console.log('Connected to WebSocket server.');
  authenticatePlayer();
});

ws.on('message', (data) => {
  const msg = JSON.parse(data);
  if (msg.type === 'player_joined') {
    console.log(`👤 Player joined: ${msg.playerId}`);
  } else if (msg.type === 'player_left') {
    console.log(`👋 Player left: ${msg.playerId}`);
  } else if (msg.type === 'match_created') {
    console.log(`🎮 We've got a game: ${msg.player1} vs ${msg.player2}`);
  } else if (msg.type === 'error') {
    console.error(`❌ Error: ${msg.message}`);
  }
});

function authenticatePlayer() {
  rl.question('Enter your player_id to log in or type "new" to create a new account: ', (input) => {
    if (input.toLowerCase() === 'new') {
      createNewPlayer();
    } else {
      ws.send(JSON.stringify({ type: 'validate_player', playerId: input }));
    }
  });
}

ws.on('message', (data) => {
  const msg = JSON.parse(data);
  if (msg.type === 'validation_result') {
    if (msg.valid) {
      playerId = msg.playerId;
      console.log(`✅ Successfully logged in as player_id: ${playerId}`);
      joinLobby();
    } else {
      console.log('❌ Invalid player_id. Please try again.');
      authenticatePlayer();
    }
  }
});

function createNewPlayer() {
  rl.question('Enter a username for your new account: ', (username) => {
    console.log(`✅ New player created with Username: ${username}`);
    ws.send(JSON.stringify({ type: 'create_player', username }));
    joinLobby();
  });
}

function joinLobby() {
  ws.send(JSON.stringify({ type: 'player_joined', playerId }));
  console.log(`✅ Successfully joined the lobby as player_id: ${playerId}`);
  messageLoop();
}

function messageLoop() {
  rl.question('Enter message (or "exit" to quit): ', (msg) => {
    if (msg === 'exit') {
      rl.close();
      ws.close();
      return;
    }
    ws.send(JSON.stringify({ type: 'send_message', content: msg }));
    messageLoop();
  });
}