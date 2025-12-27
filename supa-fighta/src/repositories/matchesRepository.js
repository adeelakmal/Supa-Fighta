class MatchesRepository{
    constructor(pool){
        this.pool = pool
    }
    async createMatch(player1, player2) {
        const match = await this.pool.query(`
            INSERT INTO matches (player1_id, player2_id, timestamp, status)
            VALUES ($1, $2, NOW(), 0)
            RETURNING match_id
        `, [player1.id, player2.id]);
        return match.rows[0].match_id
    }
    async updateMatchStatus(winner=NULL, matchId){
        const id = winner ? winner.id : null
        await this.pool.query(`
            UPDATE matches
            SET status = 1, winner_id = $1
            WHERE match_id = $2
        `, [id, matchId]);
    }
}

module.exports = MatchesRepository