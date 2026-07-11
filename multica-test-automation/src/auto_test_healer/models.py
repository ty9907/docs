from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any


class ExitReason(str, Enum):
    ALL_PASSED = "ALL_PASSED"
    MAX_RETRIES = "MAX_RETRIES"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    REJECTED = "REJECTED"
    EXECUTION_ERROR = "EXECUTION_ERROR"


@dataclass(frozen=True)
class TestCase:
    identifier: str
    description: str
    steps: list[dict[str, Any]]
    depends_on: list[str] = field(default_factory=list)


@dataclass
class TestResult:
    case_id: str
    passed: bool
    message: str = ""
    duration_seconds: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Anomaly:
    source: str
    category: str
    message: str
    case_id: str | None = None
    file_path: str | None = None
    line_number: int | None = None
    evidence: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time)

    @property
    def fingerprint(self) -> tuple[str, str, str | None, str | None, int | None]:
        return (self.source, self.category, self.case_id, self.file_path, self.line_number)


@dataclass(frozen=True)
class FixProposal:
    target: str
    summary: str
    patch: str
    confidence: float
    files: list[str] = field(default_factory=list)


@dataclass
class FixRecord:
    proposal: FixProposal
    applied: bool
    decision: str
    round_number: int


@dataclass
class LoopState:
    max_retries: int
    confidence_threshold: float
    loop_count: int = 0
    passed_case_ids: set[str] = field(default_factory=set)
    failed_case_ids: set[str] = field(default_factory=set)
    anomalies: list[Anomaly] = field(default_factory=list)
    fixes: list[FixRecord] = field(default_factory=list)
    exit_reason: ExitReason | None = None
