const test = require('node:test');
const assert = require('node:assert/strict');
const WebSocket = require('ws');

// gameController only passes the pool into its repository. Supplying a small
// test double here avoids opening a real database connection during unit tests.
const dbPath = require.resolve('../src/config/db');
require.cache[dbPath] = {
    id: dbPath,
    filename: dbPath,
    loaded: true,
    exports: {}
};

const Game = require('../src/controllers/gameController');

const makePlayer = (id) => {
    const messages = [];
    return {
        id,
        messages,
        status: 1,
        match_id: 42,
        total_wins: 0,
        total_losses: 0,
        win_streak: 0,
        max_streak: 0,
        ws: {
            readyState: WebSocket.OPEN,
            send(payload) {
                messages.push(JSON.parse(payload));
            }
        }
    };
};

const makeGame = () => {
    const player1 = makePlayer('player-1');
    const player2 = makePlayer('player-2');
    const game = new Game(42, player1, player2);
    game.acceptingInput = true;
    game.matchRepository = {
        updateMatchStatus: async () => {}
    };
    return { game, player1, player2 };
};

test('invalid movement cannot resolve a punch', () => {
    const { game, player1, player2 } = makeGame();
    game.positions[player1.id].x = 250;
    game.positions[player2.id].x = 300;
    game.lastAcceptedPositions[player1.id] = 250;

    game.validateState(player1.id, {
        player: {
            x: 480,
            history: ['punch']
        }
    });

    assert.equal(game.status, 0);
    assert.deepEqual(player2.messages, []);
    assert.deepEqual(player1.messages, [{
        type: 'correction',
        matchId: 42,
        position: 250
    }]);
});

test('a terminal punch sends only match-scoped game-end events', () => {
    const { game, player1, player2 } = makeGame();
    game.positions[player1.id].x = 250;
    game.positions[player2.id].x = 300;
    game.lastAcceptedPositions[player1.id] = 250;

    game.validateState(player1.id, {
        player: {
            x: 250,
            history: ['punch']
        }
    });

    assert.equal(game.status, 1);
    assert.deepEqual(player1.messages, [{
        type: 'game_end',
        matchId: 42,
        winner: player1.id,
        reason: 'completed',
        opponentPosition: 260
    }]);
    assert.deepEqual(player2.messages, [{
        type: 'game_end',
        matchId: 42,
        winner: player1.id,
        reason: 'completed',
        opponentPosition: 310
    }]);
});
