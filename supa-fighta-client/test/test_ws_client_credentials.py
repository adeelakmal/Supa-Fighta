import sys
import threading
import time
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch


CLIENT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = CLIENT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import config
from server.ws_client import WSClient


class WSClientCredentialMessageTests(unittest.TestCase):
    def setUp(self):
        self.original_player_id = config.PLAYER_ID
        self.original_player_token = config.PLAYER_TOKEN
        self.original_player_name = config.PLAYER_NAME
        self.original_data_file = config.PLAYER_DATA_FILE

        self.client = object.__new__(WSClient)
        self.client._last_server_activity = time.monotonic()
        self.client._heartbeat_lock = threading.Lock()
        self.client._response = None
        self.client._response_event = threading.Event()
        self.client._match_created_message = None
        self.client._match_created_lock = threading.Lock()
        self.client._game_end_message = None
        self.client._game_end_lock = threading.Lock()
        self.client._name_rejected_message = None
        self.client._name_rejected_lock = threading.Lock()
        self.created_player = False
        self.client._create_player = self._record_create_player

    def tearDown(self):
        config.PLAYER_ID = self.original_player_id
        config.PLAYER_TOKEN = self.original_player_token
        config.PLAYER_NAME = self.original_player_name
        config.PLAYER_DATA_FILE = self.original_data_file

    def _record_create_player(self):
        self.created_player = True

    @patch("server.ws_client.clear_player_credentials")
    def test_rejected_credentials_are_cleared_before_replacement(self, clear):
        config.PLAYER_ID = str(uuid.uuid4())
        config.PLAYER_TOKEN = "A" * 43
        config.PLAYER_DATA_FILE = "credentials.json"

        self.assertTrue(
            self.client._handle_server_message(
                {"type": "validation_result", "valid": False}
            )
        )

        self.assertIsNone(config.PLAYER_ID)
        self.assertIsNone(config.PLAYER_TOKEN)
        clear.assert_called_once_with("credentials.json")
        self.assertTrue(self.created_player)

    @patch("server.ws_client.save_player_credentials", return_value=True)
    def test_player_creation_saves_id_and_token_together(self, save):
        player_id = str(uuid.uuid4())
        player_token = "B" * 43
        config.PLAYER_DATA_FILE = "credentials.json"

        self.assertTrue(
            self.client._handle_server_message({
                "type": "player_created",
                "playerId": player_id,
                "playerToken": player_token,
                "username": "Fighter",
            })
        )

        save.assert_called_once_with(
            player_id,
            player_token,
            "credentials.json",
        )
        self.assertEqual(config.PLAYER_ID, player_id)
        self.assertEqual(config.PLAYER_TOKEN, player_token)
        self.assertEqual(config.PLAYER_NAME, "Fighter")


if __name__ == "__main__":
    unittest.main()
