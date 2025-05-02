// Initialize a server here for websockets 
const WebSocket = require('ws');
const { HandleMessage, HandleClose } = require('./controllers/lobbyController');


const setupWebSocketServer = (port) => {
const wss = new WebSocket.Server({ port: port });
  wss.on('connection', (ws) => {
    ws.id = crypto.randomUUID();
    console.log(`A new player - ${ws.id} has joined the lobby`);
    
    ws.on('message', message => HandleMessage(ws, message))
    ws.on('close', () => HandleClose(ws));
  
  })
  console.log('WebSocket server is listening on ws://localhost:8080');
}

module.exports = setupWebSocketServer;