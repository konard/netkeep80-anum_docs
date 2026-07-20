# -*- coding: utf-8 -*-
"""
Тесты технического reader'а формальной нотации МТС.

Reader проверяет границы контейнеров и source span, но не задаёт смысл формул.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.layers import Layer  # noqa: E402
from core.mtc_reader import find_top_level_operators, read_formula  # noqa: E402


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
        meaning = read_formula('(⟼) : (♀∞ ⟼ ∞♂)', expected_layer=Layer.CONNECTION_MEANING)
        concrete = read_formula('[1] : (⟼)', expected_layer=Layer.CONCRETE_CONNECTION)
        self.assertTrue(meaning.is_valid, meaning.diagnostics)
        self.assertTrue(concrete.is_valid, concrete.diagnostics)
        self.assertEqual(meaning.layer, Layer.CONNECTION_MEANING)
        self.assertEqual(concrete.layer, Layer.CONCRETE_CONNECTION)

    def test_reads_literal_square_abits_inside_round_forms(self):
        left = read_formula('([) : (♀∞)', expected_layer=Layer.FORMAL_FORM)
        right = read_formula('(]) : (∞♂)', expected_layer=Layer.FORMAL_FORM)

        self.assertTrue(left.is_valid, left.diagnostics)
        self.assertTrue(right.is_valid, right.diagnostics)
        self.assertEqual([c.kind for c in left.containers], ['round', 'round'])
        self.assertEqual([c.kind for c in right.containers], ['round', 'round'])
        self.assertIn('[', [token.value for token in left.tokens])
        self.assertIn(']', [token.value for token in right.tokens])

    def test_reads_empty_round_form_as_current_formal_form(self):
        result = read_formula('() : ♀() ⟼ ()♂', expected_layer=Layer.FORMAL_FORM)

        self.assertTrue(result.is_valid, result.diagnostics)
        self.assertEqual([c.kind for c in result.containers], ['round', 'round', 'round'])

    def test_reads_square_abit_forms(self):
        connection = read_formula('[1] : (⟼)', expected_layer=Layer.FORMAL_FORM)
        nonconnection = read_formula('[0] : (↛)', expected_layer=Layer.FORMAL_FORM)

        self.assertTrue(connection.is_valid, connection.diagnostics)
        self.assertTrue(nonconnection.is_valid, nonconnection.diagnostics)
        self.assertEqual(connection.containers[0].kind, 'square')
        self.assertEqual(nonconnection.containers[0].kind, 'square')

    def test_reads_start_end_link_forms(self):
        start = read_formula('♀[] : ♀[] = ♀[] ⟼ []', expected_layer=Layer.SINGLE_CONNECTION_FORM)
        end = read_formula('[]♂ : []♂ = [] ⟼ []♂', expected_layer=Layer.SINGLE_CONNECTION_FORM)

        self.assertTrue(start.is_valid, start.diagnostics)
        self.assertTrue(end.is_valid, end.diagnostics)
        self.assertEqual([c.kind for c in start.containers], ['square', 'square', 'square', 'square'])
        self.assertEqual([c.kind for c in end.containers], ['square', 'square', 'square', 'square'])

    def test_reads_equality_with_current_polarity(self):
        result = read_formula('(=) : {♀[] = ♀[], []♂ = []♂}', expected_layer=Layer.FORMAL_FORM)

        self.assertTrue(result.is_valid, result.diagnostics)
        self.assertEqual(
            [c.kind for c in result.containers],
            ['round', 'curly', 'square', 'square', 'square', 'square'],
        )

    def test_reads_nonequality_negation_definition(self):
        result = read_formula('(!=) : ¬(=)', expected_layer=Layer.FORMAL_FORM)

        self.assertTrue(result.is_valid, result.diagnostics)
        self.assertEqual([c.kind for c in result.containers], ['round', 'round'])

    def test_reads_grouped_sequence_form(self):
        result = read_formula('[]([][]) : [] ⟼ ([][])', expected_layer=Layer.SINGLE_CONNECTION_FORM)

        self.assertTrue(result.is_valid, result.diagnostics)
        self.assertEqual(
            [c.kind for c in result.containers],
            ['square', 'round', 'square', 'square', 'square', 'round', 'square', 'square'],
        )

    def test_reads_nonconnection_assertion(self):
        result = read_formula('{} != []', expected_layer=Layer.FORMAL_FORM)

        self.assertTrue(result.is_valid, result.diagnostics)
        self.assertEqual([c.kind for c in result.containers], ['curly', 'square'])

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
        def first_top_level_operator(text, operator):
            positions = find_top_level_operators(text, operator)
            return positions[0] if positions else None

        self.assertEqual(first_top_level_operator('∞ : [] = [] ⟼ []', ':'), 2)
        self.assertIsNone(first_top_level_operator('(a : b)', ':'))
        self.assertEqual(first_top_level_operator('([) : (♀∞)', ':'), 4)
        self.assertEqual(first_top_level_operator('(]) : (∞♂)', ':'), 4)
        self.assertEqual(first_top_level_operator('[1] : (⟼)', ':'), 4)
        self.assertEqual(first_top_level_operator('[0] : (↛)', ':'), 4)
        self.assertEqual(first_top_level_operator('(!=) : ¬(=)', ':'), 5)
        self.assertIsNone(first_top_level_operator('(!=) : ¬(=)', '!='))
        self.assertEqual(first_top_level_operator('{} != []', '!='), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
