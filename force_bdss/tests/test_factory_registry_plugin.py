import unittest

from force_bdss.base_extension_plugin import (
    BaseExtensionPlugin)
from force_bdss.ids import factory_id, mco_parameter_id
from force_bdss.mco.parameters.base_mco_parameter_factory import \
    BaseMCOParameterFactory

try:
    import mock
except ImportError:
    from unittest import mock

from envisage.application import Application

from force_bdss.factory_registry_plugin import FactoryRegistryPlugin
from force_bdss.data_sources.i_data_source_factory import IDataSourceFactory
from force_bdss.kpi.i_kpi_calculator_factory import IKPICalculatorFactory
from force_bdss.mco.i_mco_factory import \
    IMCOFactory


class TestFactoryRegistry(unittest.TestCase):
    def setUp(self):
        self.plugin = FactoryRegistryPlugin()
        self.app = Application([self.plugin])
        self.app.start()
        self.app.stop()

    def test_initialization(self):
        self.assertEqual(self.plugin.mco_factories, [])
        self.assertEqual(self.plugin.data_source_factories, [])
        self.assertEqual(self.plugin.kpi_calculator_factories, [])


class MySuperPlugin(BaseExtensionPlugin):
    def _mco_factories_default(self):
        return [
            mock.Mock(
                spec=IMCOFactory,
                id=factory_id("enthought", "mco1"),
                parameter_factories=mock.Mock(return_value=[
                    mock.Mock(
                        spec=BaseMCOParameterFactory,
                        id=mco_parameter_id("enthought", "mco1", "ranged")
                    )
                ]),
            )]

    def _data_source_factories_default(self):
        return [mock.Mock(spec=IDataSourceFactory,
                          id=factory_id("enthought", "ds1")),
                mock.Mock(spec=IDataSourceFactory,
                          id=factory_id("enthought", "ds2"))]

    def _kpi_calculator_factories_default(self):
        return [mock.Mock(spec=IKPICalculatorFactory,
                          id=factory_id("enthought", "kpi1")),
                mock.Mock(spec=IKPICalculatorFactory,
                          id=factory_id("enthought", "kpi2")),
                mock.Mock(spec=IKPICalculatorFactory,
                          id=factory_id("enthought", "kpi3"))]


class TestFactoryRegistryWithContent(unittest.TestCase):
    def setUp(self):
        self.plugin = FactoryRegistryPlugin()
        self.app = Application([self.plugin, MySuperPlugin()])
        self.app.start()
        self.app.stop()

    def test_initialization(self):
        self.assertEqual(len(self.plugin.mco_factories), 1)
        self.assertEqual(len(self.plugin.data_source_factories), 2)
        self.assertEqual(len(self.plugin.kpi_calculator_factories), 3)

    def test_lookup(self):
        mco_id = factory_id("enthought", "mco1")
        parameter_id = mco_parameter_id("enthought", "mco1", "ranged")
        self.assertEqual(self.plugin.mco_factory_by_id(mco_id).id, mco_id)
        self.plugin.mco_parameter_factory_by_id(mco_id, parameter_id)

        for entry in ["ds1", "ds2"]:
            id = factory_id("enthought", entry)
            self.assertEqual(self.plugin.data_source_factory_by_id(id).id, id)

        for entry in ["kpi1", "kpi2", "kpi3"]:
            id = factory_id("enthought", entry)
            self.assertEqual(self.plugin.kpi_calculator_factory_by_id(id).id,
                             id)

        with self.assertRaises(KeyError):
            self.plugin.mco_factory_by_id(
                factory_id("enthought", "foo"))

        with self.assertRaises(KeyError):
            self.plugin.mco_parameter_factory_by_id(
                mco_id,
                mco_parameter_id("enthought", "mco1", "foo")
            )

        with self.assertRaises(KeyError):
            self.plugin.data_source_factory_by_id(
                factory_id("enthought", "foo")
            )

        with self.assertRaises(KeyError):
            self.plugin.data_source_factory_by_id(
                factory_id("enthought", "foo")
            )

        with self.assertRaises(KeyError):
            self.plugin.kpi_calculator_factory_by_id(
                factory_id("enthought", "foo")
            )


if __name__ == '__main__':
    unittest.main()