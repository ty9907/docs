from __future__ import annotations

from collections.abc import Iterable

from .contracts import ApprovalProvider, Diagnoser, FixApplier, Monitor, TestExecutor
from .models import Anomaly, ExitReason, FixRecord, LoopState, TestCase, TestResult


def deduplicate(anomalies: Iterable[Anomaly]) -> list[Anomaly]:
    unique: dict[tuple[str, str, str | None, str | None, int | None], Anomaly] = {}
    for anomaly in anomalies:
        unique.setdefault(anomaly.fingerprint, anomaly)
    return list(unique.values())


class LoopController:
    def __init__(self, executor: TestExecutor, monitors: list[Monitor], diagnoser: Diagnoser, applier: FixApplier, approve: ApprovalProvider, max_retries: int = 3, confidence_threshold: float = 0.7) -> None:
        self.executor, self.monitors, self.diagnoser, self.applier, self.approve = executor, monitors, diagnoser, applier, approve
        self.state = LoopState(max_retries=max_retries, confidence_threshold=confidence_threshold)

    def run(self, cases: list[TestCase]) -> tuple[LoopState, list[TestResult]]:
        by_id = {case.identifier: case for case in cases}
        pending = list(cases)
        results: dict[str, TestResult] = {}
        while pending and self.state.loop_count < self.state.max_retries:
            self.state.loop_count += 1
            failed_this_round: list[str] = []
            for case in pending:
                if any(dependency not in self.state.passed_case_ids for dependency in case.depends_on):
                    results[case.identifier] = TestResult(case.identifier, False, "Blocked by failed dependency")
                    failed_this_round.append(case.identifier)
                    continue
                result = self.executor.execute(case)
                results[case.identifier] = result
                if result.passed:
                    self.state.passed_case_ids.add(case.identifier)
                else:
                    failed_this_round.append(case.identifier)
            self.state.failed_case_ids = set(failed_this_round)
            if not failed_this_round:
                self.state.exit_reason = ExitReason.ALL_PASSED
                return self.state, list(results.values())
            anomalies = deduplicate(anomaly for monitor in self.monitors for anomaly in monitor.collect())
            anomalies.extend(Anomaly(source="test", category="test_failure", message=results[case_id].message, case_id=case_id) for case_id in failed_this_round)
            self.state.anomalies.extend(deduplicate(anomalies))
            proposal = self.diagnoser.propose(deduplicate(anomalies))
            if proposal.confidence < self.state.confidence_threshold:
                self.state.exit_reason = ExitReason.LOW_CONFIDENCE
                return self.state, list(results.values())
            decision = self.approve(proposal).lower().strip()
            if decision != "accept":
                self.state.fixes.append(FixRecord(proposal, False, decision, self.state.loop_count))
                self.state.exit_reason = ExitReason.REJECTED
                return self.state, list(results.values())
            self.applier.apply(proposal)
            self.state.fixes.append(FixRecord(proposal, True, decision, self.state.loop_count))
            pending = self._retry_set(failed_this_round, by_id)
        self.state.exit_reason = ExitReason.MAX_RETRIES
        return self.state, list(results.values())

    def _retry_set(self, failed_ids: list[str], by_id: dict[str, TestCase]) -> list[TestCase]:
        retry_ids = set(failed_ids)
        changed = True
        while changed:
            changed = False
            for case in by_id.values():
                if any(dependency in retry_ids for dependency in case.depends_on) and case.identifier not in retry_ids:
                    retry_ids.add(case.identifier)
                    changed = True
        return [case for case in by_id.values() if case.identifier in retry_ids]
