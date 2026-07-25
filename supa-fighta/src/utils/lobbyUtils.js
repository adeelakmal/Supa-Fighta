const WebSocket = require('ws');

function broadcastToLobby(lobby, message) {
    const json = JSON.stringify(message);
    console.log(`Broadcasting to lobby: ${json}`);
    lobby.players.forEach((player) => {
      if (player.ws.readyState !== WebSocket.OPEN) return;

      try {
        player.ws.send(json);
      } catch (err) {
        console.error(`Failed to broadcast to player ${player.id}:`, err);
      }
    });
}

module.exports = { broadcastToLobby };
  
