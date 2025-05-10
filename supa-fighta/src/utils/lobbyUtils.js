function broadcastToLobby(lobby, message) {
    const json = JSON.stringify(message);
    console.log(`Broadcasting to lobby: ${json}`);
    lobby.players.forEach((ws) => {
      if (ws.readyState === ws.OPEN) {
        ws.send(json);
      }
    });
  }
  
  module.exports = { broadcastToLobby };
  