const test = require('node:test');
const assert = require('node:assert/strict');
const crypto = require('crypto');
const WebSocket = require('ws');
const { createPlayerToken } = require('../src/utils/playerAuth');

let authenticatedPlayerId;
const databaseQueries = [];
const dbPath = require.resolve('../src/config/db');
require.cache[dbPath] = {
    id: dbPath,
    filename: dbPath,
    loaded: true,
    exports: {
        query: async (sql) => {
            databaseQueries.push(sql);
            if (/SELECT \*/.test(sql)) {
                return {
                    rows: [{
                        player_id: authenticatedPlayerId,
                        player_name: 'Fighter'
                    }]
                };
            }
            return { rows: [] };
        }
    }
};

const {
    HandleClose,
    HandleMessage,
    LOBBY
} = require('../src/controllers/lobbyController');

const makeSocket = (id) => ({
    id,
    readyState: WebSocket.OPEN,
    bufferedAmount: 0,
    sent: [],
    terminated: false,
    send(message) {
        this.sent.push(JSON.parse(message));
    },
    terminate() {
        this.terminated = true;
        this.readyState = WebSocket.CLOSED;
    }
});

test('authenticated reconnect replaces a stale socket safely', async (t) => {
    t.after(() => {
        LOBBY.players = [];
    });

    authenticatedPlayerId = crypto.randomUUID();
    databaseQueries.length = 0;
    const oldSocket = makeSocket(authenticatedPlayerId);
    const oldPlayer = {
        id: authenticatedPlayerId,
        ws: oldSocket,
        username: 'Fighter',
        status: 1,
        match_id: 'finished-match'
    };
    LOBBY.players = [oldPlayer];

    const newSocket = makeSocket(crypto.randomUUID());
    await HandleMessage(newSocket, {
        type: 'validate_player',
        playerId: authenticatedPlayerId,
        playerToken: createPlayerToken()
    });

    assert.equal(oldSocket.terminated, true);
    assert.equal(newSocket.playerRegistered, true);
    assert.equal(LOBBY.players.length, 1);
    assert.equal(LOBBY.players[0].ws, newSocket);
    assert.equal(
        newSocket.sent.some(message => (
            message.type === 'validation_result' && message.valid === true
        )),
        true
    );
    assert.equal(
        databaseQueries.filter(sql => /UPDATE players/.test(sql)).length,
        1
    );

    await HandleClose(oldSocket);
    assert.equal(LOBBY.players.length, 1);
    assert.equal(LOBBY.players[0].ws, newSocket);
    assert.equal(
        databaseQueries.filter(sql => /UPDATE players/.test(sql)).length,
        1
    );
});
