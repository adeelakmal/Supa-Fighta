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

    async updatePlayerStats(player){
        if (!player) return;
        await this.pool.query(`
            UPDATE players
            SET status = $1,
                total_wins = $2,
                current_streak = $3,
                max_streak = $4,
                total_losses = $5
            WHERE player_id = $6
        `, [0, player.total_wins || 0, player.current_streak || 0, player.max_streak || 0, player.total_losses || 0, player.id]);
    }
}

module.exports = PlayerRepository