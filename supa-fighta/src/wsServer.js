const WebSocket = require('ws');
const crypto = require('crypto');
const gameManager = require('./controllers/gameManager');
const { HandleMessage, HandleClose, MatchmakePlayers, LOBBY } = require('./controllers/lobbyController');

const VALID_INPUTS = new Set([
  'idle',
  'walk_left',
  'walk_right',
  'dash_left',
  'dash_right',
  'punch',
  'parry',
  'parry-hit',
  'parried',
  'hurt',
  'win',
  'wait'
]);

const safeSend = (ws, message) => {
  if (ws.readyState !== WebSocket.OPEN) return;

  try {
    ws.send(JSON.stringify(message));
  } catch (err) {
    console.error(`Failed to send message to player ${ws.id}:`, err);
  }
};

const validateSnapshot = (snapshot) => {
  const player = snapshot?.player;

  if (!player || !Number.isFinite(player.x) || !Array.isArray(player.history)) {
    return false;
  }

  if (player.history.length > 120) {
    return false;
  }

  return player.history.every(input => VALID_INPUTS.has(input));
};

const setupWebSocketServer = (port) => {
  const wss = new WebSocket.Server({ port, maxPayload: 64 * 1024 });

  wss.on('connection', (ws) => {
    ws.id = crypto.randomUUID();
    ws.isAlive = true;

    ws.on('pong', () => {
      ws.isAlive = true;
    });

    ws.on('message', async (message) => {
      try {
        const data = JSON.parse(message.toString());

        if (!data || typeof data !== 'object' || Array.isArray(data)) {
          safeSend(ws, { type: 'error', message: 'Invalid message format.' });
          return;
        }

        if (data.type === 'snapshot') {
          if (!validateSnapshot(data.snapshot)) {
            safeSend(ws, { type: 'error', message: 'Invalid snapshot.' });
            return;
          }

          // Use the identity assigned to this socket instead of trusting client input.
          gameManager.routeInput(LOBBY, ws.id, data.matchId, data.snapshot);
          return;
        }

        await HandleMessage(ws, data);
      } catch (err) {
        console.error(`Error handling message from player ${ws.id}:`, err);
        safeSend(ws, { type: 'error', message: 'Invalid message.' });
      }
    });

    ws.on('close', async (code, reason) => {
      console.log(`WebSocket closed for player ${ws.id}. Code: ${code}, Reason: ${reason}`);
      try {
        await HandleClose(ws);
      } catch (err) {
        console.error(`Error closing player ${ws.id}:`, err);
      }
    });

    ws.on('error', (err) => {
      console.error(`WebSocket error for player ${ws.id}:`, err);
    });
  });

  // Periodically run matchmaking
  const matchmakingInterval = setInterval(() => {
    void MatchmakePlayers();
  }, 5000);

  const heartbeatInterval = setInterval(() => {
    wss.clients.forEach((ws) => {
      if (ws.readyState !== WebSocket.OPEN) return;

      if (!ws.isAlive) {
        ws.terminate();
        return;
      }

      ws.isAlive = false;
      try {
        ws.ping();
      } catch (err) {
        console.error(`Failed to ping player ${ws.id}:`, err);
        ws.terminate();
      }
    });
  }, 30000);

  wss.on('close', () => {
    clearInterval(matchmakingInterval);
    clearInterval(heartbeatInterval);
  });

  wss.on('error', (err) => {
    console.error('WebSocket server error:', err);
  });

  console.log(`WebSocket server is listening on port ${port}`);
};

module.exports = setupWebSocketServer;
