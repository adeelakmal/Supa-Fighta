const pool = require('../config/db');
const WebSocket = require('ws');
const { broadcastToLobby } = require("../utils/lobbyUtils");
const Player = require('../models/playerModel');
const PlayerRepository = require('../repositories/playerRepository')
const MatchesRepository = require('../repositories/matchesRepository')
const gameManager = require('./gameManager');
const { validatePlayerName } = require('../utils/playerNameUtils');

const LOBBY = { players: [] };
const playerRepository = new PlayerRepository(pool)
const matchesRepository = new MatchesRepository(pool)
let matchmakingInProgress = false;

const sendNameRejected = (ws, message) => {
    if (ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ type: 'name_rejected', message }));
};

const validateRequestedName = (ws, username) => {
    const result = validatePlayerName(username);
    if (!result.valid) {
        sendNameRejected(ws, result.message);
        return null;
    }

    return result;
};

const beginRegistration = (ws) => {
    if (ws.playerRegistered || ws.registrationInProgress) {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'error',
                message: 'This connection already has a player.'
            }));
        }
        return false;
    }

    ws.registrationInProgress = true;
    return true;
};

const HandleMessage = async (ws, data) => {
    const { type, playerId, username } = data;

    if (type === "validate_player") {
        if (!beginRegistration(ws)) return;

        try {
            const player_exists = await playerRepository.getPlayerById(playerId)
            if (player_exists.rows.length === 0) {
                ws.send(JSON.stringify({ type: 'validation_result', valid: false }));
                return
            }
            if (LOBBY.players.some(p => p.id === playerId)) {
                throw Error("Player already in lobby");
            }
            if (ws.readyState !== WebSocket.OPEN) return;

            const savedPlayerName = player_exists.rows[0].player_name;
            const requestedPlayerName = typeof username === 'string'
                ? username
                : savedPlayerName;
            const validatedName = validateRequestedName(
                ws,
                requestedPlayerName
            );
            if (!validatedName) return;

            if (validatedName.name !== savedPlayerName) {
                await playerRepository.updatePlayerName(
                    playerId,
                    validatedName.name
                );
            }
            if (ws.readyState !== WebSocket.OPEN) return;

            ws.id = playerId
            const player = new Player(ws, validatedName.name);
            player.id = playerId;
            LOBBY.players.push(player);
            ws.playerRegistered = true;
            ws.send(JSON.stringify({
                type: 'validation_result',
                valid: true,
                playerId,
                username: player.username
            }));
            broadcastToLobby(LOBBY, { type: 'player_joined', playerId: player.id });
        } finally {
            ws.registrationInProgress = false;
        }

    } else if (type === "create_player") {
        if (!beginRegistration(ws)) return;

        try {
            const validatedName = validateRequestedName(ws, username);
            if (!validatedName) return;

            const player = new Player(ws, validatedName.name);
            await playerRepository.addNewPlayer(player)
            if (ws.readyState !== WebSocket.OPEN) return;

            LOBBY.players.push(player);
            ws.playerRegistered = true;
            ws.send(JSON.stringify({
                type: 'player_created',
                playerId: player.id,
                username: player.username
            }));
            broadcastToLobby(LOBBY, { type: 'player_joined', playerId: player.id });
        } finally {
            ws.registrationInProgress = false;
        }
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

        const game = gameManager.createGame(match_id, player1, player2);
        if (!game) return;

        broadcastToLobby(LOBBY, {
            type: 'match_created',
            matchId: match_id,
            player1: player1.id,
            player2: player2.id,
            player1Name: player1.username,
            player2Name: player2.username,
            countdownSeconds: game.countdownSeconds,
            startsAt: game.startsAt,
            serverTime: Date.now()
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
