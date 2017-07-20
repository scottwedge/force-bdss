import unittest
import json
from six import StringIO

from force_bdss.bundle_registry_plugin import BundleRegistryPlugin
from force_bdss.io.workflow_reader import WorkflowReader

try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.id_generators import bundle_id
from force_bdss.io.workflow_writer import WorkflowWriter
from force_bdss.mco.base_mco_model import BaseMCOModel
from force_bdss.mco.i_multi_criteria_optimizer_bundle import \
    IMultiCriteriaOptimizerBundle
from force_bdss.workspecs.workflow import Workflow


class TestWorkflowWriter(unittest.TestCase):
    def setUp(self):
        self.mock_registry = mock.Mock(spec=BundleRegistryPlugin)
        mock_mco_bundle = mock.Mock(spec=IMultiCriteriaOptimizerBundle,
                                    id=bundle_id("enthought", "mock"))
        mock_mco_model = mock.Mock(
            spec=BaseMCOModel,
            bundle=mock_mco_bundle
        )
        mock_mco_bundle.create_model = mock.Mock(
            return_value = mock_mco_model
        )
        self.mock_registry.mco_bundle_by_id = mock.Mock(
            return_value=mock_mco_bundle)

    def test_write(self):
        wfwriter = WorkflowWriter()
        fp = StringIO()
        wf = self._create_mock_workflow()
        wfwriter.write(wf, fp)
        result = json.loads(fp.getvalue())
        self.assertIn("version", result)
        self.assertIn("workflow", result)
        self.assertIn("multi_criteria_optimizer", result["workflow"])
        self.assertIn("data_sources", result["workflow"])
        self.assertIn("kpi_calculators", result["workflow"])

    def test_write_and_read(self):
        wfwriter = WorkflowWriter()
        fp = StringIO()
        wf = self._create_mock_workflow()
        wfwriter.write(wf, fp)
        fp.seek(0)
        wfreader = WorkflowReader(self.mock_registry)
        wf_result = wfreader.read(fp)
        self.assertEqual(wf_result.multi_criteria_optimizer.bundle.id,
                         wf.multi_criteria_optimizer.bundle.id)

    def _create_mock_workflow(self):
        wf = Workflow()
        wf.multi_criteria_optimizer = BaseMCOModel(
            mock.Mock(
                spec=IMultiCriteriaOptimizerBundle,
                id=bundle_id("enthought", "mock")))
        return wf
