const pool = require('../config/db');
const WebSocket = require('ws');
const { broadcastToLobby } = require("../utils/lobbyUtils");
const Player = require('../models/playerModel');
const PlayerRepository = require('../repositories/playerRepository')
const MatchesRepository = require('../repositories/matchesRepository')
const gameManager = require('./gameManager');
const { validatePlayerName } = require('../utils/playerNameUtils');
const { sendJson } = require('../utils/websocketUtils');
const {
    authenticatePlayer,
    createPlayerToken,
    hashPlayerToken
} = require('../utils/playerAuth');

const LOBBY = { players: [] };
const playerRepository = new PlayerRepository(pool)
const matchesRepository = new MatchesRepository(pool)
let matchmakingInProgress = false;

const sendNameRejected = (ws, message) => {
    sendJson(ws, { type: 'name_rejected', message });
};

const sendInvalidCredentials = (ws) => {
    sendJson(ws, { type: 'validation_result', valid: false });
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
            sendJson(ws, {
                type: 'error',
                message: 'This connection already has a player.'
            });
        }
        return false;
    }

    ws.registrationInProgress = true;
    return true;
};

const HandleMessage = async (ws, data) => {
    const { type, playerId, playerToken, username } = data;

    if (type === "validate_player") {
        if (!beginRegistration(ws)) return;

        try {
            const playerRecord = await authenticatePlayer(
                playerRepository,
                playerId,
                playerToken
            );
            if (!playerRecord) {
                sendInvalidCredentials(ws);
                return
            }
            const existingPlayer = LOBBY.players.find(p => p.id === playerId);
            if (existingPlayer && existingPlayer.ws !== ws) {
                // A freshly authenticated connection replaces a socket whose
                // close event may still be in flight.
                existingPlayer.ws.terminate();
                await HandleClose(existingPlayer.ws);
            }
            if (ws.readyState !== WebSocket.OPEN) return;

            const savedPlayerName = playerRecord.player_name;
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
            sendJson(ws, {
                type: 'validation_result',
                valid: true,
                playerId,
                username: player.username
            });
            broadcastToLobby(LOBBY, { type: 'player_joined', playerId: player.id });
        } finally {
            ws.registrationInProgress = false;
        }

    } else if (type === "create_player") {
        if (!beginRegistration(ws)) return;

        try {
            if (ws.allowPlayerCreation && !ws.allowPlayerCreation()) {
                sendJson(ws, {
                    type: 'error',
                    message: 'Player creation limit reached. Try again later.'
                });
                return;
            }

            const validatedName = validateRequestedName(ws, username);
            if (!validatedName) return;

            const player = new Player(ws, validatedName.name);
            const playerToken = createPlayerToken();
            await playerRepository.addNewPlayer(
                player,
                hashPlayerToken(playerToken)
            )
            if (ws.readyState !== WebSocket.OPEN) return;

            LOBBY.players.push(player);
            ws.playerRegistered = true;
            sendJson(ws, {
                type: 'player_created',
                playerId: player.id,
                playerToken,
                username: player.username
            });
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
        sendJson(ws, { type: 'error', message: 'Unknown message type.' });
    }
};

const HandleClose = async (ws) => {
    // Match the socket, not just the public player ID. A delayed close event
    // from a replaced connection must not remove the new connection.
    const player = LOBBY.players.find(p => p.ws === ws);
    if (!player) {
        return;
    }

    if (!player.id) {
        console.error(`Player object is missing an ID:`, player);
        return;
    }

    // Remove first so matchmaking cannot select a disconnected player while
    // database work is still pending.
    LOBBY.players = LOBBY.players.filter(p => p.ws !== ws);
    console.log(`Current lobby players:`, LOBBY.players.map(p => p.id));
    broadcastToLobby(LOBBY, { type: 'player_left', playerId: player.id });

    await gameManager.handleDisconnect(player.id);

    try {
        await playerRepository.updatePlayerStats(player);
    } catch (err) {
        console.error(`Failed to update player stats for ${player.id}:`, err);
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
            matchDurationSeconds: game.durationSeconds,
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
