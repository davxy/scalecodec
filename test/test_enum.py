# Python SCALE Codec Library
#
# Copyright 2018-2020 Stichting Polkascan (Polkascan Foundation).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#  test_enum.py
#

import unittest

from scalecodec.base import RuntimeConfigurationObject, ScaleBytes
from scalecodec.type_registry import load_type_registry_preset

# Sparse on purpose: a positional reading of the mapping would encode "Three"
# as 0x01 and could never reach "Max" at all.
SPARSE_TYPE_MAPPING = {0: ("Zero", "Null"), 3: ("Three", "u16"), 255: ("Max", "Null")}

SEQUENTIAL_TYPE_MAPPING = [("Zero", "Null"), ("One", "u16")]


class TestEnum(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runtime_config = RuntimeConfigurationObject()
        cls.runtime_config.clear_type_registry()
        cls.runtime_config.update_type_registry(load_type_registry_preset("core"))

    def enum(self, type_mapping):
        return self.runtime_config.create_scale_object('Enum', type_mapping=type_mapping)

    def test_dict_type_mapping_encodes_the_declared_index(self):
        """A dict type_mapping carries the index, as the dict form of value_list does."""
        self.assertEqual("0x00", self.enum(SPARSE_TYPE_MAPPING).encode({"Zero": None}).to_hex())
        self.assertEqual("0x030100", self.enum(SPARSE_TYPE_MAPPING).encode({"Three": 1}).to_hex())
        self.assertEqual("0xff", self.enum(SPARSE_TYPE_MAPPING).encode({"Max": None}).to_hex())

    def test_dict_type_mapping_round_trips(self):
        for value in ({"Zero": None}, {"Three": 1}, {"Max": None}):
            encoded = self.enum(SPARSE_TYPE_MAPPING).encode(value)
            self.assertEqual(value, self.enum(SPARSE_TYPE_MAPPING).decode(encoded))

    def test_dict_type_mapping_rejects_an_unknown_variant(self):
        with self.assertRaises(ValueError):
            self.enum(SPARSE_TYPE_MAPPING).encode({"Nope": None})

    def test_sequence_type_mapping_still_encodes_by_position(self):
        self.assertEqual("0x00", self.enum(SEQUENTIAL_TYPE_MAPPING).encode({"Zero": None}).to_hex())
        self.assertEqual("0x010100", self.enum(SEQUENTIAL_TYPE_MAPPING).encode({"One": 1}).to_hex())
