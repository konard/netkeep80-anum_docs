# -*- coding: utf-8 -*-
"""
Legacy-тесты расширенного парсера ачисел (parsers/extended_anum_parser.py).

Эти проверки сохраняют поведение старого compatibility parser до его замены
reader'ом формальной нотации МТС. Они не являются спецификацией текущей
корневой нотации.

Покрывают:
* варианты нотации абитов (AbitNotation);
* обработку UTF-8 в чистые четверичные последовательности (UTF8ByteProcessor);
* лексер ExtendedAnumLexer и его типы токенов.

Запуск:
  python3 tests/legacy/test_extended_anum_parser.py
"""

import sys
import os
import unittest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_REPO_ROOT, 'parsers'))

from extended_anum_parser import (  # noqa: E402
    AbitNotation, UTF8ByteProcessor, ExtendedAnumLexer
)


class TestAbitNotation(unittest.TestCase):
    """Варианты нотации абитов."""

    def test_default_variant(self):
        n = AbitNotation()
        self.assertEqual(n.variant_name, 'new_abit_notation')

    def test_unknown_variant_raises(self):
        with self.assertRaises(ValueError):
            AbitNotation('does_not_exist')

    def test_abit_symbols_new_notation(self):
        n = AbitNotation('new_abit_notation')
        self.assertEqual(n.get_abit_symbol('connection'), '1')
        self.assertEqual(n.get_abit_symbol('no_connection'), '0')
        self.assertEqual(n.get_abit_symbol('open_context'), '[')
        self.assertEqual(n.get_abit_symbol('close_context'), ']')

    def test_is_abit_symbol(self):
        n = AbitNotation('new_abit_notation')
        for s in ('1', '0', '[', ']'):
            self.assertTrue(n.is_abit_symbol(s))
        self.assertFalse(n.is_abit_symbol('∞'))
        self.assertFalse(n.is_abit_symbol('x'))

    def test_get_abit_type_roundtrip(self):
        n = AbitNotation('new_abit_notation')
        self.assertEqual(n.get_abit_type('1'), 'connection')
        self.assertEqual(n.get_abit_type('['), 'open_context')
        self.assertIsNone(n.get_abit_type('∞'))

    def test_infinity_representation_is_brackets(self):
        # ∞ выражается через абиты [] — это не отдельный абит.
        n = AbitNotation('new_abit_notation')
        self.assertEqual(n.get_infinity_representation(), '[]')

    def test_validate_quaternary_rejects_infinity(self):
        n = AbitNotation('new_abit_notation')
        ok, msg = n.validate_quaternary_sequence('∞')
        self.assertFalse(ok)
        self.assertIn('∞', msg)

    def test_validate_quaternary_accepts_abits(self):
        n = AbitNotation('new_abit_notation')
        ok, _ = n.validate_quaternary_sequence('1010 [ ]')
        self.assertTrue(ok)


class TestUTF8ByteProcessor(unittest.TestCase):
    """Преобразование символов в чистые четверичные последовательности."""

    def setUp(self):
        self.n = AbitNotation('new_abit_notation')

    def test_char_to_utf8_bytes_ascii(self):
        self.assertEqual(UTF8ByteProcessor.char_to_utf8_bytes('A'), b'A')

    def test_utf8_bytes_to_binary(self):
        # 'A' = 0x41 = 01000001
        self.assertEqual(UTF8ByteProcessor.utf8_bytes_to_binary(b'A'), '01000001')

    def test_char_to_anum_ascii(self):
        # 'A' (0x41) -> 01000001 в абитах connection/no_connection (1/0)
        self.assertEqual(UTF8ByteProcessor.char_to_anum('A', self.n), '01000001')

    def test_char_to_anum_only_abits(self):
        # Любой символ должен раскладываться только в абиты 1/0.
        for char in ('и', '中', '🌟'):
            anum = UTF8ByteProcessor.char_to_anum(char, self.n)
            self.assertTrue(set(anum) <= {'1', '0'}, f'{char} -> {anum}')

    def test_string_to_anum_length(self):
        parts = UTF8ByteProcessor.string_to_anum('AB', self.n)
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], '01000001')

    def test_validate_pure_quaternary_rejects_infinity(self):
        with self.assertRaises(ValueError):
            UTF8ByteProcessor.validate_pure_quaternary_output('∞')

    def test_validate_pure_quaternary_accepts_abits(self):
        self.assertTrue(UTF8ByteProcessor.validate_pure_quaternary_output('1010[]'))

    def test_infinity_notation_rejected_by_processor(self):
        # Нотация, где connection == ∞, недопустима для сериализации.
        class _BadNotation:
            def get_abit_symbol(self, t):
                return '∞'
        with self.assertRaises(ValueError):
            UTF8ByteProcessor.binary_to_anum_sequence('10', _BadNotation())


class TestExtendedAnumLexer(unittest.TestCase):
    """Лексер: типы токенов."""

    def _tokens(self, text, notation=None):
        lexer = ExtendedAnumLexer(text, notation or AbitNotation('new_abit_notation'))
        out = []
        while True:
            tok = lexer.get_next_token()
            if tok.type == 'EOF':
                break
            out.append((tok.type, tok.value))
        return out

    def test_abits_tokenized(self):
        toks = self._tokens('1 0 [ ]')
        self.assertTrue(all(t[0] == 'ABIT' for t in toks))
        self.assertEqual([t[1] for t in toks], ['1', '0', '[', ']'])

    def test_infinity_keyword(self):
        toks = self._tokens('INF')
        self.assertEqual(toks, [('INFINITY', 'INF')])

    def test_arrow_operator(self):
        toks = self._tokens('a -> b')
        self.assertIn(('ARROW', '->'), toks)

    def test_alpha_letters_are_symbols(self):
        # Буквы (в т.ч. M/F и кириллица) читаются как слова → SYMBOL.
        self.assertEqual(self._tokens('M F'), [('SYMBOL', 'M'), ('SYMBOL', 'F')])
        self.assertEqual(self._tokens('и'), [('SYMBOL', 'и')])

    def test_parentheses(self):
        toks = self._tokens('( )')
        self.assertEqual(toks, [('LPAREN', '('), ('RPAREN', ')')])

    def test_utf8_char_token(self):
        # Не-буквенный символ вне ASCII (эмодзи) → UTF8_CHAR.
        self.assertEqual(self._tokens('🌟'), [('UTF8_CHAR', '🌟')])

    def test_unknown_char_raises(self):
        lexer = ExtendedAnumLexer('@', AbitNotation('new_abit_notation'))
        with self.assertRaises(ValueError):
            lexer.get_next_token()


if __name__ == '__main__':
    unittest.main(verbosity=2)
