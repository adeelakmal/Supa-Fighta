import os
import pickle

FILE_PATH = "supa-fighta-client/"

def load_player_id(PlayerDataFile):
    global FILE_PATH
    FILE_PATH=os.path.join(FILE_PATH, PlayerDataFile)
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "wb") as f:
            pass
        return None
    else:
        with open(FILE_PATH, "rb") as f:
            return pickle.load(f)

def save_player_id(player_id):
    with open(FILE_PATH, "wb") as f:
        pickle.dump(player_id, f)