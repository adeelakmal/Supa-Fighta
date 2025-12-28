const pool = require('../config/db');
const { broadcastToLobby } = require("../utils/lobbyUtils");
const Player = require('../models/playerModel');
const PlayerRepository = require('../repositories/playerRepository')
const MatchesRepository = require('../repositories/matchesRepository')
const gameManager = require('./gameManager');

const LOBBY = { players: [] };
const playerRepository = new PlayerRepository(pool)
const matchesRepository = new MatchesRepository(pool)

const HandleMessage = async (ws, msg) => {
    let data;
    try {
        data = JSON.parse(msg);
    } catch {
        return ws.send(JSON.stringify({ type: "error", message: "Invalid JSON" }));
    }

    const { type, playerId, username } = data;

    if (type === "validate_player") {
        const player_exists = await playerRepository.getPlayerById(playerId)
        if (player_exists.rows.length === 0 && !LOBBY.players.some(p => p.id === playerId)) {
          ws.send(JSON.stringify({ type: 'validation_result', valid: false }));
          return
        }
        // if (LOBBY.players.some(p => p.id === playerId)) {
        //   ws.send(JSON.stringify({ type: 'player_in_lobby', message: 'Player already in lobby' }));
        //   return
        // }
        ws.id = playerId
        const player = new Player(ws, player_exists.rows[0].player_name);
        player.id = playerId;
        LOBBY.players.push(player);
        ws.send(JSON.stringify({ type: 'validation_result', valid: true, playerId }));
        broadcastToLobby(LOBBY, { type: 'player_joined', playerId: player.id });

    } else if (type === "create_player") {
        const player = new Player(ws, username);
        playerRepository.addNewPlayer(player)
        LOBBY.players.push(player);
        ws.send(JSON.stringify({ type: 'player_created', playerId: player.id }));
        broadcastToLobby(LOBBY, { type: 'player_joined', playerId: player.id });
    }
};

const HandleClose = async (ws) => {
    const player = LOBBY.players.find(p => p.id === ws.id);
    await playerRepository.updatePlayerStats(player);
    // Remove the player from the lobby
    LOBBY.players = LOBBY.players.filter(p => p.id !== ws.id);   
    broadcastToLobby(LOBBY, { type: 'player_left', playerId: ws.id });
};

const MatchmakePlayers = async () => {
    try {
        
        // Sort and filter players based on win_streak and status
        const seen = new Set(); // To avoid duplicate matches
        let players = LOBBY.players
            .sort((p1, p2) => p2.win_streak - p1.win_streak)
            .filter(p => p.status === 0 && !seen.has(p.id) && seen.add(p.id));

        if (players.length < 2) return;

        const [player1, player2] = players;
        
        // Create a match
        const match_id = await matchesRepository.createMatch(player1, player2)
        const matchPlayers = [player1, player2]
        // Update player statuses to in-game
        matchPlayers.forEach( p => {
            p.status = 1
            p.match_id = match_id
        });

        console.log(`Match created: ${match_id}`);

        gameManager.createGame(match_id, player1, player2);

        broadcastToLobby(LOBBY, {
            type: 'match_created',
            matchId: match_id,
            player1: player1.id,
            player2: player2.id,
        });
    } catch (error) {
        console.error("Error during matchmaking:", error);
    }
};

module.exports = { HandleMessage, HandleClose, MatchmakePlayers, LOBBY};