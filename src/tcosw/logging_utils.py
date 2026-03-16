from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BoundedLogger:
    max_entries: int = 64
    max_payload_chars: int = 3500
    entries: list[dict[str, Any]] = field(default_factory=list)

    def log(self, event: str, **payload: Any) -> None:
        if len(self.entries) >= self.max_entries:
            return
        self.entries.append({"event": event, **payload})

    def serialize(self) -> str:
        raw = json.dumps(self.entries, separators=(",", ":"))
        if len(raw) <= self.max_payload_chars:
            return raw

        trimmed_entries = self.entries[:]
        while len(trimmed_entries) > 0:
            trimmed_entries.pop()
            candidate = json.dumps(
                trimmed_entries + [{"event": "truncated", "dropped": len(self.entries) - len(trimmed_entries)}],
                separators=(",", ":"),
            )
            if len(candidate) <= self.max_payload_chars:
                return candidate

        return "[]"
