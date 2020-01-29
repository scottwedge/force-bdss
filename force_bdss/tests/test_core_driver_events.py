import unittest

from traits.api import Instance, Int

from force_bdss.core.data_value import DataValue
from force_bdss.core_driver_events import (
    MCOProgressEvent,
    WeightedMCOProgressEvent,
    MCOStartEvent,
    WeightedMCOStartEvent,
    MCOFinishEvent,
    BaseDriverEvent,
    DriverEventTypeError,
)


class DummyEvent(BaseDriverEvent):
    stateless_data = Int(1)
    stateful_data = Instance(DataValue)


class TestCoreDriverEvents(unittest.TestCase):
    def test_getstate_progress_event(self):
        ev = MCOProgressEvent(
            optimal_kpis=[DataValue(value=10)],
            optimal_point=[DataValue(value=12), DataValue(value=13)],
        )

        self.assertEqual(
            ev.__getstate__(),
            {
                "id": "force_bdss.core_driver_events.MCOProgressEvent",
                "model_data": {
                    "optimal_kpis": [
                        {
                            "accuracy": None,
                            "name": "",
                            "quality": "AVERAGE",
                            "type": "",
                            "value": 10,
                        }
                    ],
                    "optimal_point": [
                        {
                            "accuracy": None,
                            "name": "",
                            "quality": "AVERAGE",
                            "type": "",
                            "value": 12,
                        },
                        {
                            "accuracy": None,
                            "name": "",
                            "quality": "AVERAGE",
                            "type": "",
                            "value": 13,
                        },
                    ],
                },
            },
        )

    def test_getstate_start_event(self):
        event = MCOStartEvent(
            parameter_names=["p1", "p2"], kpi_names=["k1", "k2", "k3"]
        )
        self.assertDictEqual(
            event.__getstate__(),
            {
                "model_data": {
                    "parameter_names": ["p1", "p2"],
                    "kpi_names": ["k1", "k2", "k3"],
                },
                "id": "force_bdss.core_driver_events.MCOStartEvent",
            },
        )

    def test_getstate_finish_event(self):
        event = MCOFinishEvent()
        self.assertDictEqual(
            event.__getstate__(),
            {
                "model_data": {},
                "id": "force_bdss.core_driver_events.MCOFinishEvent",
            },
        )

    def test_getstate_base_event(self):
        event = BaseDriverEvent()
        self.assertDictEqual(
            event.__getstate__(),
            {
                "id": "force_bdss.core_driver_events.BaseDriverEvent",
                "model_data": {},
            },
        )

        event = DummyEvent(stateful_data=DataValue(value=1))
        self.assertDictEqual(
            event.__getstate__(),
            {
                "id": "force_bdss.tests.test_core_driver_events.DummyEvent",
                "model_data": {
                    "stateless_data": 1,
                    "stateful_data": {
                        "accuracy": None,
                        "name": "",
                        "quality": "AVERAGE",
                        "type": "",
                        "value": 1,
                    },
                },
            },
        )

    def test_serialize_start_event(self):
        event = MCOStartEvent(
            parameter_names=["p1", "p2"], kpi_names=["k1", "k2", "k3"]
        )
        self.assertListEqual(["p1", "p2", "k1", "k2", "k3"], event.serialize())

        event = WeightedMCOStartEvent(
            parameter_names=["p1", "p2"], kpi_names=["k1", "k2", "k3"]
        )
        self.assertListEqual(
            [
                "p1",
                "p2",
                "k1",
                "k1 weight",
                "k2",
                "k2 weight",
                "k3",
                "k3 weight",
            ],
            event.serialize(),
        )

    def test_serialize_progress_event(self):
        event = MCOProgressEvent(
            optimal_kpis=[DataValue(value=10)],
            optimal_point=[DataValue(value=12), DataValue(value=13)],
        )

        self.assertListEqual(event.serialize(), [12, 13, 10])

        event = WeightedMCOProgressEvent(
            optimal_kpis=[DataValue(value=10)],
            optimal_point=[DataValue(value=12), DataValue(value=13)],
            weights=[1.0],
        )

        self.assertListEqual([12, 13, 10, 1.0], event.serialize())

    def test_default_weights_weighted_progress_event(self):
        event = WeightedMCOProgressEvent(
            optimal_kpis=[DataValue(value=10)],
            optimal_point=[DataValue(value=12), DataValue(value=13)],
        )
        self.assertEqual(len(event.optimal_kpis), len(event.weights))
        self.assertListEqual(
            event.weights,
            [1.0 / len(event.optimal_kpis)] * len(event.optimal_kpis),
        )
        self.assertEqual(event.serialize(), [12, 13, 10, 1.0])

        event = WeightedMCOProgressEvent(
            optimal_kpis=[],
            optimal_point=[DataValue(value=12), DataValue(value=13)],
        )
        self.assertEqual(len(event.optimal_kpis), len(event.weights))
        self.assertListEqual(event.weights, [])
        self.assertEqual(event.serialize(), [12, 13])

    def test_get_event_class(self):
        data = {
            "id": "force_bdss.core_driver_events.BaseDriverEvent",
            "model_data": {},
        }
        klass = BaseDriverEvent.get_event_class(data["id"])
        self.assertIs(klass, BaseDriverEvent)

        data = {
            "id": "force_bdss.core_driver_events.MCOProgressEvent",
            "model_data": {},
        }
        klass = BaseDriverEvent.get_event_class(data["id"])
        self.assertIs(klass, MCOProgressEvent)

        data = {
            "id": "force_bdss.core_driver_events.MCOStartEvent",
            "model_data": {},
        }
        klass = BaseDriverEvent.get_event_class(data["id"])
        self.assertIs(klass, MCOStartEvent)

        data = {
            "id": "force_bdss.core_driver_events.MCOFinishEvent",
            "model_data": {},
        }
        klass = BaseDriverEvent.get_event_class(data["id"])
        self.assertIs(klass, MCOFinishEvent)

        data = {"id": "force_bdss.mco.base_mco.BaseMCO", "model_data": {}}
        error_message = (
            "Class <class 'force_bdss.mco.base_mco.BaseMCO'> "
            "must be a subclass of BaseDriverEvent"
        )
        with self.assertRaisesRegex(DriverEventTypeError, error_message):
            BaseDriverEvent.get_event_class(data["id"])

        data = {"id": "force_bdss.mco.base_mco.RandomClass", "model_data": {}}
        with self.assertRaisesRegex(
            ImportError,
            "Unable to locate the class definition RandomClass in module "
            "<.*> "
            f"requested by the event with id {data['id']}",
        ):
            BaseDriverEvent.get_event_class(data["id"])
