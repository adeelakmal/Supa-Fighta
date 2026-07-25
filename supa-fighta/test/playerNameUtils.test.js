const test = require('node:test');
const assert = require('node:assert/strict');
const { validatePlayerName } = require('../src/utils/playerNameUtils');

test('accepts and normalizes valid display names', () => {
    assert.deepEqual(
        validatePlayerName('  Alice   Smith  '),
        { valid: true, name: 'Alice Smith' }
    );
    assert.equal(validatePlayerName('Player_2').valid, true);
    assert.equal(validatePlayerName('Player-2').valid, true);
});

test('allows duplicate display names and capitalization', () => {
    assert.equal(validatePlayerName('Alice').valid, true);
    assert.equal(validatePlayerName('ALICE').valid, true);
    assert.equal(validatePlayerName('Alice').valid, true);
});

test('rejects invalid lengths, characters, and reserved names', () => {
    assert.equal(validatePlayerName('ab').valid, false);
    assert.equal(validatePlayerName('name!').valid, false);
    assert.equal(validatePlayerName('ADMIN').valid, false);
    assert.equal(validatePlayerName('Guest').valid, false);
});

test('rejects profanity, hateful terms, and simple bypass attempts', () => {
    const blockedNames = [
        ['fu', 'ck'].join(''),
        ['f', '_', 'u', '_', 'c', '_', 'k'].join(''),
        ['sh', '1', 't'].join(''),
        ['ni', 'gger'].join(''),
        ['na', 'zi'].join(''),
        ['n', '_', 'a', '_', 'z', '_', 'i'].join(''),
        ['h', '1', 't', 'l', 'e', 'r'].join(''),
        ['n', '4', 'z', 'i', '1', '2', '3'].join('')
    ];

    for (const name of blockedNames) {
        assert.deepEqual(
            validatePlayerName(name),
            {
                valid: false,
                message: 'That name is not allowed.'
            },
            `Expected ${JSON.stringify(name)} to be rejected`
        );
    }
});

test('does not reject common false-positive names', () => {
    const allowedNames = [
        'Assassin',
        'ClassAct',
        'GrapeHero',
        'Raccoon',
        'Scunthorpe',
        'SpicyKnight'
    ];

    for (const name of allowedNames) {
        assert.equal(
            validatePlayerName(name).valid,
            true,
            `Expected ${JSON.stringify(name)} to be accepted`
        );
    }
});
