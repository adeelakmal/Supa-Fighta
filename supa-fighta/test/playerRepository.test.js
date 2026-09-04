const test = require('node:test');
const assert = require('node:assert/strict');
const PlayerRepository = require('../src/repositories/playerRepository');

test('looks up a player using both public ID and token hash', async () => {
    const calls = [];
    const pool = {
        query: async (sql, values) => {
            calls.push({ sql, values });
            return { rows: [] };
        }
    };
    const repository = new PlayerRepository(pool);

    await repository.getPlayerByCredentials('player-id', 'token-hash');

    assert.equal(calls.length, 1);
    assert.match(calls[0].sql, /player_id = \$1 AND auth_token_hash = \$2/);
    assert.deepEqual(calls[0].values, ['player-id', 'token-hash']);
});

test('stores only the token hash when creating a player', async () => {
    const calls = [];
    const pool = {
        query: async (sql, values) => {
            calls.push({ sql, values });
            return { rows: [] };
        }
    };
    const repository = new PlayerRepository(pool);

    await repository.addNewPlayer(
        { id: 'player-id', username: 'Fighter' },
        'token-hash'
    );

    assert.equal(calls.length, 1);
    assert.match(calls[0].sql, /auth_token_hash/);
    assert.deepEqual(calls[0].values, ['player-id', 'Fighter', 'token-hash']);
});
