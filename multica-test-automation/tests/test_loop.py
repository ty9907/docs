import unittest

from auto_test_healer.adapters import AuditOnlyApplier, PlannedExecutor, RuleBasedDiagnoser
from auto_test_healer.models import ExitReason, TestCase
from auto_test_healer.orchestration import LoopController


class LoopControllerTests(unittest.TestCase):
    def make_controller(self, outcomes, retries=3):
        return LoopController(PlannedExecutor(outcomes), [], RuleBasedDiagnoser(), AuditOnlyApplier(), lambda _: "accept", retries)

    def test_retries_failed_case_and_passes(self):
        controller = self.make_controller({"login": [False, True]})
        state, results = controller.run([TestCase("login", "Login", [])])
        self.assertEqual(state.exit_reason, ExitReason.ALL_PASSED)
        self.assertEqual(state.loop_count, 2)
        self.assertTrue(results[0].passed)

    def test_retries_downstream_dependents(self):
        controller = self.make_controller({"login": [True], "order": [False, True]})
        state, results = controller.run([TestCase("login", "Login", []), TestCase("order", "Order", [], ["login"])])
        self.assertEqual(state.exit_reason, ExitReason.ALL_PASSED)
        self.assertEqual({result.case_id for result in results}, {"login", "order"})

    def test_stops_after_limit(self):
        controller = self.make_controller({"login": [False, False]}, retries=2)
        state, _ = controller.run([TestCase("login", "Login", [])])
        self.assertEqual(state.exit_reason, ExitReason.MAX_RETRIES)


if __name__ == "__main__":
    unittest.main()
