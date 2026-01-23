import os
import pickle


def load_player_id(PlayerDataFile):
    if not os.path.exists(PlayerDataFile):
        with open(PlayerDataFile, "wb") as f:
            pass
        return None
    else:
        with open(PlayerDataFile, "rb") as f:
            return pickle.load(f)

def save_player_id(player_id, PlayerDataFile="player_data.dat"):
    with open(PlayerDataFile, "wb") as f:
        pickle.dump(player_id, f)