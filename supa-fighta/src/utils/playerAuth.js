const crypto = require('crypto');

const PLAYER_TOKEN_BYTES = 32;
const PLAYER_TOKEN_PATTERN = /^[A-Za-z0-9_-]{43}$/;
const PLAYER_ID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

const createPlayerToken = () => crypto.randomBytes(PLAYER_TOKEN_BYTES).toString('base64url');

const hashPlayerToken = (playerToken) => (
    crypto.createHash('sha256').update(playerToken, 'utf8').digest('hex')
);

const hasValidPlayerCredentials = (playerId, playerToken) => (
    typeof playerId === 'string'
    && PLAYER_ID_PATTERN.test(playerId)
    && typeof playerToken === 'string'
    && PLAYER_TOKEN_PATTERN.test(playerToken)
);

const authenticatePlayer = async (playerRepository, playerId, playerToken) => {
    if (!hasValidPlayerCredentials(playerId, playerToken)) {
        return null;
    }

    const result = await playerRepository.getPlayerByCredentials(
        playerId,
        hashPlayerToken(playerToken)
    );
    return result.rows[0] || null;
};

module.exports = {
    authenticatePlayer,
    createPlayerToken,
    hashPlayerToken,
    hasValidPlayerCredentials
};
