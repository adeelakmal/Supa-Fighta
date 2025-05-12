const pool = require('../config/db');
const { broadcastToLobby } = require("../utils/lobbyUtils");

const LOBBY = { players: [] };

const HandleMessage = (player, msg) => {
    // Hanldes broadcasting messages for players joining the lobby
    let data;
    try {
        data = JSON.parse(msg);
    } catch {
        return player.ws.send(JSON.stringify({ type: "error", message: "Invalid JSON" }));
    }

    const { type } = data;

    if (type === "player_joined") {
        LOBBY.players.push(player);
        broadcastToLobby(LOBBY, { type: 'player_joined', playerId: player.id });
    }
};

const HandleClose = (ws) => {
    // Remove the player from the lobby
    LOBBY.players = LOBBY.players.filter(p => p !== ws);
    broadcastToLobby(LOBBY, { type: 'player_left', playerId: ws.id });
};

const MatchmakePlayers = async () => {
    try {
        // Sort and filter players on bases of win_streak and status
        let players = LOBBY.players.sort((p1,p2) => p2.win_streak - p1.win_streak)
        players = players.filter(p => p.status === 0)

        if (players.length < 2) {
            return;
        }
        const [player1, player2] = players;

        // Create a match
        const match = await pool.query(`
            INSERT INTO matches (player1_id, player2_id, timestamp, status)
            VALUES ($1, $2, NOW(), 0)
            RETURNING match_id
        `, [player1.id, player2.id]);

        // Update player statuses to in-game
        [player1,player2].forEach(p => p.status = 1)

        console.log(`Match created: ${match.rows[0].match_id}`);

        broadcastToLobby(LOBBY, {
            type: 'match_created',
            matchId: match.rows[0].match_id,
            player1: player1.id,
            player2: player2.id,
        });
    } catch (error) {
        console.error("Error during matchmaking:", error);
    }
};

module.exports = { HandleMessage, HandleClose, MatchmakePlayers };