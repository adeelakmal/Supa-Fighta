const Game = require('./gameController');

class GameManager {
    constructor() {
        this.activeGames = [];
    }

    createGame(matchId, player1, player2) {
        const game = new Game(
            matchId,
            player1,
            player2,
            () => this.destroyGame(matchId)
        );
        this.activeGames.push(game)
        return game.start();
    }

    routeInput(lobby, playerId, snapshot) {
        const player = lobby.players.find(p =>  p.id === playerId);
        if (!player || player.match_id === null) return;

        const game = this.activeGames.find(g => g.matchId === player.match_id);
        if (!game || game.status === 1) return; // Game has ended, ignore inputs
        if (game) {
            game.validateState(playerId, snapshot);
        }
    }

    async handleDisconnect(playerId) {
        const game = this.activeGames.find(
            activeGame => activeGame.player1.id === playerId || activeGame.player2.id === playerId
        );

        if (!game || game.status === 1) return;

        const disconnectedPlayer = game.player1.id === playerId ? game.player1 : game.player2;
        const remainingPlayer = game.player1.id === playerId ? game.player2 : game.player1;
        await game.end(remainingPlayer, disconnectedPlayer, 'opponent_disconnected');
    }

    destroyGame(matchId) {
        const gameIndex = this.activeGames.findIndex(game => game.matchId === matchId);
        if (gameIndex === -1) return;

        clearInterval(this.activeGames[gameIndex].interval);
        this.activeGames.splice(gameIndex, 1);
    }
}

module.exports = new GameManager();
