class Player {
    constructor(ws, username = 'Guest', win_streak = 0, total_wins = 0, total_losses = 0) {
      this.id = ws.id;
      this.ws = ws;
      this.username = username;
      this.status = 0;
      this.match_id = null;
      this.win_streak = win_streak
      this.max_streak = win_streak
      this.total_wins = total_wins
      this.total_losses = total_losses
    }
  }
  
module.exports = Player;