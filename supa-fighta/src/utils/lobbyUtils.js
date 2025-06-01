function broadcastToLobby(lobby, message) {
    const json = JSON.stringify(message);
    console.log(`Broadcasting to lobby: ${json}`);
    lobby.players.forEach((player) => {
      if (player.ws.readyState === player.ws.OPEN) {
        player.ws.send(json);
      }
    });
  }
  
  module.exports = { broadcastToLobby };
  