class PlayerRepository {
    constructor (pool){
        this.pool = pool
    }
    async getPlayerByCredentials (id, authTokenHash){
        return await this.pool.query(`
            SELECT * FROM players
            WHERE player_id = $1 AND auth_token_hash = $2
        `, [id, authTokenHash]);
    }
    async addNewPlayer(player, authTokenHash){
        return await this.pool.query(`
            INSERT INTO players (player_id, player_name, status, auth_token_hash)
            VALUES ($1, $2, 0, $3)
        `, [player.id, player.username, authTokenHash]);
    }

    async updatePlayerName(playerId, username){
        return await this.pool.query(`
            UPDATE players
            SET player_name = $1
            WHERE player_id = $2
        `, [username, playerId]);
    }

    async updatePlayerStats(player){
        if (!player) return;
        await this.pool.query(`
            UPDATE players
            SET status = $1,
                total_wins = total_wins + $2,
                current_streak = $3,
                max_streak = GREATEST(max_streak, $4),
                total_losses = total_losses + $5
            WHERE player_id = $6
        `, [0, player.total_wins || 0, player.win_streak || 0, player.max_streak || 0, player.total_losses || 0, player.id]);
    }
}

module.exports = PlayerRepository
