// Initialize a server here for websockets 
const WebSocket = require('ws');
const pool = require('./config/db')
const { HandleMessage, HandleClose } = require('./controllers/lobbyController');


const setupWebSocketServer = (port) => {
const wss = new WebSocket.Server({ port: port });
  wss.on('connection', async (ws) => {
    ws.id = crypto.randomUUID();
    console.log(`A new player - ${ws.id} has joined the lobby`);
    let result = await pool.query(`INSERT INTO public."Players" (id) VALUES ($1) RETURNING *`, [ws.id])
    console.log("Player inserted into db:", result)
    
    ws.on('message', message => HandleMessage(ws, message))
    ws.on('close', () => HandleClose(ws));
  
  })
  console.log('WebSocket server is listening on ws://localhost:8080');
}

module.exports = setupWebSocketServer;