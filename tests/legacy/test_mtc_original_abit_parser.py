# -*- coding: utf-8 -*-
"""
Legacy-тесты парсера оригинальной нотации абитов МТС
(parsers/mtc_original_abit_parser.py).

Историческая оригинальная нотация оставлена только как compatibility layer.
Эти тесты не нормируют текущую квадратную нотацию МТС, где абиты — только
`[`, `]`, `1`, `0`, а `∞` не является абитом.

Покрывают:
* нотацию MTCAbitNotation (♂, ♀, →, ∞ и контекстные разделители);
* контекстное разрешение запятых (ContextualCommaResolver);
* лексер MTCOriginalLexer.

Запуск:
  python3 tests/legacy/test_mtc_original_abit_parser.py
"""

import sys
import os
import unittest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_REPO_ROOT, 'parsers'))

from mtc_original_abit_parser import (  # noqa: E402
    MTCAbitNotation, ContextualCommaResolver, MTCOriginalLexer
)


class TestMTCAbitNotation(unittest.TestCase):
    """Историческая оригинальная нотация абитов."""

    def setUp(self):
        self.n = MTCAbitNotation()

    def test_abit_symbols(self):
        self.assertTrue(self.n.is_abit('♂'))
        self.assertTrue(self.n.is_abit('♀'))
        self.assertTrue(self.n.is_abit('→'))
        self.assertTrue(self.n.is_abit('∞'))

    def test_non_abit(self):
        self.assertFalse(self.n.is_abit('x'))
        self.assertFalse(self.n.is_abit('⟨'))

    def test_abit_types(self):
        self.assertEqual(self.n.get_abit_type('♂'), 'reference_start')
        self.assertEqual(self.n.get_abit_type('♀'), 'value_end')
        self.assertEqual(self.n.get_abit_type('→'), 'connection')
        self.assertEqual(self.n.get_abit_type('∞'), 'infinity')
        self.assertIsNone(self.n.get_abit_type('x'))

    def test_context_separators(self):
        self.assertTrue(self.n.is_context_separator('⟨'))
        self.assertTrue(self.n.is_context_separator('⟩'))
        self.assertEqual(self.n.get_separator_type('⟨'), 'group_start')
        self.assertIsNone(self.n.get_separator_type('x'))


class TestContextualCommaResolver(unittest.TestCase):
    """Разрешение контекста запятых (несвязь vs разделитель)."""

    def setUp(self):
        self.resolver = ContextualCommaResolver(MTCAbitNotation())

    def test_comma_between_abits_is_abit(self):
        # Запятая между абитами трактуется как абит несвязи.
        tokens = self.resolver.resolve_comma_context('♂,♀')
        kinds = [t[0] for t in tokens]
        self.assertIn('ABIT', kinds)
        # Должен присутствовать токен несвязи.
        self.assertTrue(any(t[0] == 'ABIT' and t[1] == ',' for t in tokens))

    def test_comma_between_words_is_separator(self):
        # Запятая между обычными словами — разделитель списка.
        tokens = self.resolver.resolve_comma_context('foo, bar')
        self.assertTrue(any(t[0] == 'SEPARATOR' for t in tokens))

    def test_escaped_comma_is_abit(self):
        tokens = self.resolver.resolve_comma_context('⦃,⦄')
        self.assertEqual(tokens, [('ABIT', ',', 'no_connection')])

    def test_context_separators_detected(self):
        tokens = self.resolver.resolve_comma_context('⟨♂⟩')
        kinds = [t[0] for t in tokens]
        self.assertEqual(kinds[0], 'CONTEXT_SEP')
        self.assertEqual(kinds[-1], 'CONTEXT_SEP')


class TestMTCOriginalLexer(unittest.TestCase):
    """Лексер оригинальной нотации."""

    def _tokens(self, text):
        lexer = MTCOriginalLexer(text)
        out = []
        while True:
            tok = lexer.get_next_token()
            if tok.type == 'EOF':
                break
            out.append((tok.type, tok.value))
        return out

    def test_connection_form(self):
        # ∞♀ → ♂∞ — единица смысла (связь).
        toks = self._tokens('∞♀ → ♂∞')
        types = [t[0] for t in toks]
        self.assertTrue(all(t == 'ABIT' for t in types))
        self.assertEqual([t[1] for t in toks], ['∞', '♀', '→', '♂', '∞'])

    def test_identifier_token(self):
        toks = self._tokens('window')
        self.assertEqual(toks, [('SYMBOL', 'window')])

    def test_infinity_keyword(self):
        toks = self._tokens('INF')
        self.assertEqual(toks, [('INFINITY', 'INF')])

    def test_number_token(self):
        toks = self._tokens('123')
        self.assertEqual(toks, [('NUMBER', '123')])

    def test_equals_and_parens(self):
        toks = self._tokens('(a) = b')
        self.assertIn(('LPAREN', '('), toks)
        self.assertIn(('RPAREN', ')'), toks)
        self.assertIn(('EQUALS', '='), toks)

    def test_empty_input(self):
        toks = self._tokens('')
        self.assertEqual(toks, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
