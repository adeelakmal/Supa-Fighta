# Supa-Fighta

## 📊 Database Tables

### 🧍‍♂️ players Table

| Column         | Type        | Description                                 |
|:----------------|:------------|:---------------------------------------------|
| player_id      | UUID         | **Primary key, unique player identifier**   |
| player_name    | VARCHAR(50)  | Player's display name                       |
| total_wins     | INTEGER      | Number of wins                              |
| total_losses   | INTEGER      | Number of losses                            |
| current_streak | INTEGER      | Current win streak count                    |
| max_streak     | INTEGER      | Max win streak count                        |
| status         | INTEGER      | (0 for waiting, 1 for in-game) Player Status|

---

### ⚔️ matches Table

| Column         | Type                        | Description                               |
|:----------------|:-----------------------------|:-------------------------------------------|
| match_id       | INTEGER (PK, AUTO_INCREMENT) | Unique match identifier                   |
| player1_id     | UUID (FK to players.player_id) | Player 1's identifier                      |
| player2_id     | UUID (FK to players.player_id) | Player 2's identifier                      |
| winner_id      | UUID (FK to players.player_id) | Winner's identifier                        |
| timestamp      | DATETIME                      | When the match started                     |
| status         | INTEGER                       | (0 for in-game, 1 for ended) Match Status  |