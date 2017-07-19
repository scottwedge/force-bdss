import unittest

from force_bdss.id_generators import bundle_id

try:
    import mock
except ImportError:
    from unittest import mock

from traits.api import List
from envisage.application import Application
from envisage.plugin import Plugin

from force_bdss.bundle_registry_plugin import BundleRegistryPlugin
from force_bdss.data_sources.i_data_source_bundle import IDataSourceBundle
from force_bdss.kpi.i_kpi_calculator_bundle import IKPICalculatorBundle
from force_bdss.mco.i_multi_criteria_optimizer_bundle import \
    IMultiCriteriaOptimizerBundle


class TestBundleRegistry(unittest.TestCase):
    def setUp(self):
        self.plugin = BundleRegistryPlugin()
        self.app = Application([self.plugin])
        self.app.start()
        self.app.stop()

    def test_initialization(self):
        self.assertEqual(self.plugin.mco_bundles, [])
        self.assertEqual(self.plugin.data_source_bundles, [])
        self.assertEqual(self.plugin.kpi_calculator_bundles, [])


class BaseBDSSPlugin(Plugin):
    mco_bundles = List(
        IMultiCriteriaOptimizerBundle,
        contributes_to='force.bdss.mco.bundles'
    )

    #: A list of the available Data Sources.
    #: It will be populated by plugins.
    data_source_bundles = List(
        IDataSourceBundle,
        contributes_to='force.bdss.data_sources.bundles')

    kpi_calculator_bundles = List(
        IKPICalculatorBundle,
        contributes_to='force.bdss.kpi_calculators.bundles'
    )


class MySuperPlugin(BaseBDSSPlugin):
    def _mco_bundles_default(self):
        return [mock.Mock(spec=IMultiCriteriaOptimizerBundle,
                          id=bundle_id("enthought", "mco1"))]

    def _data_source_bundles_default(self):
        return [mock.Mock(spec=IDataSourceBundle,
                          id=bundle_id("enthought", "ds1")),
                mock.Mock(spec=IDataSourceBundle,
                          id=bundle_id("enthought", "ds2"))]

    def _kpi_calculator_bundles_default(self):
        return [mock.Mock(spec=IKPICalculatorBundle,
                          id=bundle_id("enthought", "kpi1")),
                mock.Mock(spec=IKPICalculatorBundle,
                          id=bundle_id("enthought", "kpi2")),
                mock.Mock(spec=IKPICalculatorBundle,
                          id=bundle_id("enthought", "kpi3"))]


class TestBundleRegistryWithContent(unittest.TestCase):
    def setUp(self):
        self.plugin = BundleRegistryPlugin()
        self.app = Application([self.plugin, MySuperPlugin()])
        self.app.start()
        self.app.stop()

    def test_initialization(self):
        self.assertEqual(len(self.plugin.mco_bundles), 1)
        self.assertEqual(len(self.plugin.data_source_bundles), 2)
        self.assertEqual(len(self.plugin.kpi_calculator_bundles), 3)

    def test_lookup(self):
        id = bundle_id("enthought", "mco1")
        self.assertEqual(self.plugin.mco_bundle_by_id(id).id, id)

        for entry in ["ds1", "ds2"]:
            id = bundle_id("enthought", entry)
            self.assertEqual(self.plugin.data_source_bundle_by_id(id).id, id)

        for entry in ["kpi1", "kpi2", "kpi3"]:
            id = bundle_id("enthought", entry)
            self.assertEqual(self.plugin.kpi_calculator_bundle_by_id(id).id,
                             id)


if __name__ == '__main__':
    unittest.main()
