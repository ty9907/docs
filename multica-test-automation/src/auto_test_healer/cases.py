from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import TestCase


def load_cases(path: str | Path) -> list[TestCase]:
    raw: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    cases = [
        TestCase(
            identifier=item["id"],
            description=item.get("description", item["id"]),
            steps=item.get("steps", []),
            depends_on=item.get("depends_on", []),
        )
        for item in raw.get("cases", [])
    ]
    identifiers = {case.identifier for case in cases}
    if len(identifiers) != len(cases):
        raise ValueError("Test case ids must be unique")
    for case in cases:
        missing = set(case.depends_on) - identifiers
        if missing:
            raise ValueError(f"Case {case.identifier} has missing dependencies: {sorted(missing)}")
    return cases
