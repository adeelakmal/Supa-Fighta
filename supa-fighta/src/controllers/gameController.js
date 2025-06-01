const pool = require('../config/db');
const MatchesRepository = require('../repositories/matchesRepository');

class Game {
    constructor(matchId, player1, player2) {
        this.matchRepository = new MatchesRepository(pool)
        this.matchId = matchId;
        this.player1 = player1;
        this.player2 = player2;
        this.status = 0; // 0 = in-game, 1 = ended
    }

    async start() {
        console.log(`Starting match ${this.matchId} between ${this.player1.id} and ${this.player2.id}`);
        // Notify players that the game has started
        this.player1.ws.send(JSON.stringify({ type: 'game_start', opponent: this.player2.id }));
        this.player2.ws.send(JSON.stringify({ type: 'game_start', opponent: this.player1.id }));
    }

    async end(winner) {
        losser = winner.id === this.player1.id ? this.player2 : this.player1
        console.log(`Ending match ${this.matchId}. Winner: ${winner.id}`);
        this.status = 1;

        // Update match status in the database
        await this.matchRepository.updateMatchStatus(winner.id,this.matchId)

        // Update players' stats
        winner.total_wins++;
        losser.total_losses++;
        losser.current_streak = 0;

        // TODO: Replace these only when actual game logic is written
        // Update all the player stats in the db when they leave the server this helps reduce total db calls made
        
        /*await pool.query(`
            UPDATE players
            SET total_wins = total_wins + 1, current_streak = current_streak + 1, max_streak = GREATEST(max_streak, current_streak)
            WHERE player_id = $1
        `, [winner.id]);

        await pool.query(`
            UPDATE players
            SET total_losses = total_losses + 1, current_streak = 0
            WHERE player_id = $1
        `, [winner.id === this.player1.id ? this.player2.id : this.player1.id]);*/

        // Notify players that the game has ended
        this.player1.ws.send(JSON.stringify({ type: 'game_end', winner: winnerId }));
        this.player2.ws.send(JSON.stringify({ type: 'game_end', winner: winnerId }));
    }
}

module.exports = Game;