import unittest

import testfixtures
import six

from force_bdss.core.execution_layer import ExecutionLayer
from force_bdss.core.kpi_specification import KPISpecification
from force_bdss.core.output_slot_info import OutputSlotInfo
from force_bdss.core.workflow import Workflow
from force_bdss.tests.probe_classes.data_source import ProbeDataSourceFactory

from force_bdss.core.input_slot_info import InputSlotInfo
from force_bdss.core.data_value import DataValue
from force_bdss.core.slot import Slot
from force_bdss.tests.probe_classes.factory_registry_plugin import \
    ProbeFactoryRegistryPlugin
from force_bdss.tests.probe_classes.mco import ProbeMCOFactory

from force_bdss.execution import execute_workflow, execute_layer, \
    _bind_data_values


class TestExecution(unittest.TestCase):
    def setUp(self):
        self.registry = ProbeFactoryRegistryPlugin()
        self.plugin = self.registry.plugin

    def test_bind_data_values(self):
        data_values = [
            DataValue(name="foo"),
            DataValue(name="bar"),
            DataValue(name="baz")
        ]

        slot_map = (
            InputSlotInfo(name="baz"),
            InputSlotInfo(name="bar")
        )

        slots = (
            Slot(),
            Slot()
        )

        result = _bind_data_values(data_values, slot_map, slots)
        self.assertEqual(result[0], data_values[2])
        self.assertEqual(result[1], data_values[1])

        # Check the errors. Only one slot map for two slots.
        slot_map = (
            InputSlotInfo(name="baz"),
        )

        with testfixtures.LogCapture():
            with six.assertRaisesRegex(
                    self,
                    RuntimeError,
                    "The length of the slots is not equal to the length of"
                    " the slot map"):
                _bind_data_values(data_values, slot_map, slots)

        # missing value in the given data values.
        slot_map = (
            InputSlotInfo(name="blap"),
            InputSlotInfo(name="bar")
        )

        with testfixtures.LogCapture():
            with six.assertRaisesRegex(
                    self,
                    RuntimeError,
                    "Unable to find requested name 'blap' in available"
                    " data values."):
                _bind_data_values(data_values, slot_map, slots)

    def test_compute_layer_results(self):
        data_values = [
            DataValue(name="foo"),
            DataValue(name="bar"),
            DataValue(name="baz"),
            DataValue(name="quux")
        ]

        def run(self, *args, **kwargs):
            return [DataValue(value=1), DataValue(value=2), DataValue(value=3)]

        ds_factory = self.registry.data_source_factories[0]
        ds_factory.input_slots_size = 2
        ds_factory.output_slots_size = 3
        ds_factory.run_function = run
        evaluator_model = ds_factory.create_model()

        evaluator_model.input_slot_info = [
            InputSlotInfo(name="foo"),
            InputSlotInfo(name="quux")
        ]
        evaluator_model.output_slot_info = [
            OutputSlotInfo(name="one"),
            OutputSlotInfo(name=""),
            OutputSlotInfo(name="three")
        ]

        res = execute_layer(
            ExecutionLayer(data_sources=[evaluator_model]),
            data_values,
        )
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].name, "one")
        self.assertEqual(res[0].value, 1)
        self.assertEqual(res[1].name, "three")
        self.assertEqual(res[1].value, 3)

    def test_multilayer_execution(self):
        # The multilayer peforms the following execution
        # layer 0: in1 + in2   | in3 + in4
        #             res1          res2
        # layer 1:        res1 + res2
        #                    res3
        # layer 2:        res3 * res1
        #                     res4
        # layer 3:        res4 * res2
        #                     out1
        # Final result should be
        # out1 = ((in1 + in2 + in3 + in4) * (in1 + in2) * (in3 + in4)

        data_values = [
            DataValue(value=10, name="in1"),
            DataValue(value=15, name="in2"),
            DataValue(value=3, name="in3"),
            DataValue(value=7, name="in4")
        ]

        def adder(model, parameters):

            first = parameters[0].value
            second = parameters[1].value
            return [DataValue(value=(first+second))]

        adder_factory = ProbeDataSourceFactory(
            self.plugin,
            input_slots_size=2,
            output_slots_size=1,
            run_function=adder)

        def multiplier(model, parameters):
            first = parameters[0].value
            second = parameters[1].value
            return [DataValue(value=(first*second))]

        multiplier_factory = ProbeDataSourceFactory(
            self.plugin,
            input_slots_size=2,
            output_slots_size=1,
            run_function=multiplier)

        mco_factory = ProbeMCOFactory(self.plugin)
        mco_model = mco_factory.create_model()
        mco_model.kpis = [
            KPISpecification(name="out1")
        ]

        wf = Workflow(
            mco=mco_model,
            execution_layers=[
                ExecutionLayer(),
                ExecutionLayer(),
                ExecutionLayer(),
                ExecutionLayer()
            ]
        )
        # Layer 0
        model = adder_factory.create_model()
        model.input_slot_info = [
            InputSlotInfo(name="in1"),
            InputSlotInfo(name="in2")
        ]
        model.output_slot_info = [
            OutputSlotInfo(name="res1")
        ]
        wf.execution_layers[0].data_sources.append(model)

        model = adder_factory.create_model()
        model.input_slot_info = [
            InputSlotInfo(name="in3"),
            InputSlotInfo(name="in4")
        ]
        model.output_slot_info = [
            OutputSlotInfo(name="res2")
        ]
        wf.execution_layers[0].data_sources.append(model)

        # layer 1
        model = adder_factory.create_model()
        model.input_slot_info = [
            InputSlotInfo(name="res1"),
            InputSlotInfo(name="res2")
        ]
        model.output_slot_info = [
            OutputSlotInfo(name="res3")
        ]
        wf.execution_layers[1].data_sources.append(model)

        # layer 2
        model = multiplier_factory.create_model()
        model.input_slot_info = [
            InputSlotInfo(name="res3"),
            InputSlotInfo(name="res1")
        ]
        model.output_slot_info = [
            OutputSlotInfo(name="res4")
        ]
        wf.execution_layers[2].data_sources.append(model)

        # layer 3
        model = multiplier_factory.create_model()
        model.input_slot_info = [
            InputSlotInfo(name="res4"),
            InputSlotInfo(name="res2")
        ]
        model.output_slot_info = [
            OutputSlotInfo(name="out1")
        ]
        wf.execution_layers[3].data_sources.append(model)

        kpi_results = execute_workflow(wf, data_values)
        self.assertEqual(len(kpi_results), 1)
        self.assertEqual(kpi_results[0].value, 8750)
