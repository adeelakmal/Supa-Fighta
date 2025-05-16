const WebSocket = require('ws');
const crypto = require('crypto');
const pool = require('./config/db');
const { HandleMessage, HandleClose, MatchmakePlayers, LOBBY } = require('./controllers/lobbyController');
const Player = require('./models/playerModel');

const setupWebSocketServer = (port) => {
  const wss = new WebSocket.Server({ port: port });

  wss.on('connection', async (ws) => {
    ws.id = crypto.randomUUID();

    // Validate or create a new player
    ws.on('message', async (message) => {
      const data = JSON.parse(message);

      if (data.type === 'validate_player') {
        const result = await pool.query('SELECT * FROM players WHERE player_id = $1', [data.playerId]);
        if (result.rows.length > 0 && !LOBBY.players.some(p => p.id === data.playerId)) {
          const player = new Player(ws, result.rows[0].player_name);
          player.id = data.playerId;
          LOBBY.players.push(player);
          ws.send(JSON.stringify({ type: 'validation_result', valid: true, playerId: data.playerId }));
          setupEventListeners(ws, player);
        } else {
          ws.send(JSON.stringify({ type: 'validation_result', valid: false }));
        }
      } else if (data.type === 'create_player') {
        const player = new Player(ws, data.username);
        player.id = data.playerId;

        await pool.query(`
          INSERT INTO players (player_id, player_name, status)
          VALUES ($1, $2, 0)
        `, [player.id, player.username]);

        LOBBY.players.push(player);
        ws.send(JSON.stringify({ type: 'player_created', playerId: player.id }));
        setupEventListeners(ws, player);
      }
    });
  });

  // Periodically run matchmaking
  setInterval(async () => {
    await MatchmakePlayers();
  }, 5000);

  console.log('WebSocket server is listening on ws://localhost:8080');
};

function setupEventListeners(ws, player) {
  // Event Listeners
  ws.on('message', (message) => HandleMessage(player, message));
  ws.on('close', () => HandleClose(player));
}

module.exports = setupWebSocketServer;