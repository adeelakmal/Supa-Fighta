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
  } else if (msg.type === 'validation_result') {
    if (msg.valid) {
      playerId = msg.playerId;
      joinLobby();
    } else {
      authenticatePlayer();
    }
  } else if (msg.type === 'player_created') {
    playerId = msg.playerId;
    joinLobby();
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

function createNewPlayer() {
  rl.question('Enter a username for your new account: ', (username) => {
    console.log(`✅ New player created with Username: ${username}`);
    ws.send(JSON.stringify({ type: 'create_player', username }));
  });
}

function joinLobby() {
  ws.send(JSON.stringify({ type: 'player_joined', playerId }));
  messageLoop();
}

function messageLoop() {
  rl.question('Enter command (move_left, move_right, exit): ', (msg) => {
    if (msg === 'exit') {
      rl.close();
      ws.close();
      return;
    }
    // Send as input if it's a movement command
    if (['move_left', 'move_right'].includes(msg)) {
      let i
      for (i=0;i<100;i++) {ws.send(JSON.stringify({ type: 'input', playerId, action: msg }));}
      // ws.send(JSON.stringify({ type: 'input', playerId, action: msg }));
    } else {
      ws.send(JSON.stringify({ type: 'send_message', content: msg }));
    }
    messageLoop();
  });
}