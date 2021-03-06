#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import unittest

import testfixtures

from traits.trait_errors import TraitError

from force_bdss.data_sources.tests.test_base_data_source import DummyDataSource
from force_bdss.data_sources.tests.test_base_data_source_model import \
    DummyDataSourceModel
from force_bdss.tests.dummy_classes.data_source import DummyDataSourceFactory


class TestBaseDataSourceFactory(unittest.TestCase):
    def setUp(self):
        self.plugin = {'id': "pid", 'name': 'Plugin'}

    def test_initialization(self):
        factory = DummyDataSourceFactory(self.plugin)
        self.assertEqual(factory.id, 'pid.factory.dummy_data_source')
        self.assertEqual(factory.plugin_id, 'pid')
        self.assertEqual(factory.name, 'Dummy data source')
        self.assertEqual(factory.description, "No description available.")
        self.assertEqual(factory.model_class, DummyDataSourceModel)
        self.assertEqual(factory.data_source_class, DummyDataSource)
        self.assertIsInstance(factory.create_data_source(), DummyDataSource)
        self.assertIsInstance(factory.create_model(), DummyDataSourceModel)

    def test_initialization_errors_invalid_idetifier(self):
        class Broken(DummyDataSourceFactory):
            def get_identifier(self):
                return None

        with testfixtures.LogCapture():
            with self.assertRaises(ValueError):
                Broken(self.plugin)

    def test_initialization_errors_invalid_name(self):
        class Broken(DummyDataSourceFactory):
            def get_name(self):
                return None

        with testfixtures.LogCapture():
            with self.assertRaises(TraitError):
                Broken(self.plugin)

    def test_initialization_errors_invalid_model_class(self):
        class Broken(DummyDataSourceFactory):
            def get_model_class(self):
                return None

        with testfixtures.LogCapture():
            with self.assertRaises(TraitError):
                Broken(self.plugin)

    def test_initialization_errors_invalid_data_source_class(self):
        class Broken(DummyDataSourceFactory):
            def get_data_source_class(self):
                return None

        with testfixtures.LogCapture():
            with self.assertRaises(TraitError):
                Broken(self.plugin)
