const pool = require('../config/db');
const WebSocket = require('ws');
const { broadcastToLobby } = require("../utils/lobbyUtils");
const Player = require('../models/playerModel');
const PlayerRepository = require('../repositories/playerRepository')
const MatchesRepository = require('../repositories/matchesRepository')
const gameManager = require('./gameManager');

const LOBBY = { players: [] };
const playerRepository = new PlayerRepository(pool)
const matchesRepository = new MatchesRepository(pool)
let matchmakingInProgress = false;

const HandleMessage = async (ws, data) => {
    const { type, playerId, username } = data;

    if (type === "validate_player") {
        console.log(data)
        const player_exists = await playerRepository.getPlayerById(playerId)
        if (player_exists.rows.length === 0) {
            ws.send(JSON.stringify({ type: 'validation_result', valid: false }));
            return
        }
        if (LOBBY.players.some(p => p.id === playerId)) {
            throw Error("Player already in lobby");
        }
        if (ws.readyState !== WebSocket.OPEN) return;

        ws.id = playerId
        const player = new Player(ws, player_exists.rows[0].player_name);
        player.id = playerId;
        LOBBY.players.push(player);
        ws.send(JSON.stringify({ type: 'validation_result', valid: true, playerId }));
        broadcastToLobby(LOBBY, { type: 'player_joined', playerId: player.id });

    } else if (type === "create_player") {
        const player = new Player(ws, username);
        await playerRepository.addNewPlayer(player)
        if (ws.readyState !== WebSocket.OPEN) return;

        LOBBY.players.push(player);
        ws.send(JSON.stringify({ type: 'player_created', playerId: player.id }));
        broadcastToLobby(LOBBY, { type: 'player_joined', playerId: player.id });
    } else if (type === "player_rejoined") {
        const player = LOBBY.players.find(p => p.id === ws.id);
        if (!player) {
            throw Error("Player not found in lobby");
        }
        player.status = 0;
        player.match_id = null;
    } else {
        ws.send(JSON.stringify({ type: 'error', message: 'Unknown message type.' }));
    }
};

const HandleClose = async (ws) => {
    const player = LOBBY.players.find(p => p.id === ws.id);
    if (!player) {
        console.warn(`Player with ID ${ws.id} not found in the lobby.`);
        return;
    }

    if (!player.id) {
        console.error(`Player object is missing an ID:`, player);
        return;
    }

    // Remove first so matchmaking cannot select a disconnected player while
    // database work is still pending.
    LOBBY.players = LOBBY.players.filter(p => p.id !== ws.id);
    console.log(`Current lobby players:`, LOBBY.players.map(p => p.id));
    broadcastToLobby(LOBBY, { type: 'player_left', playerId: ws.id });

    await gameManager.handleDisconnect(ws.id);

    try {
        await playerRepository.updatePlayerStats(player);
    } catch (err) {
        console.error(`Failed to update player stats for ${ws.id}:`, err);
    }
};

const MatchmakePlayers = async () => {
    if (matchmakingInProgress) return;
    matchmakingInProgress = true;

    let matchPlayers = [];

    try {
        // Sort and filter players based on win_streak and status
        const seen = new Set(); // To avoid duplicate matches
        let players = LOBBY.players
            .sort((p1, p2) => p2.win_streak - p1.win_streak)
            .filter(p =>
                p.status === 0
                && p.ws.readyState === WebSocket.OPEN
                && !seen.has(p.id)
                && seen.add(p.id)
            );

        if (players.length < 2) return;

        const [player1, player2] = players;
        matchPlayers = [player1, player2];

        // Reserve these players while the database creates the match.
        matchPlayers.forEach(player => {
            player.status = 2;
        });

        // Create a match
        const match_id = await matchesRepository.createMatch(player1, player2)

        const playersStillConnected = matchPlayers.every(player =>
            LOBBY.players.includes(player) && player.ws.readyState === WebSocket.OPEN
        );

        if (!playersStillConnected) {
            matchPlayers.forEach(player => {
                if (LOBBY.players.includes(player) && player.status === 2) {
                    player.status = 0;
                }
            });
            await matchesRepository.updateMatchStatus(null, match_id);
            return;
        }

        // Update player statuses to in-game
        matchPlayers.forEach( p => {
            p.status = 1
            p.match_id = match_id
        });

        console.log(`Match created: ${match_id}`);

        const gameStarted = gameManager.createGame(match_id, player1, player2);
        if (!gameStarted) return;

        broadcastToLobby(LOBBY, {
            type: 'match_created',
            matchId: match_id,
            player1: player1.id,
            player2: player2.id,
        });
    } catch (error) {
        console.error("Error during matchmaking:", error);
        matchPlayers.forEach(player => {
            if (LOBBY.players.includes(player) && player.status === 2) {
                player.status = 0;
            }
        });
    } finally {
        matchmakingInProgress = false;
    }
};

module.exports = { HandleMessage, HandleClose, MatchmakePlayers, LOBBY};
