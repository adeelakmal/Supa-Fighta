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
        this.timer = 10 * 60; // 60 seconds at 60Hz
        this.winner = null;
        this.losser = null;
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
            this.end(null, null); // Draw or time-out
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
                else if ( pos.x + this.moveStep > 640 - (80*2)) {
                    console.log("right side limit reached");
                    pos.x = 640 - (80*2);
                }
                else {
                    // else players are definitely overlapping so we add pushing logic here
                    console.log("players pushing");
                    pos.x = pos.x + 1;
                    // console.log(`Player ${playerId} position after push: ${pos.x}`);
                    reversedOtherPos.x = Math.min(640 - 80, +(pos.x + 80));
                    otherPos.x = this.reversePosition(reversedOtherPos).x;
                  
                }
                break;
            case 'dash_left':
                if ( pos.x - this.moveStep > 0 ) {
                    pos.x -= this.moveStep * (DASH_FACTOR - 0.5);
                }
                else {
                    pos.x = 0;
                }
                break;
            case 'dash_right':
                if (pos.x + (this.moveStep * DASH_FACTOR) <= reversedOtherPos.x - 80 ) {
                    pos.x += this.moveStep * DASH_FACTOR;
                }
                else if ( pos.x + (this.moveStep * DASH_FACTOR) > 640 - (80*2)) {
                    console.log("right side limit reached");
                    pos.x = 640 - (80 * 2);
                } 
                else {
                    // else players are definitely overlapping so we add pushing logic here
                    console.log("players pushing");
                    pos.x += 1 * DASH_FACTOR;
                    reversedOtherPos.x = Math.min(640 - 80, (pos.x + 80));
                    otherPos.x = this.reversePosition(reversedOtherPos).x;
                }
                break;
            case 'punch':
                if(pos.x+80+30 > reversedOtherPos.x) {
                    console.log(`Player ${playerId} punched Player ${otherId}`);
                    this.winner = this.player1.id === playerId ? this.player1 : this.player2;
                    this.losser = this.player1.id === playerId ? this.player2 : this.player1;
                    this.end(this.winner, this.losser);
                }
                break;
            case 'parry':
                break;
            default:
                // console.log("Unknown input:", input);
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
        if (!state) return state;
        const words = state.split('_');
        if (words.length > 1) {
            if (words[1] === 'left') {
                words[1] = 'right';
            } else {
                words[1] = 'left';
            }
            return words.join('_');
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
            if (this.status!=1) {
                this.processInput(playerId, input); 
            }
            
        })
        if (history[history.length - 1] === "dash_right") {
            console.log(`Player ${playerId} history: ${history}`);
            console.log(`serverPos after dash_right processing: x=${serverPos.x}`);
            console.log(`vs client x=${x}`);
        }
        // console.log(`Player ${playerId} position: client x=${x}, server x=${serverPos.x}`);
        if (Math.abs(x - serverPos.x) > 10) {
            console.log(`Desync detected for player ${playerId} diff: ${Math.abs(x - serverPos.x)}, correcting to x=${serverPos.x}`);
            const target = playerId === this.player1.id ? this.player1 : this.player2;
            target.ws.send(JSON.stringify({type: 'correction', position: serverPos.x}));
        } 
        // console.log(`Validating state for player ${playerId}: Client Pos (x=${x}, y=${y}) vs Server Pos (x=${serverPos.x}, y=${serverPos.y})`);

        // send response to opponent
        let pos = this.reversePosition(serverPos);
        let op_state = this.reverseState(history[history.length - 1]);
        let message = {
            type: 'opponent_update',
            position: pos,
            current_state: op_state
        };
        this.sendToOpponent(playerId, message);
    }

    async end(winner, losser) {

        clearInterval(this.interval);
        this.status = 1;
        await this.matchRepository.updateMatchStatus(winner,this.matchId)


        // Update players' stats
        if (winner) {
            winner.total_wins++;
            winner.win_streak++;
            winner.max_streak = Math.max(winner.max_streak, winner.win_streak);
            losser.total_losses++;
            losser.win_streak = 0;
        } else {
            this.player1.total_losses++;
            this.player1.win_streak = 0;
            this.player2.total_losses++;
            this.player2.win_streak = 0;
        }

        // Notify players that the game has ended
        this.player1.ws.send(JSON.stringify({ type: 'game_end', winner: winner ? winner.id : null }));
        this.player2.ws.send(JSON.stringify({ type: 'game_end', winner: winner ? winner.id : null }));
        return;
    }
}

module.exports = Game;