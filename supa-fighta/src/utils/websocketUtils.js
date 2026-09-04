const WebSocket = require('ws');

const MAX_BUFFERED_AMOUNT = 256 * 1024;

const sendJson = (ws, message) => {
    if (ws.readyState !== WebSocket.OPEN) return false;

    if (ws.bufferedAmount > MAX_BUFFERED_AMOUNT) {
        ws.terminate();
        return false;
    }

    try {
        ws.send(JSON.stringify(message));
        return true;
    } catch (err) {
        console.error(`Failed to send WebSocket message to ${ws.id}:`, err);
        return false;
    }
};

module.exports = { MAX_BUFFERED_AMOUNT, sendJson };
