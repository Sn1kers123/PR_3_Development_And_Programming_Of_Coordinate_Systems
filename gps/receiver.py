import json
import threading
import time

import websocket

from .config import RECONNECT_S, WS_URL
from .store import GPSStore

FIELDS = ("id", "x", "y", "sentAt", "receivedAt")


class Receiver(threading.Thread):
    def __init__(self, url, store):
        super().__init__(daemon=True)
        self.url = url
        self.store = store

    def _on_message(self, _ws, raw):
        try:
            msg = json.loads(raw)
            if all(k in msg for k in FIELDS):
                self.store.add_measurement(msg)
        except (ValueError, TypeError):
            pass  # пошкоджене повідомлення ігноруємо

    def run(self):
        while True:  # автоматичне перепідключення
            app = websocket.WebSocketApp(
                self.url,
                on_open=lambda _ws: self.store.set_connected(True),
                on_message=self._on_message,
            )
            app.run_forever()
            self.store.set_connected(False)
            time.sleep(RECONNECT_S)


def start_receiver():
    """Створює сховище й запускає потік отримання даних."""
    store = GPSStore()
    Receiver(WS_URL, store).start()
    return store
