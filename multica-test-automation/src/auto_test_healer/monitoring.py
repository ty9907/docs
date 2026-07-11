from __future__ import annotations

import re
from pathlib import Path

from .models import Anomaly


class LogMonitor:
    """Incrementally scans a local log without modifying the application."""

    def __init__(self, log_path: str | Path, patterns: list[str] | None = None) -> None:
        self.path = Path(log_path)
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns or [r"Exception", r"\bError\b", r"FATAL"]]
        self.position = 0

    def collect(self) -> list[Anomaly]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8", errors="replace") as handle:
            handle.seek(self.position)
            lines = handle.readlines()
            self.position = handle.tell()
        return [
            Anomaly(source="backend", category="backend_exception", message=line.strip(), evidence={"log_path": str(self.path)})
            for line in lines
            if any(pattern.search(line) for pattern in self.patterns)
        ]


def browser_event_to_anomaly(event: dict[str, object]) -> Anomaly | None:
    event_type = str(event.get("type", ""))
    status = int(event.get("status", 0) or 0)
    if event_type == "console" and str(event.get("level", "")).lower() in {"error", "fatal"}:
        return Anomaly(source="frontend", category="browser_console", message=str(event.get("text", "browser error")), evidence=event)
    if event_type == "network" and status >= 400:
        return Anomaly(source="frontend", category="network_error", message=f"HTTP {status}: {event.get('url', '')}", evidence=event)
    return None
