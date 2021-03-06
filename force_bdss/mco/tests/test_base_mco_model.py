#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import unittest

from traits.testing.api import UnittestTools

from force_bdss.core.data_value import DataValue
from force_bdss.tests.dummy_classes.factory_registry import (
    DummyFactoryRegistry,
)
from force_bdss.tests.probe_classes.workflow_file import ProbeWorkflowFile
from force_bdss.tests import fixtures


class TestBaseMCOModel(unittest.TestCase, UnittestTools):
    def setUp(self):
        factory_registry = DummyFactoryRegistry()
        self.mcomodel_factory = factory_registry.mco_factories[0]

    def test_from_json(self):
        empty_data = {
            "parameters": [
                {
                    "id": "force.bdss.enthought.plugin."
                    "test.v0.factory.dummy_mco.parameter."
                    "dummy_mco_parameter",
                    "model_data": {},
                }
            ],
            "kpis": [],
        }
        mco_model = self.mcomodel_factory.model_class.from_json(
            self.mcomodel_factory, empty_data
        )
        self.assertDictEqual(
            mco_model.__getstate__(),
            {
                "id": "force.bdss.enthought.plugin.test.v0."
                "factory.dummy_mco",
                "model_data": {
                    "parameters": [
                        {
                            "id": "force.bdss.enthought.plugin."
                            "test.v0.factory.dummy_mco."
                            "parameter.dummy_mco_parameter",
                            "model_data": {"x": 0, "name": "", "type": ""},
                        }
                    ],
                    "kpis": [],
                },
            },
        )

        self.assertDictEqual(
            empty_data,
            {
                "parameters": [
                    {
                        "id": "force.bdss.enthought.plugin."
                        "test.v0.factory.dummy_mco."
                        "parameter.dummy_mco_parameter",
                        "model_data": {},
                    }
                ],
                "kpis": [],
            },
        )
        with self.assertRaisesRegex(
                RuntimeError,
                "The number of data values returned by"
                r" the MCO \(0 values\) does not match the"
                r" number of parameters specified \(1 values\)."
                " This is either a MCO plugin error or the workflow"
                " file is corrupted."):
            mco_model.bind_parameters([])

    def test_notify_events(self):
        workflow_file = ProbeWorkflowFile(path=fixtures.get("test_probe.json"))
        workflow_file.read()
        workflow = workflow_file.workflow

        with self.assertTraitChanges(workflow, "event", count=1):
            with self.assertTraitChanges(workflow.mco_model, "event", count=1):
                workflow.mco_model.notify_start_event()

        with self.assertTraitChanges(workflow, "event", count=1):
            with self.assertTraitChanges(workflow.mco_model, "event", count=1):
                workflow.mco_model.notify_finish_event()

        with self.assertTraitChanges(workflow, "event", count=1):
            with self.assertTraitChanges(workflow.mco_model, "event", count=1):
                workflow.mco_model.notify_progress_event(
                    [DataValue(value=2), DataValue(value=3)],
                    [DataValue(value=4), DataValue(value=5)]
                )
