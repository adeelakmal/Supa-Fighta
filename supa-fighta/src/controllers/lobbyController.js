const pool = require('../config/db');
const { broadcastToLobby } = require("../utils/lobbyUtils");
const Player = require('../models/playerModel');

const LOBBY = { players: [] };

const HandleMessage = async (ws, msg) => {
    let data;
    try {
        data = JSON.parse(msg);
    } catch {
        return ws.send(JSON.stringify({ type: "error", message: "Invalid JSON" }));
    }

    const { type, playerId, username } = data;

    if (type === "validate_player") {
        const player_exists = await pool.query('SELECT * FROM players WHERE player_id = $1', [playerId]);
        if (player_exists.rows.length === 0 && !LOBBY.players.some(p => p.id === playerId)) {
          ws.send(JSON.stringify({ type: 'validation_result', valid: false }));
          return
        }
        const player = new Player(ws, player_exists.rows[0].player_name);
        player.id = playerId;
        LOBBY.players.push(player);
        ws.send(JSON.stringify({ type: 'validation_result', valid: true, playerId }));
        broadcastToLobby(LOBBY, { type: 'player_joined', playerId: player.id });

    } else if (type === "create_player") {
        const player = new Player(ws, username);
        pool.query(`
            INSERT INTO players (player_id, player_name, status)
            VALUES ($1, $2, 0)
        `, [player.id, player.username]);
        LOBBY.players.push(player);
        ws.send(JSON.stringify({ type: 'player_created', playerId: player.id }));
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
        // Sort and filter players based on win_streak and status
        let players = LOBBY.players.sort((p1, p2) => p2.win_streak - p1.win_streak);
        players = players.filter(p => p.status === 0);

        if (players.length < 2) return;

        const [player1, player2] = players;

        // Create a match
        const match = await pool.query(`
            INSERT INTO matches (player1_id, player2_id, timestamp, status)
            VALUES ($1, $2, NOW(), 0)
            RETURNING match_id
        `, [player1.id, player2.id]);

        // Update player statuses to in-game
        [player1, player2].forEach(p => p.status = 1);

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

module.exports = { HandleMessage, HandleClose, MatchmakePlayers, LOBBY};