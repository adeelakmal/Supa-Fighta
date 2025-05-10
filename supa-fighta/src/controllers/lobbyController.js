const pool = require('../config/db');
const { broadcastToLobby } = require("../utils/lobbyUtils");

const LOBBY = { players: [] };

const HandleMessage = (ws, msg) => {
    let data;
    try {
        data = JSON.parse(msg);
    } catch {
        return ws.send(JSON.stringify({ type: "error", message: "Invalid JSON" }));
    }

    const { type, content } = data;

    if (type === "player_joined") {
        LOBBY.players.push(ws);
        console.log(LOBBY)
        broadcastToLobby(LOBBY, { type: 'player_joined', playerId: ws.id });
    }
};

const HandleClose = (ws) => {
    // Remove the player from the lobby
    LOBBY.players = LOBBY.players.filter(p => p !== ws);

    // Notify the lobby that the player has left
    broadcastToLobby(LOBBY, { type: 'player_left', playerId: ws.id });
};

const MatchmakePlayers = async () => {
    try {
        // Fetch players sorted by max_streak where status = 0 (waiting)
        const players = await pool.query(`
            SELECT * FROM players
            WHERE status = 0
            ORDER BY max_streak ASC
        `);

        if (players.rows.length < 2) {
            return;
        }

        // Pair the first two players
        const [player1, player2] = players.rows;

        // Create a match
        const match = await pool.query(`
            INSERT INTO matches (player1_id, player2_id, timestamp, status)
            VALUES ($1, $2, NOW(), 0)
            RETURNING match_id
        `, [player1.player_id, player2.player_id]);

        // Update player statuses to in-game (1)
        await pool.query(`
            UPDATE players
            SET status = 1
            WHERE player_id IN ($1, $2)
        `, [player1.player_id, player2.player_id]);

        console.log(`Match created: ${match.rows[0].match_id}`);

        // Notify the lobby about the new match
        broadcastToLobby(LOBBY, {
            type: 'match_created',
            matchId: match.rows[0].match_id,
            player1: player1.player_id,
            player2: player2.player_id,
        });
    } catch (error) {
        console.error("Error during matchmaking:", error);
    }
};

module.exports = { HandleMessage, HandleClose, MatchmakePlayers };