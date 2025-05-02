class Player {
    constructor(ws, username = 'Guest') {
      this.id = ws.id;
      this.ws = ws;
      this.username = username;
    }
  }
  
module.exports = Player;
  