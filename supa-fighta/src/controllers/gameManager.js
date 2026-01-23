const Game = require('./gameController');

class GameManager {
    constructor() {
        this.activeGames = [];
    }

    createGame(matchId, player1, player2) {
        const game = new Game(matchId, player1, player2);
        this.activeGames.push(game)
        game.start();
    }

    routeInput(lobby, playerId, snapshot) {
        const player = lobby.players.find(p =>  p.id === playerId);
        if (player.matchId === null) return;

        const game = this.activeGames.find(g => g.matchId === player.match_id);
        if (game) {
            game.validateState(playerId, snapshot);
        }
    }

}

module.exports = new GameManager();