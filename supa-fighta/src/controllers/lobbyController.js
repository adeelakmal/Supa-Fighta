const { broadcastToLobby } = require("../utils/lobbyUtils");

const LOBBY = {players: []};

const HandleMessage = (ws, msg) => {
    let data;
    try {
        data = JSON.parse(msg);
    } catch {
        return ws.send(JSON.stringify({type: "error", message: "Invalid JSON"}))
    }

    const { type, content } = data;

    if (type === "player_joined") {
        LOBBY.players.push(ws)
        broadcastToLobby(LOBBY, { type: 'player_joined', playerId: ws.id })
    }
}

const HandleClose = (ws) => {
    LOBBY.players = LOBBY.players.filter(p => p !== ws);
    broadcastToLobby(LOBBY, { type: 'player_left', playerId: ws.id });
}

module.exports = {HandleMessage, HandleClose}