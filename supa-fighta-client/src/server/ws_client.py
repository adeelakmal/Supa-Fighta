import threading
import websocket
import json
import asyncio
import config
from player_manager import save_player_id

class WSClient:
    """
    Very small wrapper around a persistent websocket connection.
    Runs a receive loop on a background thread.
    """

    def __init__(self, url: str):
        self.ws = websocket.WebSocket()
        try:
            self.ws.connect(url, timeout=config.WS_CONNECT_TIMEOUT)
            self.ws.settimeout(None)
        except Exception as error:
            self.ws.close()
            raise ConnectionError("Could not connect to the game server.") from error

        self._running = True
        self._connected = True
        self._connection_error = None
        self._connection_lock = threading.Lock()
        self._response = None
        self.last_opponent_update = None
        self.last_player_correction = None
        self._match_created_message = None
        self._match_created_lock = threading.Lock()
        self._game_end_message = None
        self._game_end_lock = threading.Lock()
        self._response_event = threading.Event()
        self._recv_thread = threading.Thread(target=self._start_async_recv_loop, daemon=True)
        self._recv_thread.start()
        if config.PLAYER_ID:
            self.send({"type":'validate_player', "playerId": config.PLAYER_ID})
        else:
            self._create_player()
            

    def send(self, payload: dict | None = None):
        """
        Serialise to JSON and push to the server.
        """
        try:
            self.ws.send(json.dumps(payload))
            return True
        except Exception as e:
            print(f"Failed to send message: {e}")
            self._mark_connection_lost("The connection to the server was lost.")
            return False
    
    def send_snapshot(self, snapshot: dict):
        self._response_event.clear()
        self._response = None
        self.send({"type": "snapshot", "playerId": config.PLAYER_ID, "snapshot": snapshot})

    def get_last_response(self):
        return self._response

    def get_game_end_message(self):
        """Return a game-end message once without letting snapshots erase it."""
        with self._game_end_lock:
            message = self._game_end_message
            self._game_end_message = None
            return message

    def get_match_created_message(self):
        """Return the match message once, after the lobby is ready for it."""
        with self._match_created_lock:
            message = self._match_created_message
            self._match_created_message = None
            return message

    def get_connection_error(self):
        with self._connection_lock:
            return self._connection_error
    
    def get_last_opponent_update(self):
        update = self.last_opponent_update
        self.last_opponent_update = None
        return update
    
    def get_last_player_correction(self):
        correction = self.last_player_correction
        self.last_player_correction = None
        return correction

    def close(self):
        """Close the WebSocket connection gracefully."""
        print("Closing WebSocket connection...")
        self._running = False
        with self._connection_lock:
            self._connected = False
        try:
            self.ws.close()
        except Exception as e:
            print(f"Error closing WebSocket: {e}")

    def _create_player(self):
        self.send({
            "type": "create_player",
            "username": config.PLAYER_NAME
        })

    def _mark_connection_lost(self, message):
        # The game screen handles the message and gives the player a retry button.
        with self._connection_lock:
            if self._connection_error is None:
                self._connection_error = message
            self._connected = False
        self._running = False

    def _handle_server_message(self, data):
        self._response = data
        self._response_event.set()

        message_type = data.get('type')
        if message_type == 'match_created':
            # Keep this safe so a normal update cannot replace it.
            with self._match_created_lock:
                self._match_created_message = data

        if message_type == 'game_end':
            with self._game_end_lock:
                self._game_end_message = data

        if message_type == 'error':
            error_message = str(
                data.get('message') or "The server reported an error."
            )
            print(f"Server error: {error_message}")
            self._mark_connection_lost(error_message)
            return False

        if message_type == 'validation_result' and data.get('valid') is False:
            # Old saves happen sometimes, so make a fresh player and keep going.
            config.PLAYER_ID = None
            save_player_id(None, config.PLAYER_DATA_FILE)
            self._create_player()

        if message_type == 'player_created':
            player_id = data.get('playerId')
            if player_id:
                save_player_id(player_id, config.PLAYER_DATA_FILE)
                print(f"New player ID saved: {player_id}")
                config.PLAYER_ID = player_id

        if message_type == 'opponent_update':
            self.last_opponent_update = data

        if message_type == 'correction':
            self.last_player_correction = float(data.get('position'))
            print(f"Received position correction from server: {self.last_player_correction}")

        return True

    def _start_async_recv_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_recv_loop())

    async def _async_recv_loop(self):
        while self._running:
            try:
                msg = await asyncio.to_thread(self.ws.recv)
                if not msg:
                    if self._running:
                        self._mark_connection_lost("The connection to the server was lost.")
                    break

                data = json.loads(msg)
                if not self._handle_server_message(data):
                    break

            except websocket.WebSocketConnectionClosedException:
                if self._running:
                    print("WebSocket connection closed by server")
                    self._mark_connection_lost("The connection to the server was lost.")
                break
            except Exception as e:
                if self._running:
                    print(f"Error in receive loop: {e}")
                    self._mark_connection_lost("The connection to the server was lost.")
                break
