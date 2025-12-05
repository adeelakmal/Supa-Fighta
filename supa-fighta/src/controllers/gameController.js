const pool = require('../config/db');
const MatchesRepository = require('../repositories/matchesRepository');
const PlayerState = require('../models/playerState');
const DASH_FACTOR = 2.5

class Game {
    constructor(matchId, player1, player2) {
        this.matchRepository = new MatchesRepository(pool)
        this.matchId = matchId;
        this.player1 = player1;
        this.player2 = player2;
        this.status = 0; // 0 = in-game, 1 = ended

        // Use PlayerState objects
        this.positions = {
            [player1.id]: new PlayerState(200, 220),
            [player2.id]: new PlayerState(200, 220)
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
        this.moveStep = 2;

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
        // Advance timer and check for end
        this.timer--;
        if (this.timer <= 0) {
            this.end(null); // Draw or time-out
        }
    }

    processInput(playerId, input) {
        const otherId = playerId === this.player1.id ? this.player2.id : this.player1.id;
        const pos = this.positions[playerId];
        let otherPos = this.positions[otherId];
        let reversedOtherPos = this.reversePosition(otherPos);
        // console.log(`Reversed opponent position for processing:`, otherPos);

        switch (input) {
            case 'idle':
                // do nothing
                break;
            case 'walk_left':
                if ( pos.x - this.moveStep > 0 ) {
                    pos.x -= this.moveStep;
                }
                else{
                    pos.x = 0;
                }
                break;
            case 'walk_right':
                if ( pos.x + this.moveStep <= reversedOtherPos.x - 80 ) {
                    pos.x += this.moveStep;
                }
                else if ( pos.x + this.moveStep > 640 - (80*2) ) {
                    console.log("right side limit reached");
                    pos.x = 640 - (80*2);
                }
                else {
                    // else players are definitely overlapping so we add pushing logic here
                    console.log("players pushing");
                    this.moveStep = 0.7;
                    pos.x = +(pos.x + this.moveStep).toFixed(1);
                    // console.log(`Player ${playerId} position after push: ${pos.x}`);
                    reversedOtherPos.x = Math.min(640 - 80, +(pos.x + 80).toFixed(1));
                    otherPos.x = this.reversePosition(reversedOtherPos).x;
                    this.moveStep = 2;
                  
                }
                break;
            case 'dash_left':
                if (pos.x - this.moveStep < reversedOtherPos.x || pos.x - this.moveStep > reversedOtherPos.x ) {
                    pos.x -= this.moveStep * (DASH_FACTOR-0.5);
                }
                break;
            case 'dash_right':
                if (pos.x + this.moveStep > reversedOtherPos.x || pos.x + this.moveStep < reversedOtherPos.x ) {
                    pos.x += this.moveStep * DASH_FACTOR;
                }
                break;
            case 'punch':
                if(pos.x+80+30 > reversedOtherPos.x) {
                    console.log(`Player ${playerId} punched Player ${otherId}`);
                    this.winner = this.player1.id === playerId ? this.player1 : this.player2;
                }
                break;
            case 'parry':
                break;
            default:
                console.log("Unknown input:", input);
                break;
        }
    }

    reversePosition(position) {
        // Reverse the position so it makes the same from the opponent's view 80 = sprite width, 120 = ofest p1 starts at from
        return {
            x: 640 - (position.x + 80),
            y: position.y
        };
    }
    reverseState(state) {
        // Reverse the state so it makes the same from the opponent's view
        // if last 4 characters are "left", change them to "right"
        if (state.slice(-4) === 'left') {
            return state.slice(0, -4) + 'right';
        }
        if (state.slice(-5) === 'right'){ 
           return state.slice(0, -5) + 'left';
        }
        return state;
    }

    sendToOpponent(playerId, message) {
        const opponentId = playerId === this.player1.id ? this.player2.id : this.player1.id;
        const opponentWs = opponentId === this.player1.id ? this.player1.ws : this.player2.ws;
        opponentWs.send(JSON.stringify(message));
    }

    validateState(playerId, snapshot) {
        const player_state  = snapshot.player;
        const { history, state} = player_state;
        let x = player_state.x;
        const serverPos = this.positions[playerId];
        history.forEach((input, index) => {
            this.processInput(playerId, input); 
        })
        if (Math.abs(x - serverPos.x) > 10) {
            console.log(`Player ${playerId} position before correction: x=${x}, server x=${serverPos.x}`);
            const corrected_x = (serverPos.x+x)/2;
            serverPos.x = corrected_x;
            console.log(`Desync detected for player ${playerId} diff: ${Math.abs(x - serverPos.x)}, correcting to x=${corrected_x}`);
            const target = playerId === this.player1.id ? this.player1 : this.player2;
            target.ws.send(JSON.stringify({type: 'correction', position: corrected_x}));
        } 
        // console.log(`Validating state for player ${playerId}: Client Pos (x=${x}, y=${y}) vs Server Pos (x=${serverPos.x}, y=${serverPos.y})`);

        // send response to opponent
        let pos = this.reversePosition(playerId, serverPos);
        let op_state = this.reverseState(history[history.length - 1]);
        let message = {
            type: 'opponent_update',
            position: pos,
            current_state: op_state
        };
        this.sendToOpponent(playerId, message);
    }

    async end(winner) {
        clearInterval(this.interval);
        this.status = 1;

        if (!winner) {
            console.log(`Match ${this.matchId} ended in a draw or time-out.`);
            await this.matchRepository.updateMatchStatus(null, this.matchId);
            this.player1.ws.send(JSON.stringify({ type: 'game_end', winner: null }));
            this.player2.ws.send(JSON.stringify({ type: 'game_end', winner: null }));
            return;
        }
        console.log(`Match ${this.matchId} ended with ${winnerd.id} as winner.`);
        await this.matchRepository.updateMatchStatus(winner.id,this.matchId)

        // Update players' stats
        winner.total_wins++;
        winner.current_streak++;
        winner.max_streak = Math.max(winner.max_streak, winner.current_streak);
        losser.total_losses++;
        losser.current_streak = 0;

        /**
         * TODO: Replace these only when actual game logic is written
         * Update all the player stats in the db when they leave the server this helps reduce total db calls made
         */
        
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