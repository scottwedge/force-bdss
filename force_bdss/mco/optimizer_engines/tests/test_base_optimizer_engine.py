from unittest import TestCase

from force_bdss.core.kpi_specification import KPISpecification
from force_bdss.tests.dummy_classes.optimizer_engine import (
    EmptyOptimizerEngine,
)
from force_bdss.tests.probe_classes.workflow_file import ProbeWorkflowFile
from force_bdss.tests import fixtures


class TestBaseOptimizerEngine(TestCase):
    def setUp(self):
        workflow_file = ProbeWorkflowFile(path=fixtures.get("test_probe.json"))
        workflow_file.read()
        self.workflow = workflow_file.workflow
        self.optimizer_engine = EmptyOptimizerEngine(
            single_point_evaluator=self.workflow
        )

    def test_initialize(self):
        self.assertIs(
            self.workflow, self.optimizer_engine.single_point_evaluator
        )
        self.assertListEqual([], self.optimizer_engine.parameters)
        self.assertListEqual([], self.optimizer_engine.kpis)

    def test_base_methods(self):
        self.assertListEqual([0.0], self.optimizer_engine.optimize())

        point = [1.0]
        self.assertListEqual(
            self.workflow.evaluate(point), self.optimizer_engine._score(point)
        )

    def test__minimization_score(self):
        temp_kpis = [
            KPISpecification(),
            KPISpecification(objective="MAXIMISE"),
        ]
        self.optimizer_engine.kpis = temp_kpis
        score = [10.0, 20.0]
        inv_values = self.optimizer_engine._minimization_score(score)
        self.assertListEqual(list(inv_values), [10.0, -20.0])

    def test___getstate__(self):
        state_dict = self.optimizer_engine.__getstate__()
        self.assertEqual(1, len(state_dict))
        self.assertEqual(False, state_dict["verbose_run"])