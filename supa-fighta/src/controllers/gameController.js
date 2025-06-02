const pool = require('../config/db');
const MatchesRepository = require('../repositories/matchesRepository');
const PlayerState = require('../models/playerState');


class Game {
    constructor(matchId, player1, player2) {
        this.matchRepository = new MatchesRepository(pool)
        this.matchId = matchId;
        this.player1 = player1;
        this.player2 = player2;
        this.status = 0; // 0 = in-game, 1 = ended

        // Use PlayerState objects
        this.positions = {
            [player1.id]: new PlayerState(-5, 0),
            [player2.id]: new PlayerState(5, 0)
        };
        this.actions = {
            [player1.id]: 'idle',
            [player2.id]: 'idle'
        };
        this.inputQueue = {
            [player1.id]: [],
            [player2.id]: []
        };
        this.timer = 60 * 60; // 60 seconds at 60Hz
        this.winner = null;
        this.interval = null;
        this.playerDistance = 1; // Minimum allowed distance between players
    }

    start() {
        console.log(`Starting match ${this.matchId} between ${this.player1.id} and ${this.player2.id}`);
        this.player1.ws.send(JSON.stringify({ type: 'game_start', opponent: this.player2.id }));
        this.player2.ws.send(JSON.stringify({ type: 'game_start', opponent: this.player1.id }));
        this.interval = setInterval(() => this.tick(), 1000 / 60);
    }

    receiveInput(playerId, input) {
        this.inputQueue[playerId].push(input);
    }

    tick() {
        // Process inputs for both players
        [this.player1.id, this.player2.id].forEach(pid => {
            const input = this.inputQueue[pid].shift();
            if (input) {
                this.processInput(pid, input);
                // Log input and position only when input is detected
                console.log(
                    `Player ${pid} input: ${input} | Position: x=${this.positions[pid].x}, y=${this.positions[pid].y}`
                );
            }
        });

        // Advance timer and check for end
        this.timer--;
        if (this.timer <= 0) {
            this.end(null); // Draw or time-out
        }
    }

    processInput(playerId, input) {
        const otherId = playerId === this.player1.id ? this.player2.id : this.player1.id;
        const pos = this.positions[playerId];
        const otherPos = this.positions[otherId];
        const moveStep = 1;

        if (input === 'move_left') {
            // Prevent overlap
            if (pos.x - moveStep < otherPos.x - this.playerDistance || pos.x - moveStep > otherPos.x + this.playerDistance) {
                pos.x -= moveStep;
            }
        } else if (input === 'move_right') {
            if (pos.x + moveStep > otherPos.x + this.playerDistance || pos.x + moveStep < otherPos.x - this.playerDistance) {
                pos.x += moveStep;
            }
        }
    }

    async end(winner) {
        clearInterval(this.interval);
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
        this.player1.ws.send(JSON.stringify({ type: 'game_end', winner: winner ? winner.id : null }));
        this.player2.ws.send(JSON.stringify({ type: 'game_end', winner: winner ? winner.id : null }));
    }
}

module.exports = Game;