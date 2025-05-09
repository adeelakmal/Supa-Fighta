// Initialize a server here for websockets 
const WebSocket = require('ws');
const crypto = require('crypto');
const pool = require('./config/db');
const { HandleMessage, HandleClose, MatchmakePlayers } = require('./controllers/lobbyController');
const Player = require('./models/playerModel'); // Import the Player class

const setupWebSocketServer = (port) => {
  const wss = new WebSocket.Server({ port: port });

  wss.on('connection', async (ws) => {
      ws.id = crypto.randomUUID();

      // Create a Player instance
      const player = new Player(ws, "player");

      // Insert the player into the database
      let result = await pool.query(`
          INSERT INTO players (player_id, player_name, status)
          VALUES ($1, $2, 0)
          RETURNING *
      `, [player.id, player.username]);

      // Pass the Player instance to the handlers
      ws.on('message', message => HandleMessage(player, message));
      ws.on('close', () => HandleClose(player));
  });

  // Periodically run matchmaking
  setInterval(() => {
      MatchmakePlayers();
  }, 5000); // Run matchmaking every 5 seconds
  console.log('WebSocket server is listening on ws://localhost:8080');
};

module.exports = setupWebSocketServer;