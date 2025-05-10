const WebSocket = require('ws');
const crypto = require('crypto');
const pool = require('./config/db');
const { HandleMessage, HandleClose, MatchmakePlayers } = require('./controllers/lobbyController');
const Player = require('./models/playerModel');

const setupWebSocketServer = (port) => {
  const wss = new WebSocket.Server({ port: port });

  wss.on('connection', async (ws) => {
      ws.id = crypto.randomUUID();
      const player = new Player(ws);

      // Insert the player into the database
      pool.query(`
          INSERT INTO players (player_id, player_name, status)
          VALUES ($1, $2, 0)
          RETURNING *
      `, [player.id, player.username]);

      // Event Listners
      ws.on('message', message => HandleMessage(player, message));
      ws.on('close', () => HandleClose(player));
  });

  // Periodically run matchmaking
  setInterval(async () => {
      await MatchmakePlayers();
  }, 5000);
  console.log('WebSocket server is listening on ws://localhost:8080');
};

module.exports = setupWebSocketServer;