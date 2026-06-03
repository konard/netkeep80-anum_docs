# -*- coding: utf-8 -*-
"""
Тесты системы разграничения нотаций МТС (core/notation_system.py).

Покрывают (issue #46, пункт 5):
* legacy-подсказку типов нотаций (NotationDetector);
* резолвер ссылок на абиты (AbitReferenceResolver);
* конвертер и валидатор нотаций;
* унифицированный API MTC_NotationAPI.

Запуск:
  python3 tests/test_notation_system.py
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.notation_system import (  # noqa: E402
    NotationType, NotationDetector, AbitReferenceResolver,
    NotationConverter, NotationValidator, MTC_NotationAPI
)


class TestNotationDetector(unittest.TestCase):
    """Эвристическая подсказка типа нотации."""

    def test_quaternary(self):
        for text in ('1100', '[[]]', '10[]', '[ ] 1 0'):
            self.assertEqual(
                NotationDetector.guess_notation_type(text),
                NotationType.QUATERNARY, text
            )

    def test_formula(self):
        for text in ('♂♀ = ∞', '1 == 1', '[] == ∞', 'a -> b'):
            self.assertEqual(
                NotationDetector.guess_notation_type(text),
                NotationType.FORMULA, text
            )

    def test_string(self):
        for text in ('hello', 'abc', '"начало{[}конец"'):
            self.assertEqual(
                NotationDetector.guess_notation_type(text),
                NotationType.STRING, text
            )

    def test_empty_is_quaternary(self):
        self.assertEqual(
            NotationDetector.guess_notation_type(''),
            NotationType.QUATERNARY
        )

    def test_detect_name_is_legacy_wrapper(self):
        with self.assertWarns(DeprecationWarning):
            detected = NotationDetector.detect_notation_type('♂♀ = ∞')
        self.assertEqual(detected, NotationDetector.guess_notation_type('♂♀ = ∞'))

    def test_extract_abit_references(self):
        refs = NotationDetector.extract_abit_references('a{1}b{0}c{∞}d{[}')
        self.assertEqual(refs, ['1', '0', '∞', '['])

    def test_confidence_quaternary(self):
        self.assertEqual(
            NotationDetector.get_confidence('1100', NotationType.QUATERNARY), 1.0
        )
        self.assertEqual(
            NotationDetector.get_confidence('abc', NotationType.QUATERNARY), 0.0
        )

    def test_confidence_formula_full(self):
        # Оператор + символ → максимальная уверенность.
        self.assertEqual(
            NotationDetector.get_confidence('♂♀ = ∞', NotationType.FORMULA), 1.0
        )


class TestAbitReferenceResolver(unittest.TestCase):
    """Разрешение ссылок на абиты."""

    def test_basic_abits_are_identity(self):
        for a in ('1', '0', '[', ']'):
            self.assertEqual(AbitReferenceResolver.resolve_abit_reference(a), a)

    def test_infinity_reference_expands_to_brackets_but_is_not_abit(self):
        # ∞ выражается через [] как ссылка на акорень, но не входит в ABIT_MAP.
        self.assertNotIn('∞', AbitReferenceResolver.ABIT_MAP)
        self.assertEqual(AbitReferenceResolver.resolve_abit_reference('∞'), '[]')

    def test_unknown_reference_empty(self):
        self.assertEqual(AbitReferenceResolver.resolve_abit_reference('?'), '')

    def test_resolve_all_references(self):
        self.assertEqual(
            AbitReferenceResolver.resolve_all_references('x{1}y{∞}z'),
            'x1y[]z'
        )


class TestNotationConverter(unittest.TestCase):
    """Конвертер между нотациями."""

    def setUp(self):
        self.conv = NotationConverter()

    def test_string_refs_to_quaternary(self):
        self.assertEqual(self.conv.string_to_quaternary('{1}{0}'), '10')

    def test_quaternary_char_identity(self):
        self.assertEqual(self.conv.string_to_quaternary('10[]'), '10[]')

    def test_char_to_quaternary_wraps_brackets(self):
        # Обычный символ кодируется UTF-8 битами в [...].
        result = self.conv._char_to_quaternary('A')
        self.assertTrue(result.startswith('[') and result.endswith(']'))
        self.assertEqual(result, '[01000001]')


class TestNotationValidator(unittest.TestCase):
    """Валидатор нотаций."""

    def test_valid_quaternary(self):
        self.assertTrue(NotationValidator.validate_quaternary('1100[]').is_valid)

    def test_invalid_quaternary(self):
        self.assertFalse(NotationValidator.validate_quaternary('1102').is_valid)

    def test_empty_quaternary_valid(self):
        self.assertTrue(NotationValidator.validate_quaternary('').is_valid)

    def test_formula_requires_operators_or_symbols(self):
        self.assertTrue(NotationValidator.validate_formula('♂♀ = ∞').is_valid)
        self.assertFalse(NotationValidator.validate_formula('plain text').is_valid)

    def test_string_anum_valid_references(self):
        # Распознаются только ссылки {1},{0},{[},{]},{∞}; они всегда валидны.
        self.assertTrue(NotationValidator.validate_string_anum('a{1}b{∞}c').is_valid)

    def test_string_anum_unrecognized_braces_ignored(self):
        # {x} не соответствует паттерну ссылок, поэтому не считается ошибкой.
        self.assertTrue(NotationValidator.validate_string_anum('a{x}b').is_valid)


class TestMTC_NotationAPI(unittest.TestCase):
    """Унифицированный API."""

    def setUp(self):
        self.api = MTC_NotationAPI()

    def test_parse_autodetect(self):
        parsed = self.api.parse('1100')
        self.assertEqual(parsed.notation_type, NotationType.QUATERNARY)
        self.assertEqual(parsed.confidence, 1.0)

    def test_parse_explicit_type(self):
        parsed = self.api.parse('hello', NotationType.STRING)
        self.assertEqual(parsed.notation_type, NotationType.STRING)

    def test_convert_same_type_identity(self):
        self.assertEqual(
            self.api.convert('1100', NotationType.QUATERNARY, NotationType.QUATERNARY),
            '1100'
        )

    def test_convert_string_to_quaternary(self):
        self.assertEqual(
            self.api.convert('{1}{0}', NotationType.STRING, NotationType.QUATERNARY),
            '10'
        )

    def test_validate_matches_type(self):
        self.assertTrue(self.api.validate('1100', NotationType.QUATERNARY).is_valid)
        self.assertFalse(self.api.validate('1102', NotationType.QUATERNARY).is_valid)

    def test_analyze_returns_full_report(self):
        report = self.api.analyze('♂♀ = ∞')
        self.assertEqual(report['detected_type'], 'formula')
        self.assertTrue(report['is_valid'])
        self.assertIn('confidence', report)


if __name__ == '__main__':
    unittest.main(verbosity=2)
