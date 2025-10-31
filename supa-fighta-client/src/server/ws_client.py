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
        self.ws.connect(url)
        self._running = True
        self._response = None
        self._response_event = threading.Event()
        threading.Thread(target=self._start_async_recv_loop, daemon=True).start()
        if config.PLAYER_ID:
            self.send({"type":'validate_player', "playerId": config.PLAYER_ID})
        else:
            self.send({"type":'create_player'})
            

    def send(self, payload: dict | None = None):
        """
        Serialise to JSON and push to the server.
        """
        self.ws.send(json.dumps(payload))
    
    def send_snapshot(self, snapshot: dict):
        self._response_event.clear()
        self._response = None
        self.send({"type": "snapshot", "playerId": config.PLAYER_ID, "snapshot": snapshot})

    def get_last_response(self):
        return self._response

    def close(self):
        self._running = False
        self.ws.close()

    def _start_async_recv_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_recv_loop())

    async def _async_recv_loop(self):
        while self._running:
            try:
                msg = await asyncio.to_thread(self.ws.recv)
                if msg:
                    data = json.loads(msg)
                    self._response = data
                    self._response_event.set()
                    
                    if data.get('type') == 'player_created':
                        player_id = data.get('playerId')
                        if player_id:
                            save_player_id(player_id)
                            print(f"✅ New player ID saved: {player_id}")
                            config.PLAYER_ID = player_id

                    #TODO: Add logic in the game state to correct any discrepancies
                    # If message recieved is a snapshot ack, dont need to do anything
                    # If message recieved asks to correct game state, do so
                    print("Srv ▸", msg)
            except websocket.WebSocketConnectionClosedException:
                break
            except Exception:
                await asyncio.sleep(0.1)
