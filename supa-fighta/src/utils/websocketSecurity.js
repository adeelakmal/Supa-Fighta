const MAX_CONNECTIONS_PER_IP = 5;
const MAX_MESSAGES_PER_SECOND = 120;
const MAX_PLAYER_CREATIONS_PER_HOUR = 20;
const PLAYER_CREATION_WINDOW_MS = 60 * 60 * 1000;
const MAX_INPUTS_PER_SNAPSHOT = 4;

const VALID_INPUTS = new Set([
    'idle',
    'walk_left',
    'walk_right',
    'dash_left',
    'dash_right',
    'punch',
    'parry',
    'parry-hit',
    'parried',
    'hurt',
    'win',
    'wait'
]);

const getClientIp = (request) => {
    const forwardedFor = request.headers['x-forwarded-for'];
    if (typeof forwardedFor === 'string' && forwardedFor.length > 0) {
        // Render appends the connecting address. Using the final value avoids
        // trusting an attacker-controlled value prepended to the header.
        return forwardedFor.split(',').at(-1).trim().slice(0, 64);
    }

    return String(request.socket.remoteAddress || 'unknown').slice(0, 64);
};

const validateSnapshot = (snapshot) => {
    const player = snapshot?.player;

    return Boolean(
        player
        && Number.isFinite(player.x)
        && Number.isSafeInteger(snapshot.sequence)
        && snapshot.sequence >= 0
        && Array.isArray(player.history)
        && player.history.length > 0
        && player.history.length <= MAX_INPUTS_PER_SNAPSHOT
        && player.history.every(input => VALID_INPUTS.has(input))
    );
};

class WebSocketSecurity {
    constructor() {
        this.connectionCounts = new Map();
        this.playerCreations = new Map();
    }

    openConnection(ip) {
        const count = this.connectionCounts.get(ip) || 0;
        if (count >= MAX_CONNECTIONS_PER_IP) return false;

        this.connectionCounts.set(ip, count + 1);
        return true;
    }

    closeConnection(ip) {
        const count = this.connectionCounts.get(ip) || 0;
        if (count <= 1) {
            this.connectionCounts.delete(ip);
        } else {
            this.connectionCounts.set(ip, count - 1);
        }
    }

    allowMessage(ws, now = Date.now()) {
        if (!ws.messageRate || now - ws.messageRate.startedAt >= 1000) {
            ws.messageRate = { startedAt: now, count: 1 };
            return true;
        }

        ws.messageRate.count += 1;
        return ws.messageRate.count <= MAX_MESSAGES_PER_SECOND;
    }

    allowPlayerCreation(ip, now = Date.now()) {
        const cutoff = now - PLAYER_CREATION_WINDOW_MS;
        const recent = (this.playerCreations.get(ip) || [])
            .filter(timestamp => timestamp > cutoff);

        if (recent.length >= MAX_PLAYER_CREATIONS_PER_HOUR) {
            this.playerCreations.set(ip, recent);
            return false;
        }

        recent.push(now);
        this.playerCreations.set(ip, recent);
        return true;
    }
}

module.exports = {
    MAX_CONNECTIONS_PER_IP,
    MAX_INPUTS_PER_SNAPSHOT,
    MAX_MESSAGES_PER_SECOND,
    MAX_PLAYER_CREATIONS_PER_HOUR,
    WebSocketSecurity,
    getClientIp,
    validateSnapshot
};
