from __future__ import annotations

from dataclasses import dataclass

from .models import Anomaly, FixProposal, TestCase, TestResult


@dataclass
class PlannedExecutor:
    """Deterministic adapter for local validation and Multica dry runs."""
    outcomes: dict[str, list[bool]]

    def execute(self, case: TestCase) -> TestResult:
        attempts = self.outcomes.get(case.identifier, [True])
        passed = attempts.pop(0) if attempts else True
        return TestResult(case.identifier, passed, "" if passed else "Configured test failure")


class RuleBasedDiagnoser:
    def propose(self, anomalies: list[Anomaly]) -> FixProposal:
        category = anomalies[0].category if anomalies else "unknown"
        target = "frontend-engineer" if category in {"browser_console", "network_error", "selector_failure"} else "backend-engineer"
        return FixProposal(target=target, summary=f"Investigate {category}", patch="# Generated proposal; apply through Multica repair agent.", confidence=0.8)


class AuditOnlyApplier:
    def __init__(self) -> None:
        self.applied: list[FixProposal] = []

    def apply(self, proposal: FixProposal) -> None:
        self.applied.append(proposal)
