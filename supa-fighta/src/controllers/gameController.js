const pool = require('../config/db');

class Game {
    constructor(matchId, player1, player2) {
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

    async end(winnerId) {
        console.log(`Ending match ${this.matchId}. Winner: ${winnerId}`);
        this.status = 1;

        // Update match status in the database
        await pool.query(`
            UPDATE matches
            SET status = 1, winner_id = $1
            WHERE match_id = $2
        `, [winnerId, this.matchId]);

        // Update players' stats in the database
        await pool.query(`
            UPDATE players
            SET total_wins = total_wins + 1, current_streak = current_streak + 1, max_streak = GREATEST(max_streak, current_streak)
            WHERE player_id = $1
        `, [winnerId]);

        await pool.query(`
            UPDATE players
            SET total_losses = total_losses + 1, current_streak = 0
            WHERE player_id = $1
        `, [winnerId === this.player1.id ? this.player2.id : this.player1.id]);

        // Notify players that the game has ended
        this.player1.ws.send(JSON.stringify({ type: 'game_end', winner: winnerId }));
        this.player2.ws.send(JSON.stringify({ type: 'game_end', winner: winnerId }));
    }
}

module.exports = Game;