# -*- coding: utf-8 -*-
"""
Тесты загрузки корневой библиотеки формул МТС.

Эти проверки фиксируют новое направление issue #46: первичный источник
формальной нотации находится в ``tests/mtc_formulas.mtc``, а не в legacy
Python AST/parser правилах.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.layers import Layer  # noqa: E402
from core.root_library import FormulaKind, load_root_library  # noqa: E402
from core.validate_root import validate_root_library  # noqa: E402


ROOT_FORMULAS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'mtc_formulas.mtc',
)


class TestRootLibrary(unittest.TestCase):
    """Корневая библиотека читается из .mtc с source locations."""

    def setUp(self):
        self.library = load_root_library(ROOT_FORMULAS)

    def test_loads_mtc_formulas(self):
        self.assertGreaterEqual(len(self.library.formulas), 30)
        self.assertTrue(all(formula.text for formula in self.library.formulas))

    def test_source_locations_are_preserved(self):
        first = self.library.formulas[0]
        self.assertEqual(first.text, '∞ : [] = [] ⟼ []')
        self.assertTrue(first.source_path.endswith('mtc_formulas.mtc'))
        self.assertEqual(first.line_no, 10)

    def test_root_contains_key_formulas(self):
        texts = set(self.library.texts())
        self.assertIn('∞ : [] = [] ⟼ []', texts)
        self.assertIn('(⟼) : [] ⟼ []', texts)
        self.assertIn('[⟼] : ∞♀ ⟼ ♂∞', texts)
        self.assertIn('(!=) : ¬(=)', texts)

    def test_difference_registry_is_built_from_definitions(self):
        registry = self.library.registry
        self.assertIsNotNone(registry.lookup('∞'))
        self.assertIsNotNone(registry.lookup('(⟼)'))
        self.assertIsNotNone(registry.lookup('[⟼]'))
        self.assertIsNotNone(registry.lookup('['))
        self.assertIsNotNone(registry.lookup(']'))
        self.assertIsNotNone(registry.lookup('1'))
        self.assertIsNotNone(registry.lookup('0'))

    def test_square_abits_are_exactly_four_and_infinity_is_not_abit(self):
        self.assertEqual(set(self.library.square_abits()), {'[', ']', '1', '0'})
        self.assertNotIn('∞', self.library.square_abits())

    def test_formula_kinds_are_detected_from_top_level_operators(self):
        kinds = {formula.text: formula.kind for formula in self.library.formulas}
        self.assertEqual(kinds['∞ : [] = [] ⟼ []'], FormulaKind.DEFINITION)
        self.assertEqual(kinds['[] = ∞'], FormulaKind.EQUATION)
        self.assertEqual(kinds['{} != []'], FormulaKind.NON_EQUATION)

    def test_colon_inside_container_is_not_a_definition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            formula_path = os.path.join(tmpdir, 'nested_colon.mtc')
            with open(formula_path, 'w', encoding='utf-8') as target:
                target.write('(a : b)\n')

            library = load_root_library(formula_path)
            self.assertEqual(library.formulas[0].kind, FormulaKind.EXPRESSION)
            self.assertEqual(library.registry.symbols(), [])

    def test_literal_square_abit_definitions_still_work(self):
        registry = self.library.registry
        self.assertEqual(registry.lookup('[').introduction, '∞♀')
        self.assertEqual(registry.lookup(']').introduction, '♂∞')

    def test_infinity_layer_is_not_quaternary(self):
        entry = self.library.registry.lookup('∞')
        self.assertIsNotNone(entry)
        self.assertNotEqual(entry.layer, Layer.QUATERNARY_SERIALIZATION)


class TestRootValidation(unittest.TestCase):
    """Минимальная валидация корневой библиотеки."""

    def test_root_library_validates(self):
        result = validate_root_library(ROOT_FORMULAS)
        self.assertTrue(result.is_valid, result.messages)
        self.assertEqual(result.status, 'valid')

    def test_duplicate_definitions_are_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            formula_path = os.path.join(tmpdir, 'duplicate_defs.mtc')
            with open(formula_path, 'w', encoding='utf-8') as target:
                target.write('∞ : [] = [] ⟼ []\n')
                target.write('∞ : []\n')

            result = validate_root_library(formula_path)
            self.assertFalse(result.is_valid)
            self.assertTrue(
                any('Повторное введение различия' in message for message in result.messages),
                result.messages,
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)
