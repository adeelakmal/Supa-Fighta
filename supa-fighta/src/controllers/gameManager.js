const Game = require('./gameController');

class GameManager {
    constructor() {
        this.activeGames = {}; // matchId -> Game instance
        this.playerToGame = {}; // playerId -> matchId
    }

    createGame(matchId, player1, player2) {
        const game = new Game(matchId, player1, player2);
        this.activeGames[matchId] = game;
        this.playerToGame[player1.id] = matchId;
        this.playerToGame[player2.id] = matchId;
        game.start();
        return game;
    }

    routeInput(playerId, input) {
        const matchId = this.playerToGame[playerId];
        if (matchId && this.activeGames[matchId]) {
            this.activeGames[matchId].receiveInput(playerId, input);
        }
    }

    endGame(matchId) {
        delete this.activeGames[matchId];
        for (const pid in this.playerToGame) {
            if (this.playerToGame[pid] === matchId) {
                delete this.playerToGame[pid];
            }
        }
    }
}

module.exports = new GameManager();