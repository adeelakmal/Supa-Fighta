const test = require('node:test');
const assert = require('node:assert/strict');
const crypto = require('crypto');
const {
    authenticatePlayer,
    createPlayerToken,
    hashPlayerToken,
    hasValidPlayerCredentials
} = require('../src/utils/playerAuth');

test('creates a valid high-entropy player token', () => {
    const token = createPlayerToken();

    assert.equal(token.length, 43);
    assert.match(token, /^[A-Za-z0-9_-]+$/);
    assert.notEqual(token, createPlayerToken());
});

test('authenticates only a matching ID and token pair', async () => {
    const playerId = crypto.randomUUID();
    const playerToken = createPlayerToken();
    const playerRecord = { player_id: playerId, player_name: 'Fighter' };
    const repository = {
        getPlayerByCredentials: async (id, tokenHash) => {
            assert.equal(id, playerId);
            assert.equal(tokenHash, hashPlayerToken(playerToken));
            return { rows: [playerRecord] };
        }
    };

    assert.equal(
        await authenticatePlayer(repository, playerId, playerToken),
        playerRecord
    );
});

test('rejects missing and incorrect credentials without authenticating', async () => {
    const playerId = crypto.randomUUID();
    const playerToken = createPlayerToken();
    let lookupCount = 0;
    const repository = {
        getPlayerByCredentials: async () => {
            lookupCount += 1;
            return { rows: [] };
        }
    };

    assert.equal(await authenticatePlayer(repository, playerId, undefined), null);
    assert.equal(await authenticatePlayer(repository, 'not-a-uuid', playerToken), null);
    assert.equal(lookupCount, 0);

    assert.equal(await authenticatePlayer(repository, playerId, playerToken), null);
    assert.equal(lookupCount, 1);
});

test('hashes player tokens without storing the raw credential', () => {
    const token = createPlayerToken();
    const expected = crypto.createHash('sha256').update(token).digest('hex');

    assert.equal(hashPlayerToken(token), expected);
    assert.equal(hashPlayerToken(token).length, 64);
    assert.notEqual(hashPlayerToken(token), token);
});

test('requires a version 4 UUID and a complete player token', () => {
    const playerId = crypto.randomUUID();
    const playerToken = createPlayerToken();

    assert.equal(hasValidPlayerCredentials(playerId, playerToken), true);
    assert.equal(hasValidPlayerCredentials(playerId, undefined), false);
    assert.equal(hasValidPlayerCredentials(playerId, 'short-token'), false);
    assert.equal(hasValidPlayerCredentials('not-a-uuid', playerToken), false);
    assert.equal(
        hasValidPlayerCredentials('00000000-0000-1000-8000-000000000000', playerToken),
        false
    );
});
