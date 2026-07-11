from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import AuditOnlyApplier, PlannedExecutor, RuleBasedDiagnoser
from .cases import load_cases
from .orchestration import LoopController
from .reporting import write_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the guarded self-healing loop in dry-run mode.")
    parser.add_argument("--cases", default="cases/e2e_cases.yaml")
    parser.add_argument("--outcomes", help="JSON file mapping case ids to ordered pass/fail outcomes")
    parser.add_argument("--report", default="reports/latest.md")
    parser.add_argument("--max-retries", type=int, default=3)
    arguments = parser.parse_args()
    outcomes = json.loads(Path(arguments.outcomes).read_text(encoding="utf-8")) if arguments.outcomes else {}
    controller = LoopController(PlannedExecutor(outcomes), [], RuleBasedDiagnoser(), AuditOnlyApplier(), lambda _: "accept", arguments.max_retries)
    state, results = controller.run(load_cases(arguments.cases))
    write_report(arguments.report, state, results)
    print(f"{state.exit_reason.value}: report written to {arguments.report}")
    return 0 if state.exit_reason.value == "ALL_PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
