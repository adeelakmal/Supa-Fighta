const WebSocket = require('ws');
const readline = require('readline');

const ws = new WebSocket('ws://localhost:8080');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

let lobbyId = null;

ws.on('open', () => {
  console.log('Connected to WebSocket server.');
  mainMenu();
});

ws.on('message', (data) => {
  const msg = JSON.parse(data);
  if (msg.type === 'player_joined') {
    console.log(`👤 Player joined: ${msg.playerId}`);
  } else if (msg.type === 'player_left') {
    console.log(`👋 Player left: ${msg.playerId}`);
  } else if(msg.type === "match_created"){
    console.log(`🎮 We've got a game: ${msg.player1} vs ${msg.player2}`);
  }else if (msg.type === 'error') {
    console.error(`❌ Error: ${msg.message}`);
  }
});

function mainMenu() {
    ws.send(JSON.stringify({ type: 'player_joined', lobbyId }));
    messageLoop()
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
