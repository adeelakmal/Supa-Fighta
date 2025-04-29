## Supa Fighta Planning
* Setup a server with websockets
* Use PostgreSQL DB design the schema for the game i.e players, games, stats etc yada yada.
* Get things setup on a local environment.


## 📊 Database Tables

### 🧍‍♂️ players Table

| Column         | Type        | Description                                 |
|:----------------|:------------|:---------------------------------------------|
| player_name    | VARCHAR(50) | Player's name (unique player identifier)    |
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
| player1_name   | VARCHAR(50) (FK to players.player_name) | Player 1                         |
| player2_name   | VARCHAR(50) (FK to players.player_name) | Player 2                         |
| winner_name    | VARCHAR(50) (FK to players.player_name) | Who won                              |
| timestamp      | DATETIME                      | When the match started                   |
| status         | INTEGER                       | (0 for in-game, 1 for ended) Match Status|


ecvwdcvdcwdcv