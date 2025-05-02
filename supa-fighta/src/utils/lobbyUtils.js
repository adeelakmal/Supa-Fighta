function broadcastToLobby(lobby, message) {
    const json = JSON.stringify(message);
    lobby.players.forEach((ws) => {
      if (ws.readyState === ws.OPEN) {
        ws.send(json);
      }
    });
  }
  
  module.exports = { broadcastToLobby };
  