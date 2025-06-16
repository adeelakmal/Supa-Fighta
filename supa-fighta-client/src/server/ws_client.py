import threading
import websocket
import json



class WSClient:
    """
    Very small wrapper around a persistent websocket connection.
    Runs a receive loop on a background thread.
    """

    def __init__(self, url: str):
        self.ws = websocket.WebSocket()
        self.ws.connect(url)
        self._running = True
        threading.Thread(target=self._recv_loop, daemon=True).start()
        self.send({"type":'validate_player', "playerId": "eecb1d48-7e94-4ce9-8b00-1c40e7ddf8e7"})

    def send(self, payload: dict | None = None):
        """
        Serialise to JSON and push to the server.
        """
        self.ws.send(json.dumps(payload))

    def close(self):
        self._running = False
        self.ws.close()

    def _recv_loop(self):
        while self._running:
            try:
                msg = self.ws.recv()
                if msg:
                    print("Srv ▸", msg)
            except websocket.WebSocketConnectionClosedException:
                break
