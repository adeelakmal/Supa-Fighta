const WebSocket = require('ws');
const crypto = require('crypto');
const gameManager = require('./controllers/gameManager');
const { HandleMessage, HandleClose, MatchmakePlayers, LOBBY } = require('./controllers/lobbyController');
const { sendJson } = require('./utils/websocketUtils');
const {
  WebSocketSecurity,
  getClientIp,
  validateSnapshot
} = require('./utils/websocketSecurity');

const REGISTRATION_DEADLINE_MS = 10 * 1000;

const setupWebSocketServer = (port) => {
  const wss = new WebSocket.Server({ port, maxPayload: 64 * 1024 });
  const security = new WebSocketSecurity();

  wss.on('connection', (ws, request) => {
    const clientIp = getClientIp(request);
    if (!security.openConnection(clientIp)) {
      ws.terminate();
      return;
    }

    ws.id = crypto.randomUUID();
    ws.isAlive = true;
    ws.clientIp = clientIp;
    ws.allowPlayerCreation = () => security.allowPlayerCreation(clientIp);
    ws.registrationTimer = setTimeout(() => {
      if (!ws.playerRegistered) {
        ws.terminate();
      }
    }, REGISTRATION_DEADLINE_MS);

    ws.on('pong', () => {
      ws.isAlive = true;
    });

    ws.on('message', async (message) => {
      if (!security.allowMessage(ws)) {
        ws.terminate();
        return;
      }

      try {
        const data = JSON.parse(message.toString());

        if (!data || typeof data !== 'object' || Array.isArray(data)) {
          sendJson(ws, { type: 'error', message: 'Invalid message format.' });
          return;
        }

        if (data.type === 'snapshot') {
          if (!validateSnapshot(data.snapshot)) {
            sendJson(ws, { type: 'error', message: 'Invalid snapshot.' });
            return;
          }

          // Use the identity assigned to this socket instead of trusting client input.
          gameManager.routeInput(LOBBY, ws.id, data.snapshot);
          return;
        }

        await HandleMessage(ws, data);
      } catch (err) {
        console.error(`Error handling message from player ${ws.id}:`, err);
        sendJson(ws, { type: 'error', message: 'Invalid message.' });
      }
    });

    ws.on('close', async (code, reason) => {
      clearTimeout(ws.registrationTimer);
      security.closeConnection(clientIp);
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
