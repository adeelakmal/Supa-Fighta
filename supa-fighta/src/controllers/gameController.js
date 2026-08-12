const pool = require('../config/db');
const MatchesRepository = require('../repositories/matchesRepository');
const PlayerState = require('../models/playerState');
const { Inputs } = require('../enums');
const WebSocket = require('ws');
const DASH_FACTOR = 2.1
const MOVE_SPEED = 3;
const MAX_FRAME_SPEED = MOVE_SPEED * DASH_FACTOR;
const POSITION_EPSILON = 2;
// The client runs at 60 FPS and the punch animation at 25 FPS. These inputs
// line up with animation frames 3-5, where the fist is visibly extended.
const PUNCH_ACTIVE_INPUT_START = 10;
const PUNCH_ACTIVE_INPUT_END = 18;
const PARRY_ACTIVE_INPUT_END = 15;
const MATCH_DURATION_SECONDS = 20;
const INTRO_COUNTDOWN_SECONDS = 3;

class Game {
    constructor(matchId, player1, player2, onEnd = null) {
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
        this.lastAcceptedPositions = {
            [player1.id]: 200,
            [player2.id]: 200
        };
        this.durationSeconds = MATCH_DURATION_SECONDS;
        this.timer = this.durationSeconds * 60;
        this.winner = null;
        this.losser = null;
        this.interval = null;
        this.countdownTimeout = null;
        this.countdownSeconds = INTRO_COUNTDOWN_SECONDS;
        this.startsAt = null;
        this.acceptingInput = false;
        this.onEnd = onEnd;
        this.parryLocks = new Set();
        this.attackResolved = {
            [player1.id]: false,
            [player2.id]: false
        };
        this.attackProgress = {
            [player1.id]: 0,
            [player2.id]: 0
        };
        this.parryProgress = {
            [player1.id]: 0,
            [player2.id]: 0
        };

    }

    start() {
        console.log(`Starting match ${this.matchId} between ${this.player1.id} and ${this.player2.id}`);
        this.startsAt = Date.now() + (this.countdownSeconds * 1000);
        const startMessage = {
            type: 'game_start',
            matchId: this.matchId,
            countdownSeconds: this.countdownSeconds,
            matchDurationSeconds: this.durationSeconds,
            startsAt: this.startsAt
        };
        const player1Ready = this.sendToPlayer(
            this.player1,
            { ...startMessage, opponent: this.player2.id }
        );
        const player2Ready = this.sendToPlayer(
            this.player2,
            { ...startMessage, opponent: this.player1.id }
        );

        if (!player1Ready || !player2Ready) {
            const winner = player1Ready ? this.player1 : player2Ready ? this.player2 : null;
            const losser = winner === this.player1 ? this.player2 : winner === this.player2 ? this.player1 : null;

            [this.player1, this.player2].forEach(player => {
                if (player.ws.readyState === WebSocket.OPEN) {
                    player.status = 0;
                    player.match_id = null;
                }
            });

            void this.end(winner, losser, 'opponent_disconnected');
            return false;
        }

        const countdownDelay = Math.max(0, this.startsAt - Date.now());
        this.countdownTimeout = setTimeout(() => {
            if (this.status === 1) return;

            this.acceptingInput = true;
            this.interval = setInterval(() => this.tick(), 1000 / 60);
        }, countdownDelay);

        return true;
    }

    receiveInput(playerId, input) {
        this.inputQueue[playerId].push(input);
    }

    tick() {
        // Advance timer and check for end
        this.timer--;
        if (this.timer <= 0) {
            void this.end(null, null, 'timeout');
        }
    }

