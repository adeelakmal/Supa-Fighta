const { sendJson } = require('./websocketUtils');

function broadcastToLobby(lobby, message) {
    console.log(`Broadcasting lobby message: ${message.type}`);
    lobby.players.forEach((player) => {
      sendJson(player.ws, message);
    });
}

module.exports = { broadcastToLobby };
  
