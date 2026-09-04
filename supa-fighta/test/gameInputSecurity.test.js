const test = require('node:test');
const assert = require('node:assert/strict');
const WebSocket = require('ws');

const dbPath = require.resolve('../src/config/db');
require.cache[dbPath] = {
    id: dbPath,
    filename: dbPath,
    loaded: true,
    exports: {}
};

const Game = require('../src/controllers/gameController');

const makePlayer = (id) => ({
    id,
    state: 'idle',
    status: 1,
    match_id: 'match',
    total_wins: 0,
    total_losses: 0,
    win_streak: 0,
    max_streak: 0,
    ws: {
        readyState: WebSocket.OPEN,
        bufferedAmount: 0,
        sent: [],
        send(message) {
            this.sent.push(JSON.parse(message));
        },
        terminate() {}
    }
});

test('queues bounded input, rejects replay, and ignores client position', () => {
    const player1 = makePlayer('player-1');
    const player2 = makePlayer('player-2');
    const game = new Game('match', player1, player2);
    game.acceptingInput = true;

    game.validateState('player-1', {
        sequence: 0,
        player: { x: 500, history: ['walk_right'] }
    });
    assert.equal(game.positions['player-1'].x, 200);
    assert.equal(game.inputQueue['player-1'].length, 1);

    game.tick();
    assert.equal(game.positions['player-1'].x, 200.45);
    assert.equal(game.lastAcceptedPositions['player-1'], 200.45);
    assert.equal(player1.ws.sent.at(-1).position, 200.45);

    game.validateState('player-1', {
        sequence: 0,
        player: { x: 201, history: ['walk_right'] }
    });
    assert.equal(game.inputQueue['player-1'].length, 0);
});

test('processes at most one queued input per server tick', () => {
    const game = new Game('match', makePlayer('player-1'), makePlayer('player-2'));
    game.acceptingInput = true;
    game.validateState('player-1', {
        sequence: 0,
        player: { x: 200, history: Array(4).fill('walk_right') }
    });

    game.tick();
    assert.equal(game.inputQueue['player-1'].length, 3);
});

test('enforces server-side combat cooldowns', () => {
    const player1 = makePlayer('player-1');
    const game = new Game('match', player1, makePlayer('player-2'));

    game.tickNumber = 1;
    game.processInput('player-1', 'punch');
    assert.equal(player1.state, 'punch');

    player1.state = 'idle';
    game.tickNumber = 2;
    game.processInput('player-1', 'punch');
    assert.equal(player1.state, 'idle');

    game.tickNumber = 31;
    game.processInput('player-1', 'punch');
    assert.equal(player1.state, 'punch');
});
