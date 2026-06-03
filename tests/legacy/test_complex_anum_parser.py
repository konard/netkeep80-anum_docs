# -*- coding: utf-8 -*-
"""
Legacy-тесты парсера сложных ачисел (parsers/complex_anum_parser.py).

Эти проверки сохраняют поведение старого compatibility parser до его замены
reader'ом формальной нотации МТС. Они не являются спецификацией текущей
корневой нотации.

Покрывают обработку выражений вида
window(position)(10)(int) с корректным разграничением абитов,
идентификаторов и чисел внутри скобок.

Запуск:
  python3 tests/legacy/test_complex_anum_parser.py
"""

import sys
import os
import unittest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_REPO_ROOT, 'parsers'))

from extended_anum_parser import AbitNotation  # noqa: E402
from complex_anum_parser import (  # noqa: E402
    ComplexAnumLexer, ComplexAnumParser,
    StringAnum, NumberAnum, ContextGroup, ComplexAnumStructure
)


def _parse(text):
    notation = AbitNotation('new_abit_notation')
    lexer = ComplexAnumLexer(text, notation)
    return ComplexAnumParser(lexer).parse()


class TestBaseExpressions(unittest.TestCase):
    """Базовые выражения без контекстных групп."""

    def test_identifier_becomes_string_anum(self):
        result = _parse('window')
        self.assertIsInstance(result, StringAnum)
        self.assertEqual(result.text, 'window')
        # Строка раскладывается только в абиты 1/0.
        self.assertTrue(set(result.anum_sequence) <= {'1', '0'})

    def test_number_becomes_number_anum(self):
        result = _parse('42')
        self.assertIsInstance(result, NumberAnum)
        self.assertEqual(result.number, 42)


class TestComplexStructures(unittest.TestCase):
    """Сложные структуры base(group)(group)..."""

    def test_single_context_group(self):
        result = _parse('window(position)')
        self.assertIsInstance(result, ComplexAnumStructure)
        self.assertEqual(result.base_anum.text, 'window')
        self.assertEqual(len(result.context_groups), 1)
        self.assertIsInstance(result.context_groups[0], ContextGroup)

    def test_multiple_context_groups(self):
        result = _parse('window(position)(10)(int)')
        self.assertIsInstance(result, ComplexAnumStructure)
        self.assertEqual(len(result.context_groups), 3)

    def test_number_inside_parens_stays_number(self):
        # Внутри скобок 10 — это число, а НЕ абиты 1 и 0.
        result = _parse('window(10)')
        group = result.context_groups[0]
        self.assertEqual(len(group.expressions), 1)
        self.assertIsInstance(group.expressions[0], NumberAnum)
        self.assertEqual(group.expressions[0].number, 10)

    def test_identifier_inside_parens(self):
        result = _parse('window(position)')
        group = result.context_groups[0]
        self.assertIsInstance(group.expressions[0], StringAnum)
        self.assertEqual(group.expressions[0].text, 'position')


class TestErrors(unittest.TestCase):
    """Ошибочные входные данные."""

    def test_trailing_garbage_raises(self):
        notation = AbitNotation('new_abit_notation')
        lexer = ComplexAnumLexer('window)', notation)
        with self.assertRaises(ValueError):
            ComplexAnumParser(lexer).parse()

    def test_str_representations(self):
        # __str__ не должен падать и должен отражать структуру.
        result = _parse('window(position)(10)')
        s = str(result)
        self.assertIn('ComplexStructure', s)
        self.assertIn('window', s)


if __name__ == '__main__':
    unittest.main(verbosity=2)
