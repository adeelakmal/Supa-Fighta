class PlayerRepository {
    constructor (pool){
        this.pool = pool
    }
    async getPlayerById (id){
        return await this.pool.query('SELECT * FROM players WHERE player_id = $1', [id]);
    }
    addNewPlayer(player){
        this.pool.query(`
            INSERT INTO players (player_id, player_name, status)
            VALUES ($1, $2, 0)
        `, [player.id, player.username]);
    }
    async updatePlayerWins(id){
        await this.pool.query(`
            UPDATE players
            SET total_wins = total_wins + 1, current_streak = current_streak + 1, max_streak = GREATEST(max_streak, current_streak)
            WHERE player_id = $1
        `, [id]);
    }
    async updatePlayerLosses(id){
        await this.pool.query(`
            UPDATE players
            SET total_losses = total_losses + 1, current_streak = 0
            WHERE player_id = $1
        `, [id]);

    }
}

module.exports = PlayerRepository