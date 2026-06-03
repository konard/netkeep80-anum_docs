# -*- coding: utf-8 -*-
"""
Тесты технического reader'а формальной нотации МТС.

Reader проверяет границы контейнеров и source span, но не является EBNF-
грамматикой и не задаёт смысл формул.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.layers import Layer  # noqa: E402
from core.mtc_reader import find_top_level_operator, read_formula  # noqa: E402


class TestMTCReader(unittest.TestCase):
    """Reader читает ключевые формы без назначения внешней грамматики."""

    def test_reads_definition_formula(self):
        result = read_formula('∞ : [] = [] ⟼ []', expected_layer=Layer.FORMAL_FORM)
        self.assertTrue(result.is_valid, result.diagnostics)
        self.assertEqual(result.layer, Layer.FORMAL_FORM)
        self.assertEqual(result.containers[0].kind, 'square')

    def test_reads_bundle_formula(self):
        result = read_formula('{[], []} = {[]}', expected_layer=Layer.FORMAL_FORM)
        self.assertTrue(result.is_valid, result.diagnostics)
        self.assertEqual([c.kind for c in result.containers], ['curly', 'square', 'square', 'curly', 'square'])

    def test_preserves_layer_distinction_in_containers(self):
        meaning = read_formula('(⟼) : [] ⟼ []', expected_layer=Layer.CONNECTION_MEANING)
        concrete = read_formula('[⟼] : ∞♀ ⟼ ♂∞', expected_layer=Layer.CONCRETE_CONNECTION)
        self.assertTrue(meaning.is_valid, meaning.diagnostics)
        self.assertTrue(concrete.is_valid, concrete.diagnostics)
        self.assertEqual(meaning.layer, Layer.CONNECTION_MEANING)
        self.assertEqual(concrete.layer, Layer.CONCRETE_CONNECTION)

    def test_unclosed_container_is_invalid(self):
        result = read_formula('{[]', expected_layer=Layer.FORMAL_FORM)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.status, 'invalid')
        self.assertTrue(any('Незакрытый контейнер' in d for d in result.diagnostics))

    def test_reader_without_layer_is_ambiguous_not_valid_specification(self):
        result = read_formula('[] = ∞')
        self.assertEqual(result.status, 'ambiguous')
        self.assertFalse(result.is_valid)
        self.assertTrue(any('Слой чтения не указан' in d for d in result.diagnostics))

    def test_finds_only_top_level_definition_operator(self):
        self.assertEqual(find_top_level_operator('∞ : [] = [] ⟼ []', ':'), 2)
        self.assertIsNone(find_top_level_operator('(a : b)', ':'))
        self.assertEqual(find_top_level_operator('[ : ∞♀', ':'), 2)
        self.assertEqual(find_top_level_operator('] : ♂∞', ':'), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