    processInput(playerId, input) {
        const otherId = playerId === this.player1.id ? this.player2.id : this.player1.id;
        const pos = this.positions[playerId];
        const otherPos = this.positions[otherId];
        const reversedOtherPos = this.reversePosition(otherPos);
        let player = this.player1.id === playerId ? this.player1 : this.player2;
        const parryLockKey = `${playerId}:${otherId}`;

        if (input !== 'punch') {
            this.parryLocks.delete(parryLockKey);
            this.attackResolved[playerId] = false;
            this.attackProgress[playerId] = 0;
        }
        if (input !== 'parry') {
            this.parryProgress[playerId] = 0;
        }

        switch (input) {
            case 'idle':
                player.state = 'idle'
                break;
            case 'walk_left':
            case 'walk_right':
            case 'dash_left':
            case 'dash_right':
                player.state = input;
                break;
            case 'punch':
                player.state = 'punch';
                this.attackProgress[playerId]++;
                if (this.attackResolved[playerId]) {
                    break;
                }
                if (
                    this.attackProgress[playerId] < PUNCH_ACTIVE_INPUT_START
                    || this.attackProgress[playerId] > PUNCH_ACTIVE_INPUT_END
                ) {
                    break;
                }
                if(pos.x+80+30 > reversedOtherPos.x) {
                    this.attackResolved[playerId] = true;
                    let otherPlayer = this.player1.id === otherId ? this.player1 : this.player2;
                    const parryIsActive = (
                        otherPlayer.state === Inputs.PARRY
                        && this.parryProgress[otherId] > 0
                        && this.parryProgress[otherId] <= PARRY_ACTIVE_INPUT_END
                    );
                    if (parryIsActive){
                        if (!this.parryLocks.has(parryLockKey)) {
                            console.log(`Player ${otherId} parried Player ${playerId}`);
                            this.parryLocks.add(parryLockKey);
                        }
                        player.state = 'parried';
                        otherPlayer.state = 'parry-hit';
                    } else {
                        console.log(`Player ${playerId} punched Player ${otherId}`);
                        this.winner = this.player1.id === playerId ? this.player1 : this.player2;
                        this.losser = this.player1.id === playerId ? this.player2 : this.player1;
                        void this.end(this.winner, this.losser);
                    }
                }
                break;
            case 'parry':
                player.state = Inputs.PARRY
                this.parryProgress[playerId]++;
                break;
            case 'parry-hit':
            case 'parried':
                player.state = input;
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
        const opponent = opponentId === this.player1.id ? this.player1 : this.player2;
        this.sendToPlayer(opponent, message);
    }

    sendToPlayer(player, message) {
        if (player.ws.readyState !== WebSocket.OPEN) return false;

        try {
            player.ws.send(JSON.stringify(message));
            return true;
        } catch (err) {
            console.error(`Failed to send match ${this.matchId} message to ${player.id}:`, err);
            return false;
        }
    }

    validateState(playerId, snapshot) {
        if (!this.acceptingInput || this.status === 1) return;

        const playerState = snapshot.player;
        const { history } = playerState;
        const x = playerState.x;
        const serverPos = this.positions[playerId];
        const previousAcceptedX = this.lastAcceptedPositions[playerId];
        const maxSnapshotTravel = (
            history.length * MAX_FRAME_SPEED
        ) + POSITION_EPSILON;
        const clientTravel = Math.abs(x - previousAcceptedX);
        const positionInBounds = x >= 0 && x <= 640 - (80 * 2);

        if (!positionInBounds || clientTravel > maxSnapshotTravel) {
            console.log(
                `Invalid movement for player ${playerId}: ` +
                `travel=${clientTravel}, allowed=${maxSnapshotTravel}`
            );
            const target = playerId === this.player1.id ? this.player1 : this.player2;
            this.sendToPlayer(target, {
                type: 'correction',
                matchId: this.matchId,
                position: previousAcceptedX
            });
            serverPos.x = previousAcceptedX;
            return;
        } else {
            // Input labels are still processed for combat and state, but the
            // validated client position is the reconciliation point. Trying
            // to reproduce client acceleration from 30 Hz snapshots creates
            // frame-order drift and visible correction loops.
            serverPos.x = x;
            this.lastAcceptedPositions[playerId] = x;
        }

        for (const input of history) {
            if (this.status === 1) break;
            this.processInput(playerId, input);
        }

        // end() already sent the terminal event. Do not send a late update
        // that could be buffered and replayed in the next match.
        if (this.status === 1) return;

        // send response to opponent
        let pos = this.reversePosition(serverPos);
        let player = this.player1.id === playerId ? this.player1 : this.player2;
        let op_state = this.reverseState(player.state || history[history.length - 1]);
        let message = {
            type: 'opponent_update',
            matchId: this.matchId,
            position: pos,
            current_state: op_state
        };
        this.sendToOpponent(playerId, message);
    }

    async end(winner, losser, reason = 'completed') {
        if (this.status === 1) return;

        clearTimeout(this.countdownTimeout);
        clearInterval(this.interval);
        this.status = 1;
        this.acceptingInput = false;

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
        const message = {
            type: 'game_end',
            matchId: this.matchId,
            winner: winner ? winner.id : null,
            reason
        };
        this.sendToPlayer(this.player1, {
            ...message,
            opponentPosition: this.reversePosition(
                this.positions[this.player2.id]
            ).x
        });
        this.sendToPlayer(this.player2, {
            ...message,
            opponentPosition: this.reversePosition(
                this.positions[this.player1.id]
            ).x
        });

        if (this.onEnd) {
            this.onEnd(this);
        }

        try {
            await this.matchRepository.updateMatchStatus(winner, this.matchId);
        } catch (err) {
            console.error(`Failed to save result for match ${this.matchId}:`, err);
        }
    }
}

module.exports = Game;
