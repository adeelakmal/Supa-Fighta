const setupWebSocketServer = require('./wsServer');
const config = require('./config/dotenv');


setupWebSocketServer(config.port);
