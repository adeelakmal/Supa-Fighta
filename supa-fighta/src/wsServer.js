const WebSocket = require('ws');
const crypto = require('crypto');
const pool = require('./config/db');
const { HandleMessage, HandleClose, MatchmakePlayers} = require('./controllers/lobbyController');
const Player = require('./models/playerModel');

const setupWebSocketServer = (port) => {
  const wss = new WebSocket.Server({ port: port });

  wss.on('connection', (ws) => {
    ws.id = crypto.randomUUID();
    ws.on('message', (message) => HandleMessage(ws, message));
    ws.on('close', () => HandleClose(ws));
  });

  // Periodically run matchmaking
  setInterval(async () => {
    await MatchmakePlayers();
  }, 5000);

  console.log('WebSocket server is listening on ws://localhost:8080');
};

module.exports = setupWebSocketServer;