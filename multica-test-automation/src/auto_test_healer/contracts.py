from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Protocol

from .models import Anomaly, FixProposal, TestCase, TestResult


class TestExecutor(Protocol):
    def execute(self, case: TestCase) -> TestResult: ...


class Monitor(Protocol):
    def collect(self) -> Iterable[Anomaly]: ...


class Diagnoser(Protocol):
    def propose(self, anomalies: list[Anomaly]) -> FixProposal: ...


class FixApplier(Protocol):
    def apply(self, proposal: FixProposal) -> None: ...


ApprovalProvider = Callable[[FixProposal], str]
