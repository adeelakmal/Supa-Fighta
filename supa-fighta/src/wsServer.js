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
      if (data.type === 'input' && data.playerId && data.action) {
        gameManager.routeInput(data.playerId, data.action);
        return;
      }

      // Otherwise, handle as a lobby message
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