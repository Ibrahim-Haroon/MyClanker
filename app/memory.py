from __future__ import annotations

from threading import Lock
from typing import Any, Dict, Optional


class InMemoryStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._last_payload: Optional[Dict[str, Any]] = None

    def set_last(self, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._last_payload = payload

    def get_last(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._last_payload


store = InMemoryStore()

