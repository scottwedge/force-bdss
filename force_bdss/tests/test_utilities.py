import unittest

from force_bdss.utilities import pop_dunder_recursive, pop_recursive


class TestDictUtils(unittest.TestCase):
    def test_dunder_recursive(self):
        test_dict = {
            "__traits_version__": "4.6.0",
            "some_important_data": {
                "__traits_version__": "4.6.0",
                "value": 10,
            },
            "_some_private_data": {"__instance_traits__": ["yes", "some"]},
            "___": {"__": "a", "foo": "bar"},
            "list_of_dicts": [
                {"__bad_key__": "bad", "good_key": "good"},
                {"also_good_key": "good"},
            ],
        }
        expected = {
            "some_important_data": {"value": 10},
            "_some_private_data": {},
            "list_of_dicts": [{"good_key": "good"}, {"also_good_key": "good"}],
        }
        self.assertEqual(pop_dunder_recursive(test_dict), expected)

    def test_pop_recursive(self):
        test_dictionary = {
            "K1": {"K1": "V1", "K2": "V2", "K3": "V3"},
            "K2": ["V1", "V2", {"K1": "V1", "K2": "V2", "K3": "V3"}],
            "K3": "V3",
            "K4": ("V1", {"K3": "V3"}),
        }

        result_dictionary = {
            "K1": {"K1": "V1", "K2": "V2"},
            "K2": ["V1", "V2", {"K1": "V1", "K2": "V2"}],
            "K4": ("V1", {}),
        }

        test_result_dictionary = pop_recursive(test_dictionary, "K3")
        self.assertEqual(test_result_dictionary, result_dictionary)

        small_dict = {"key": "value"}
        missing_key = "another_key"
        self.assertDictEqual(
            pop_recursive(small_dict, missing_key), small_dict
        )
