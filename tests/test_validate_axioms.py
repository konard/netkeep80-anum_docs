# -*- coding: utf-8 -*-
"""
Тесты валидатора аксиом МТС (core/axioms/validate_axioms.py).

Главная цель — проверить, что валидатор РЕАЛЬНО вычисляет результаты
доказателем и структурными проверками, а не хардкодит ``True``
(регрессия issue #46, пункт 2).

Запуск:
  python3 tests/test_validate_axioms.py
"""

import sys
import os
import unittest

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.axioms.validate_axioms import MTCAxiomValidator, ABITS, ABIT_INVERSE


class TestProverBackedChecks(unittest.TestCase):
    """prove()/refute() обёрнуты вокруг настоящего доказателя."""

    def setUp(self):
        self.v = MTCAxiomValidator()

    def test_prove_true_equivalences(self):
        # Ключевые теоремы МТС должны доказываться.
        self.assertTrue(self.v.prove('♂♀ = ∞'))
        self.assertTrue(self.v.prove('∞ = ∞→∞'))
        self.assertTrue(self.v.prove('♂∞♀ = (♂∞)♀'))
        self.assertTrue(self.v.prove('a = a'))

    def test_prove_rejects_false_equivalences(self):
        # Ложные равенства НЕ должны доказываться — иначе валидатор хардкодит.
        self.assertFalse(self.v.prove('a = b'))
        self.assertFalse(self.v.prove('a→b = b→a'))
        self.assertFalse(self.v.prove('♂v = ♂w'))

    def test_refute_is_negation_of_prove(self):
        self.assertTrue(self.v.refute('a = b'))
        self.assertTrue(self.v.refute('a→b = b→a'))
        self.assertFalse(self.v.refute('a = a'))

    def test_prove_never_raises(self):
        # Любой мусор должен возвращать булев результат, а не исключение.
        for junk in ('', '???', '♂♂♂', '() ) (', 'a->'):
            self.assertIsInstance(self.v.prove(junk), bool)


class TestAbitStructuralChecks(unittest.TestCase):
    """Структурные проверки нотации абитов."""

    def setUp(self):
        self.v = MTCAxiomValidator()

    def test_abit_set(self):
        self.assertEqual(set(ABITS), {'[', ']', '1', '0'})
        self.assertEqual(len(set(ABITS)), 4)

    def test_abit_inverse_is_involution(self):
        for a in ABITS:
            self.assertEqual(ABIT_INVERSE[ABIT_INVERSE[a]], a)
            self.assertNotEqual(ABIT_INVERSE[a], a)

    def test_valid_sequences(self):
        for seq in ('[', ']', '1', '0', '[ ] 1 0', '1110', '[1]0'):
            ok, _ = self.v.validate_abit_sequence(seq)
            self.assertTrue(ok, f'{seq} должна быть валидной')

    def test_infinity_is_not_an_abit(self):
        self.assertNotIn('∞', ABITS)
        ok, msg = self.v.validate_abit_sequence('∞')
        self.assertFalse(ok)
        self.assertIn('∞', msg)

    def test_sequence_with_infinity_rejected(self):
        ok, _ = self.v.validate_abit_sequence('[∞]')
        self.assertFalse(ok)


class TestRunAllTests(unittest.TestCase):
    """Полный прогон валидации проходит и считается честно."""

    def test_run_all_tests_passes(self):
        v = MTCAxiomValidator()
        self.assertTrue(v.run_all_tests())

    def test_counts_are_consistent(self):
        v = MTCAxiomValidator()
        v.run_all_tests()
        # Все детальные тесты должны быть пройдены...
        self.assertEqual(v.passed_tests, v.total_tests)
        # ...и их должно быть много (это не один захардкоженный вызов).
        self.assertGreaterEqual(v.total_tests, 50)


class TestNotHardcoded(unittest.TestCase):
    """Доказываем, что результаты НЕ хардкодятся: подмена доказателя ломает прогон."""

    def test_broken_prover_breaks_validation(self):
        v = MTCAxiomValidator()

        class _AlwaysFalseProver(object):
            def parse_and_prove(self, formula):
                return False

        # Если бы результаты были захардкожены True, прогон всё равно прошёл бы.
        v.prover = _AlwaysFalseProver()
        self.assertFalse(
            v.run_all_tests(),
            'При сломанном доказателе валидация обязана провалиться'
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
