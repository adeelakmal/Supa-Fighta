const { isPlayerNameOffensive } = require('./playerNameModeration');

const MIN_PLAYER_NAME_LENGTH = 3;
const MAX_PLAYER_NAME_LENGTH = 20;
const ALLOWED_PLAYER_NAME = /^[A-Za-z0-9 _-]+$/;
const RESERVED_PLAYER_NAMES = new Set([
    'admin',
    'developer',
    'guest',
    'moderator',
    'server',
    'system'
]);

const validatePlayerName = (username) => {
    if (typeof username !== 'string') {
        return {
            valid: false,
            message: 'Enter a player name.'
        };
    }

    const name = username.trim().replace(/\s+/g, ' ');
    const length = Array.from(name).length;

    if (
        length < MIN_PLAYER_NAME_LENGTH
        || length > MAX_PLAYER_NAME_LENGTH
    ) {
        return {
            valid: false,
            message: 'Name must be 3-20 characters.'
        };
    }

    if (!ALLOWED_PLAYER_NAME.test(name)) {
        return {
            valid: false,
            message: 'Use only letters, numbers, spaces, _ or -.'
        };
    }

    const key = name.toLowerCase();
    if (RESERVED_PLAYER_NAMES.has(key)) {
        return {
            valid: false,
            message: 'That name is reserved.'
        };
    }

    if (isPlayerNameOffensive(name)) {
        return {
            valid: false,
            message: 'That name is not allowed.'
        };
    }

    return {
        valid: true,
        name
    };
};

module.exports = {
    MAX_PLAYER_NAME_LENGTH,
    MIN_PLAYER_NAME_LENGTH,
    RESERVED_PLAYER_NAMES,
    validatePlayerName
};
