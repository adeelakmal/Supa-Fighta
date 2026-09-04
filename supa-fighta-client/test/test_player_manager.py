import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


CLIENT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = CLIENT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from player_manager import (
    clear_player_credentials,
    load_player_credentials,
    save_player_credentials,
)


VALID_TOKEN = "A" * 43


class PlayerCredentialsTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.credentials_path = (
            Path(self.temporary_directory.name) / "player_credentials.json"
        )
        self.player_id = str(uuid.uuid4())

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_credentials_round_trip_as_json(self):
        self.assertTrue(
            save_player_credentials(
                self.player_id,
                VALID_TOKEN,
                self.credentials_path,
            )
        )
        self.assertEqual(
            load_player_credentials(self.credentials_path),
            {"playerId": self.player_id, "playerToken": VALID_TOKEN},
        )

        stored = json.loads(self.credentials_path.read_text(encoding="utf-8"))
        self.assertEqual(
            stored,
            {"playerId": self.player_id, "playerToken": VALID_TOKEN},
        )

    def test_missing_malformed_and_incomplete_files_are_rejected(self):
        self.assertIsNone(load_player_credentials(self.credentials_path))

        invalid_values = [
            "not json",
            json.dumps([]),
            json.dumps({"playerId": self.player_id}),
            json.dumps({"playerId": "not-a-uuid", "playerToken": VALID_TOKEN}),
            json.dumps({"playerId": self.player_id, "playerToken": "short"}),
        ]
        for value in invalid_values:
            with self.subTest(value=value):
                self.credentials_path.write_text(value, encoding="utf-8")
                self.assertIsNone(load_player_credentials(self.credentials_path))

    def test_legacy_pickle_bytes_are_never_deserialized(self):
        self.credentials_path.write_bytes(
            b"cos\nsystem\n(S'echo this-must-not-run'\ntR."
        )

        self.assertIsNone(load_player_credentials(self.credentials_path))

    def test_invalid_credentials_are_not_written(self):
        self.assertFalse(
            save_player_credentials(
                self.player_id,
                "short",
                self.credentials_path,
            )
        )
        self.assertFalse(self.credentials_path.exists())

    def test_credentials_can_be_cleared(self):
        self.assertTrue(
            save_player_credentials(
                self.player_id,
                VALID_TOKEN,
                self.credentials_path,
            )
        )

        self.assertTrue(clear_player_credentials(self.credentials_path))
        self.assertFalse(self.credentials_path.exists())


if __name__ == "__main__":
    unittest.main()
