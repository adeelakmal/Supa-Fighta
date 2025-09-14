const WebSocket = require('ws');
const crypto = require('crypto');
const gameManager = require('./controllers/gameManager');
const { HandleMessage, HandleClose, MatchmakePlayers } = require('./controllers/lobbyController');


const setupWebSocketServer = (port) => {
  const wss = new WebSocket.Server({ port: port });

  wss.on('connection', (ws) => {
    ws.id = crypto.randomUUID();
    ws.on('message', (message) => {
      let data;
      try {
        data = JSON.parse(message);
      } catch {
        console.error('Failed to parse message:', message.toString());
        console.error('Parse error:', err);
        ws.send(JSON.stringify({ type: 'error', message: 'Invalid JSON format.' }));
        return;
      }

      // Handle input messages for the game
      if ( data.type === "snapshot") {
        // TODO: Validate and process the snapshot
        console.log("Snapshot received:", data);
        ws.send(JSON.stringify({ type: 'ack', message: 'valid state' }));
      }

      HandleMessage(ws, message);
    });

    ws.on('close', () => HandleClose(ws));
  });

  // Periodically run matchmaking
  setInterval(async () => {
    await MatchmakePlayers();
  }, 5000);

  console.log('WebSocket server is listening on ws://localhost:8080');
};

module.exports = setupWebSocketServer;