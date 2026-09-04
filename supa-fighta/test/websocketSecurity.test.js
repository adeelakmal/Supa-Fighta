const test = require('node:test');
const assert = require('node:assert/strict');
const {
    MAX_CONNECTIONS_PER_IP,
    MAX_MESSAGES_PER_SECOND,
    MAX_PLAYER_CREATIONS_PER_HOUR,
    WebSocketSecurity,
    getClientIp,
    validateSnapshot
} = require('../src/utils/websocketSecurity');

test('accepts only bounded snapshots with known inputs', () => {
    assert.equal(validateSnapshot({
        player: { x: 200, history: ['walk_right'] }
    }), true);
    assert.equal(validateSnapshot({
        player: { x: 200, history: Array(121).fill('walk_right') }
    }), false);
    assert.equal(validateSnapshot({
        player: { x: 200, history: ['teleport'] }
    }), false);
});

test('limits connections, messages, and player creation per IP', () => {
    const security = new WebSocketSecurity();
    const ip = '203.0.113.10';

    for (let index = 0; index < MAX_CONNECTIONS_PER_IP; index++) {
        assert.equal(security.openConnection(ip), true);
    }
    assert.equal(security.openConnection(ip), false);
    security.closeConnection(ip);
    assert.equal(security.openConnection(ip), true);

    const ws = {};
    for (let index = 0; index < MAX_MESSAGES_PER_SECOND; index++) {
        assert.equal(security.allowMessage(ws, 1000), true);
    }
    assert.equal(security.allowMessage(ws, 1000), false);
    assert.equal(security.allowMessage(ws, 2000), true);

    for (let index = 0; index < MAX_PLAYER_CREATIONS_PER_HOUR; index++) {
        assert.equal(security.allowPlayerCreation(ip, 1000), true);
    }
    assert.equal(security.allowPlayerCreation(ip, 1000), false);
    assert.equal(security.allowPlayerCreation(ip, 60 * 60 * 1000 + 1001), true);
});

test('uses the final address added by the trusted proxy', () => {
    const request = {
        headers: { 'x-forwarded-for': 'spoofed, 203.0.113.20' },
        socket: { remoteAddress: '127.0.0.1' }
    };

    assert.equal(getClientIp(request), '203.0.113.20');
});
