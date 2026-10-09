import threading
import time
from collections import deque

from .config import (HISTORY_LEN, LIGHT_SPEED_KM_PER_MS, MAX_SPREAD_MS,
                     STALE_AFTER_S)
from .trilateration import analytic, numeric


class GPSStore:
    def __init__(self):
        self.lock = threading.Lock()
        self.connected = False
        self.max_spread_ms = MAX_SPREAD_MS
        self.sats = {}
        self.history = deque(maxlen=HISTORY_LEN)
        self.spread = None
        self.skipped = 0
        self.last_xy = None

    def set_connected(self, value):
        with self.lock:
            self.connected = value

    def reset(self):
        with self.lock:
            self.history.clear()
            self.skipped = 0
            self.last_xy = None

    def _prune(self):
        now = time.monotonic()
        for k in [k for k, v in self.sats.items() if now - v["seen"] > STALE_AFTER_S]:
            del self.sats[k]

    def add_measurement(self, msg):
        r = LIGHT_SPEED_KM_PER_MS * (msg["receivedAt"] - msg["sentAt"])  # R = 300·Δt, км
        with self.lock:
            self.sats[msg["id"]] = {
                "x": msg["x"], "y": msg["y"], "r": r,
                "received_at": msg["receivedAt"], "seen": time.monotonic(),
            }
            self._prune()
            self._calculate()

    def _calculate(self):
        if len(self.sats) < 3:
            return
        # три найсвіжіші вимірювання
        used = sorted(self.sats.values(), key=lambda s: s["received_at"])[-3:]
        self.spread = used[-1]["received_at"] - used[0]["received_at"]
        if self.spread > self.max_spread_ms:
            self.skipped += 1
            return

        pts = [(s["x"], s["y"]) for s in used]
        rs = [s["r"] for s in used]

        a = analytic(pts, rs)
        start = a or self.last_xy
        n = numeric(pts, rs, start) if start else None
        if a is None and n is None:
            self.skipped += 1
            return

        self.last_xy = n or a
        self.history.append({"analytic": a, "numeric": n, "spread": self.spread})

    def snapshot(self):
        with self.lock:
            self._prune()
            return {
                "connected": self.connected,
                "sats": [{"id": k, "x": v["x"], "y": v["y"]} for k, v in self.sats.items()],
                "history": list(self.history),
                "spread": self.spread,
                "max_spread": self.max_spread_ms,
                "skipped": self.skipped,
            }
