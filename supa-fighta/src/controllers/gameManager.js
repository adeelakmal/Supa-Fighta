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
        if (game.status === 1) return; // Game has ended, ignore inputs
        if (game) {
            game.validateState(playerId, snapshot);
        }
    }

    // destroyGame(matchId) {
    //     const gameIndex = this.activeGames.findIndex(g => g.matchId === matchId);
    //     if (gameIndex !== -1) {
    //         clearInterval(this.activeGames[gameIndex].interval);
    //         this.activeGames.splice(gameIndex, 1);
    //     }
    // }

}

module.exports = new GameManager();